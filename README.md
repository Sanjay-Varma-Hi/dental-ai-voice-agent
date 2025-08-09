# Dental AI Voice Agent

A Twilio + Whisper + GPT-based AI voice agent for dental clinics. This project is built with FastAPI and MongoDB Atlas.

## Phase 1: Foundation Setup

This phase establishes the core backend infrastructure with:
- FastAPI backend framework
- MongoDB Atlas integration
- Patient data management
- API endpoints for call triggering

## Phase 2: Twilio Voice Integration

This phase adds voice calling capabilities with:
- Twilio Programmable Voice integration
- Outbound call initiation
- TwiML voice responses
- Call logging and tracking
- Webhook handling for call events

## Project Structure

```
dental-ai-agent/
├── main.py                    # FastAPI application with Twilio integration
├── requirements-minimal.txt   # Python dependencies (Python 3.13 compatible)
├── requirements-stable.txt    # Stable dependencies (fallback)
├── env.example               # Environment variables template
├── README.md                # This file
├── .gitignore               # Git ignore rules
├── setup_sample_data.py     # Sample data population
├── test_api.py              # API testing script
├── test_twilio.py           # Twilio integration testing
├── quick_start.py           # Automated setup script
└── install_deps.py          # Specialized dependency installer
```

## Setup Instructions

### 1. Clone and Navigate to Project
```bash
cd dental-ai-agent
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**If you encounter build errors (especially with Python 3.13+), try:**
```bash
pip install -r requirements-stable.txt
```

### 4. Environment Configuration
1. Copy the environment template:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` file with your credentials:
   ```
   # MongoDB Atlas
   MONGODB_URI=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/dental_clinic?retryWrites=true&w=majority
   
   # Twilio (Get from https://console.twilio.com/)
   TWILIO_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_PHONE_NUMBER=+1234567890
   ```

### 5. MongoDB Atlas Setup
1. Create a MongoDB Atlas account at [mongodb.com](https://mongodb.com)
2. Create a new cluster
3. Create a database named `dental_clinic`
4. Create a collection named `patients`
5. Add sample patient data:

```json
{
  "name": "John Doe",
  "phone_number": "+1234567890",
  "pincode": "12345",
  "email": "john@example.com",
  "last_visit": "2024-01-15"
}
```

### 6. Run the Application
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## API Endpoints

### Health Check
- **GET** `/health`
- Returns application and database status

### Root
- **GET** `/`
- Returns basic application info

### Trigger Call
- **POST** `/api/trigger-call`
- **Request Body:**
  ```json
  {
    "pincode": "12345"
  }
  ```
- **Response:**
  ```json
  {
    "patients": [
      {
        "name": "John Doe",
        "phone_number": "+1234567890"
      }
    ],
    "total_count": 1
  }
  ```

### Call Patients (Phase 2)
- **POST** `/api/call-patients`
- **Request Body:**
  ```json
  {
    "pincode": "12345"
  }
  ```
  OR
  ```json
  {
    "phone_numbers": ["+1234567890", "+1234567891"]
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "message": "Initiated 3 calls",
    "calls_initiated": 3,
    "failed_numbers": []
  }
  ```

### Call Logs (Phase 2)
- **GET** `/api/call-logs`
- **Response:**
  ```json
  [
    {
      "call_sid": "CA1234567890",
      "phone_number": "+1234567890",
      "status": "completed",
      "timestamp": "2024-01-15T10:30:00",
      "message": "Call initiated successfully"
    }
  ]
  ```

## API Documentation

Once the server is running, you can access:
- **Interactive API Docs (Swagger UI):** `http://localhost:8000/docs`
- **Alternative API Docs (ReDoc):** `http://localhost:8000/redoc`

## Testing the API

### Using curl
```bash
# Health check
curl http://localhost:8000/health

# Trigger call for pincode 12345
curl -X POST http://localhost:8000/api/trigger-call \
  -H "Content-Type: application/json" \
  -d '{"pincode": "12345"}'
```

### Using the Swagger UI
1. Open `http://localhost:8000/docs` in your browser
2. Click on the `/api/trigger-call` endpoint
3. Click "Try it out"
4. Enter the pincode in the request body
5. Click "Execute"

## Development

### Adding New Endpoints
1. Add your endpoint function in `main.py`
2. Use FastAPI decorators (`@app.get()`, `@app.post()`, etc.)
3. Define Pydantic models for request/response validation

### Database Operations
- Use `db.patients` for patient collection operations
- All database operations are async
- Use Motor's async methods for MongoDB operations

## Next Phases

- **Phase 2:** ✅ Twilio integration for voice calls (COMPLETED)
- **Phase 3:** ✅ AI Voice Intelligence with OpenAI Whisper, GPT-4o, and Azure TTS (COMPLETED)
- **Phase 4:** Advanced call flow management and scheduling
- **Phase 5:** Multi-language support and analytics

## 🧠 Phase 3: AI Voice Intelligence

### Features Added:
- ✅ **OpenAI Whisper Integration**: Speech-to-text transcription
- ✅ **GPT-4o Integration**: AI response generation
- ✅ **Azure TTS Integration**: Text-to-speech conversion
- ✅ **Voice Interaction Pipeline**: Complete AI voice loop
- ✅ **Audio File Management**: Serve generated audio files
- ✅ **Interaction Logging**: Full conversation history in MongoDB

### New API Endpoints:
- `GET /api/voice-interactions` - View AI conversation history
- `GET /audio/{filename}` - Serve generated audio files
- `POST /api/twilio-voice` - Enhanced with AI voice intelligence

### Setup Instructions:
1. **Get OpenAI API Key**:
   - Sign up at [OpenAI Platform](https://platform.openai.com/)
   - Get your API key

2. **Get Azure Speech Service**:
   - Sign up at [Azure Portal](https://portal.azure.com/)
   - Create a Speech Service resource
   - Get your key and region

3. **Update Environment Variables**:
   ```bash
   # Add to your .env file
   OPENAI_API_KEY=your_openai_api_key_here
   AZURE_TTS_KEY=your_azure_tts_key_here
   AZURE_TTS_REGION=your_azure_region_here
   ```

4. **Install Dependencies**:
   ```bash
   pip install openai azure-cognitiveservices-speech aiofiles
   ```

### How It Works:
1. **Call Initiation**: Twilio calls the patient
2. **Voice Recording**: Patient speaks after the greeting
3. **Audio Processing**: Download and transcribe with Whisper
4. **AI Response**: GPT-4o generates contextual response
5. **TTS Conversion**: Azure TTS converts response to speech
6. **Audio Playback**: Twilio plays the AI response
7. **Logging**: Full interaction saved to MongoDB

### Testing:
- Use `test_phase3.py` to verify AI voice intelligence
- Check voice interactions at `/api/voice-interactions`
- Monitor AI processing in server logs

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Verify your connection string in `.env`
   - Ensure your IP is whitelisted in MongoDB Atlas
   - Check network connectivity

2. **Port Already in Use**
   - Change the port in `main.py` or use a different port with uvicorn
   - Kill existing processes using the port

3. **Missing Dependencies**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt` again

4. **Python 3.13+ Build Errors**
   - The error you encountered is common with Python 3.13+ and newer package versions
   - Try using the stable requirements: `pip install -r requirements-stable.txt`
   - Or downgrade to Python 3.11 or 3.12 for better compatibility
   - Alternative: Use `pip install --no-build-isolation pydantic` before installing other packages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
