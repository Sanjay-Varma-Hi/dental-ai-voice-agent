from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import JSONResponse, FileResponse, Response
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
from datetime import datetime
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import re

# Handle both Pydantic v1 and v2
try:
    from pydantic import BaseModel
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseModel

# Load environment variables early so downstream imports see them
load_dotenv()

from ai_voice import ai_agent

app = FastAPI(title="Dental AI Voice Agent", version="1.0.0")

# MongoDB connection
client = None
db = None

# Twilio client
twilio_client = None

# ---------------- Intent Detection ---------------- #
POSITIVE_PAT = re.compile(r"\b(yes|yeah|yep|sure|okay|ok|interested|book|sounds good)\b", re.I)
NEGATIVE_PAT = re.compile(r"\b(no|nah|not interested|stop|don't|do not|decline)\b", re.I)
DAY_PAT = re.compile(r"\b(mon|tue|wed|thu|fri|sat|sun|today|tomorrow)\b", re.I)
DATE_PAT = re.compile(r"\b(\d{1,2}(st|nd|rd|th)?\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)?|\d{4}-\d{2}-\d{2})\b", re.I)
TIME_PAT = re.compile(r"\b(\d{1,2}(:\d{2})?\s*(am|pm)?)\b", re.I)

async def detect_intent(user_text: str) -> str:
    if NEGATIVE_PAT.search(user_text or ""):
        return "negative"
    if DAY_PAT.search(user_text or "") or DATE_PAT.search(user_text or ""):
        if TIME_PAT.search(user_text or ""):
            return "scheduling"
    if POSITIVE_PAT.search(user_text or ""):
        return "positive"
    return "fallback"

# --------------- App lifecycle -------------------- #
@app.on_event("startup")
async def startup_db_client():
    global client, db, twilio_client
    
    # Setup MongoDB
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        raise ValueError("MONGODB_URI environment variable is required")
    
    client = AsyncIOMotorClient(mongodb_uri)
    db = client.dental_clinic
    
    # Setup Twilio
    twilio_sid = os.getenv("TWILIO_SID")
    twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    if twilio_sid and twilio_auth_token:
        twilio_client = Client(twilio_sid, twilio_auth_token)
        print("✅ Twilio client initialized")
    else:
        print("⚠️  Twilio credentials not found. Voice calls will be disabled.")

@app.on_event("shutdown")
async def shutdown_db_client():
    if client:
        client.close()

# ---------------- Models -------------------------- #
class TriggerCallRequest(BaseModel):
    pincode: str

class PatientInfo(BaseModel):
    name: str
    phone_number: str

class TriggerCallResponse(BaseModel):
    patients: List[PatientInfo]
    total_count: int

class CallPatientsRequest(BaseModel):
    phone_numbers: List[str] = []
    pincode: str = None

class CallPatientsResponse(BaseModel):
    success: bool
    message: str
    calls_initiated: int
    failed_numbers: List[str] = []

class CallLog(BaseModel):
    call_sid: str
    phone_number: str
    status: str
    timestamp: datetime
    message: str

class VoiceInteraction(BaseModel):
    call_sid: str
    transcript: str
    ai_response: str
    tts_path: Optional[str] = None
    timestamp: datetime

# ---------------- Helpers ------------------------- #
async def upsert_conversation(call_sid: str, update: Dict):
    await db.conversations.update_one(
        {"call_sid": call_sid},
        {"$set": update, "$setOnInsert": {"created_at": datetime.now()}},
        upsert=True,
    )

async def append_turn(call_sid: str, role: str, text: str):
    await db.conversations.update_one(
        {"call_sid": call_sid},
        {"$push": {"turns": {"role": role, "text": text, "ts": datetime.now()}}},
        upsert=True,
    )

# ---------------- Routes -------------------------- #
@app.get("/")
async def root():
    return {"message": "Dental AI Voice Agent API", "status": "running"}

@app.post("/api/trigger-call", response_model=TriggerCallResponse)
async def trigger_call(request: TriggerCallRequest):
    """
    Trigger a call by pincode - returns all patients in the specified pincode
    """
    try:
        # Query MongoDB for patients in the specified pincode
        patients_collection = db.patients
        cursor = patients_collection.find({"pincode": request.pincode})
        
        patients = []
        async for patient in cursor:
            patients.append(PatientInfo(
                name=patient.get("name", ""),
                phone_number=patient.get("phone_number", "")
            ))
        
        return TriggerCallResponse(
            patients=patients,
            total_count=len(patients)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "database": "connected" if client else "disconnected", "twilio": "connected" if twilio_client else "disconnected"}

@app.get("/api/patients", response_model=List[dict])
async def get_all_patients():
    """
    Get all patients from the database
    """
    try:
        patients_collection = db.patients
        cursor = patients_collection.find({})
        
        patients = []
        async for patient in cursor:
            # Convert ObjectId to string for JSON serialization
            patient["_id"] = str(patient["_id"])
            patients.append(patient)
        
        return patients
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/api/call-patients", response_model=CallPatientsResponse)
async def call_patients(request: CallPatientsRequest):
    """
    Initiate outbound calls to patients
    """
    if not twilio_client:
        raise HTTPException(status_code=500, detail="Twilio not configured")
    
    try:
        phone_numbers = request.phone_numbers
        
        # If no phone numbers provided but pincode is, fetch from database
        if not phone_numbers and request.pincode:
            patients_collection = db.patients
            cursor = patients_collection.find({"pincode": request.pincode})
            
            phone_numbers = []
            async for patient in cursor:
                phone_numbers.append(patient.get("phone_number"))
        
        if not phone_numbers:
            return CallPatientsResponse(
                success=False,
                message="No phone numbers provided or found",
                calls_initiated=0
            )
        
        twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
        if not twilio_phone:
            raise HTTPException(status_code=500, detail="Twilio phone number not configured")
        
        calls_initiated = 0
        failed_numbers = []
        
        for phone_number in phone_numbers:
            try:
                # Create call using Twilio
                webhook_url = os.getenv('HOST', 'http://localhost:8000')
                print(f"🔗 Using webhook URL: {webhook_url}")
                
                call = twilio_client.calls.create(
                    to=phone_number,
                    from_=twilio_phone,
                    url=f"{webhook_url}/api/twilio-voice",
                    method='POST'
                )
                
                # Log the call attempt
                call_log = {
                    "call_sid": call.sid,
                    "phone_number": phone_number,
                    "status": "initiated",
                    "timestamp": datetime.now(),
                    "message": "Call initiated successfully"
                }
                
                await db.call_logs.insert_one(call_log)
                calls_initiated += 1
                
            except Exception as e:
                failed_numbers.append(phone_number)
                print(f"Failed to call {phone_number}: {str(e)}")
                # Log the detailed error for debugging
                error_details = {
                    "phone_number": phone_number,
                    "error": str(e),
                    "timestamp": datetime.now()
                }
                await db.call_errors.insert_one(error_details)
        
        return CallPatientsResponse(
            success=True,
            message=f"Initiated {calls_initiated} calls",
            calls_initiated=calls_initiated,
            failed_numbers=failed_numbers
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Call initiation error: {str(e)}")

@app.post("/api/twilio-voice")
async def twilio_voice_webhook(request: Request):
    """
    Conversational webhook: greet → record → transcribe → intent → reply → repeat or end
    """
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid", "")
        recording_url = form_data.get("RecordingUrl", "")
        caller = form_data.get("From", "")

        vr = VoiceResponse()

        if not call_sid:
            xml = vr.say("Sorry, missing call information.").to_xml()
            return Response(content=xml, media_type="application/xml")

        # Initial greeting (no recording yet)
        if not recording_url:
            greeting = "Hello! This is your dental clinic. Are you available to schedule an appointment?"
            await upsert_conversation(call_sid, {
                "call_sid": call_sid,
                "status": "ongoing",
                "last_intent": None,
                "last_message": greeting,
                "caller": caller,
            })
            await append_turn(call_sid, "agent", greeting)

            vr.say(greeting, voice='alice', language='en-US')
            vr.record(
                action=f"{os.getenv('HOST', 'http://localhost:8000')}/api/twilio-voice",
                method='POST', maxLength=30, playBeep=True, trim='trim-silence'
            )
            xml = vr.to_xml()
            return Response(content=xml, media_type="application/xml")

        # We have a recording → download, transcribe, detect intent
        # Download via ai_agent (uses Twilio auth)
        audio_path = await ai_agent.download_audio(recording_url, f"{call_sid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")
        transcript = await ai_agent.transcribe_audio(audio_path)
        await append_turn(call_sid, "patient", transcript)

        intent = await detect_intent(transcript)
        next_response = ""
        end_call = False

        if intent == "negative":
            next_response = "No problem. Thank you for your time. Goodbye."
            end_call = True
        elif intent == "scheduling":
            next_response = f"Great, I heard: {transcript}. I will note that and send a confirmation shortly. Goodbye."
            end_call = True
        elif intent == "positive":
            next_response = "Great! What date and time works best for you?"
        else:  # fallback
            next_response = "Sorry, I didn't catch that. Could you please say the preferred date and time?"

        # Optionally have the LLM refine the response
        try:
            refined = await ai_agent.generate_response(transcript)
            if refined:
                next_response = refined
        except Exception:
            pass

        await upsert_conversation(call_sid, {
            "status": "completed" if end_call else "ongoing",
            "last_intent": intent,
            "last_message": next_response,
            "updated_at": datetime.now(),
        })
        await append_turn(call_sid, "agent", next_response)

        # Speak response (Azure TTS path or fallback <Say>)
        tts_path = await ai_agent.text_to_speech(next_response, f"resp_{call_sid}_{datetime.now().strftime('%H%M%S')}.wav")
        if tts_path and os.path.exists(tts_path):
            vr.play(f"{os.getenv('HOST', 'http://localhost:8000')}/audio/{os.path.basename(tts_path)}")
        else:
            vr.say(next_response, voice='alice', language='en-US')

        if end_call:
            vr.hangup()
        else:
            vr.record(
                action=f"{os.getenv('HOST', 'http://localhost:8000')}/api/twilio-voice",
                method='POST', maxLength=30, playBeep=True, trim='trim-silence'
            )

        xml = vr.to_xml()
        return Response(content=xml, media_type="application/xml")

    except Exception as e:
        print(f"Error in Twilio webhook: {str(e)}")
        vr = VoiceResponse()
        vr.say("Sorry, there was an error with this call. Goodbye.")
        xml = vr.to_xml()
        return Response(content=xml, media_type="application/xml")

@app.post("/api/twilio-voice-response")
async def twilio_voice_response(request: Request):
    """
    Handle user input from the voice call
    """
    try:
        form_data = await request.form()
        digits = form_data.get("Digits", "")
        call_sid = form_data.get("CallSid", "")
        
        print(f"📞 User pressed: {digits}")
        
        vr = VoiceResponse()
        vr.say(
            f"You pressed {digits}. Thank you for confirming. We will call you back soon. Goodbye!",
            voice='alice',
            language='en-US'
        )
        
        # Log the user interaction
        if call_sid:
            await db.call_logs.update_one(
                {"call_sid": call_sid},
                {"$set": {"status": "user_interacted", "user_input": digits, "timestamp": datetime.now()}}
            )
        
        xml = vr.to_xml()
        return Response(content=xml, media_type="application/xml")
    
    except Exception as e:
        print(f"Error in voice response: {str(e)}")
        vr = VoiceResponse()
        vr.say("Thank you for your time. Goodbye.")
        xml = vr.to_xml()
        return Response(content=xml, media_type="application/xml")

@app.get("/api/call-logs", response_model=List[dict])
async def get_call_logs():
    """
    Get call logs from the database
    """
    try:
        call_logs_collection = db.call_logs
        cursor = call_logs_collection.find({}).sort("timestamp", -1)
        
        logs = []
        async for log in cursor:
            log["_id"] = str(log["_id"])
            logs.append(log)
        
        return logs
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/voice-interactions", response_model=List[dict])
async def get_voice_interactions():
    """
    Get all voice interactions from MongoDB
    """
    try:
        interactions = []
        async for interaction in db.voice_interactions.find().sort("timestamp", -1):
            # Convert ObjectId to string for JSON serialization
            interaction["_id"] = str(interaction["_id"])
            interactions.append(interaction)
        return interactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching voice interactions: {str(e)}")

@app.get("/api/conversations", response_model=List[dict])
async def list_conversations():
    try:
        out = []
        async for c in db.conversations.find().sort("created_at", -1):
            c["_id"] = str(c["_id"])
            out.append(c)
        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio/{filename}")
async def serve_audio(filename: str):
    """
    Serve audio files from the public/audio directory
    """
    try:
        file_path = f"public/audio/{filename}"
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type="audio/wav")
        else:
            raise HTTPException(status_code=404, detail="Audio file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving audio: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
