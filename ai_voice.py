import os
import asyncio
import aiofiles
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from typing import Optional

# Optional OpenAI client (used for DeepSeek too via base_url)
from openai import OpenAI

try:
    from faster_whisper import WhisperModel
    HAS_FASTER_WHISPER = True
except Exception:
    HAS_FASTER_WHISPER = False

from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, AudioConfig
from azure.cognitiveservices.speech.audio import AudioOutputConfig

class AIVoiceAgent:
    def __init__(self):
        # Provider toggles
        self.stt_provider = os.getenv('STT_PROVIDER', 'faster_whisper').lower()
        self.llm_provider = os.getenv('LLM_PROVIDER', 'deepseek').lower()

        # API keys
        self.openai_api_key = (os.getenv('OPENAI_API_KEY') or '').strip()
        self.deepseek_api_key = (os.getenv('DEEPSEEK_API_KEY') or '').strip()

        # Initialize LLM client (DeepSeek via OpenAI SDK-compatible endpoint)
        self.llm_client = None
        if self.llm_provider == 'deepseek' and self.deepseek_api_key:
            self.llm_client = OpenAI(api_key=self.deepseek_api_key, base_url="https://api.deepseek.com")
        elif self.openai_api_key:
            self.llm_client = OpenAI(api_key=self.openai_api_key)

        # Initialize local Faster-Whisper model lazily
        self.whisper_model: Optional[WhisperModel] = None
        if self.stt_provider == 'faster_whisper' and HAS_FASTER_WHISPER:
            try:
                # small or medium balance speed/quality; change as needed
                self.whisper_model = WhisperModel("small", device="cpu", compute_type="int8")
            except Exception:
                self.whisper_model = None

        # Azure TTS
        self.azure_speech_key = os.getenv('AZURE_TTS_KEY')
        self.azure_region = os.getenv('AZURE_TTS_REGION')

        # Twilio creds for recording download
        self.twilio_sid = (os.getenv('TWILIO_SID') or '').strip()
        self.twilio_auth_token = (os.getenv('TWILIO_AUTH_TOKEN') or '').strip()

        os.makedirs('public/audio', exist_ok=True)
    
    async def download_audio(self, audio_url: str, filename: str) -> str:
        try:
            use_twilio_auth = 'api.twilio.com' in audio_url and self.twilio_sid and self.twilio_auth_token
            filepath = f"public/audio/{filename}"

            candidates = []
            if 'api.twilio.com' in audio_url:
                candidates = [
                    f"{audio_url}.wav",
                    f"{audio_url}.mp3",
                    f"{audio_url}?Download=true",
                ]
            else:
                candidates = [audio_url]

            last_error: Optional[Exception] = None
            with requests.Session() as session:
                if use_twilio_auth:
                    session.auth = HTTPBasicAuth(self.twilio_sid, self.twilio_auth_token)
                headers = {"Accept": "audio/wav, audio/mpeg, */*"}
                for cand in candidates:
                    try:
                        resp = session.get(cand, headers=headers, timeout=25, allow_redirects=True)
                        resp.raise_for_status()
                        async with aiofiles.open(filepath, 'wb') as f:
                            await f.write(resp.content)
                        return filepath
                    except Exception as e:
                        last_error = e
                        continue
            raise last_error if last_error else RuntimeError('Failed to download audio')
        except Exception as e:
            print(f"❌ Error downloading audio: {str(e)}")
            raise

    async def transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio using Faster-Whisper or OpenAI Whisper fallback"""
        try:
            if self.stt_provider == 'faster_whisper' and self.whisper_model is not None:
                # Local transcription
                segments, info = self.whisper_model.transcribe(audio_file_path, language="en")
                transcript = " ".join([seg.text.strip() for seg in segments]).strip()
                print(f"🎤 FW Transcribed: {transcript}")
                return transcript
            # Fallback to OpenAI Whisper if configured
            if self.openai_api_key:
                client = OpenAI(api_key=self.openai_api_key)
                with open(audio_file_path, 'rb') as audio_file:
                    result = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text"
                    )
                print(f"🎤 OpenAI Transcribed: {result}")
                return result
            raise RuntimeError("No STT provider available. Set STT_PROVIDER=faster_whisper or provide OPENAI_API_KEY.")
        except Exception as e:
            print(f"❌ Error transcribing audio: {str(e)}")
            raise

    async def generate_response(self, transcript: str) -> str:
        try:
            if not self.llm_client:
                return "Thanks! I noted your response."
            prompt = (
                "You are a friendly dental assistant calling to book appointments. "
                f"The patient said: '{transcript}'. "
                "Respond naturally under 50 words. If they want to book, ask for preferred date and time."
            )
            response = self.llm_client.chat.completions.create(
                model="deepseek-chat" if self.llm_provider == 'deepseek' else "gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a professional dental assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            ai_response = response.choices[0].message.content.strip()
            print(f"🤖 AI Response: {ai_response}")
            return ai_response
        except Exception as e:
            print(f"❌ Error generating AI response: {str(e)}")
            return "I'm sorry, I didn't catch that. Could you please repeat?"

    async def text_to_speech(self, text: str, filename: str) -> str:
        try:
            if not self.azure_speech_key or not self.azure_region:
                return await self._fallback_tts(text, filename)
            speech_config = SpeechConfig(subscription=self.azure_speech_key, region=self.azure_region)
            speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
            audio_file_path = f"public/audio/{filename}"
            audio_config = AudioOutputConfig(filename=audio_file_path)
            synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
            result = synthesizer.speak_text_async(text).get()
            if result.reason == 0:
                return audio_file_path
            return await self._fallback_tts(text, filename)
        except Exception:
            return await self._fallback_tts(text, filename)

    async def _fallback_tts(self, text: str, filename: str) -> str:
        return text

    async def process_voice_interaction(self, audio_url: str, call_sid: str) -> dict:
        try:
            audio_filename = f"{call_sid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            audio_path = await self.download_audio(audio_url, audio_filename)
            transcript = await self.transcribe_audio(audio_path)
            ai_response = await self.generate_response(transcript)
            tts_filename = f"response_{call_sid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            tts_path = await self.text_to_speech(ai_response, tts_filename)
            return {
                "transcript": transcript,
                "ai_response": ai_response,
                "tts_path": tts_path,
                "timestamp": datetime.now()
            }
        except Exception as e:
            print(f"❌ Error in voice interaction: {str(e)}")
            return {
                "transcript": "Error processing audio",
                "ai_response": "I'm sorry, I couldn't understand. Could you please repeat?",
                "tts_path": None,
                "timestamp": datetime.now()
            }

ai_agent = AIVoiceAgent()
