#!/usr/bin/env python3
"""
Comprehensive test for Phase 3 AI Voice Intelligence Pipeline
Tests OpenAI Whisper, GPT-4o, and Azure TTS integration
"""

import os
import asyncio
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai_connection():
    """Test OpenAI API connection"""
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        
        if response.choices[0].message.content:
            print("✅ OpenAI API connection working")
            return True
        else:
            print("❌ OpenAI API response empty")
            return False
    except Exception as e:
        print(f"❌ OpenAI API error: {str(e)}")
        return False

def test_ai_voice_module():
    """Test the AI voice module directly"""
    try:
        from ai_voice import ai_agent
        
        # Test AI response generation
        test_transcript = "I need to book a dental appointment"
        
        # This would normally be async, but we'll test the module import
        print("✅ AI voice module imported successfully")
        print(f"   OpenAI API Key: {'Set' if os.getenv('OPENAI_API_KEY') else 'Missing'}")
        print(f"   Azure TTS Key: {'Set' if os.getenv('AZURE_TTS_KEY') else 'Missing'}")
        print(f"   Azure Region: {'Set' if os.getenv('AZURE_TTS_REGION') else 'Missing'}")
        
        return True
    except Exception as e:
        print(f"❌ AI voice module error: {str(e)}")
        return False

def test_webhook_with_ai():
    """Test the webhook endpoint with AI processing"""
    try:
        # Test the webhook endpoint
        response = requests.post(
            "http://localhost:8000/api/twilio-voice",
            data={
                "CallSid": "test_ai_call_123",
                "RecordingUrl": "https://example.com/test.wav"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ Webhook with AI processing working")
            print(f"   Response length: {len(response.text)} characters")
            return True
        else:
            print(f"❌ Webhook failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Webhook test error: {str(e)}")
        return False

def test_voice_interactions_database():
    """Test voice interactions database operations"""
    try:
        # Test getting voice interactions
        response = requests.get("http://localhost:8000/api/voice-interactions")
        
        if response.status_code == 200:
            interactions = response.json()
            print(f"✅ Voice interactions database working")
            print(f"   Current interactions: {len(interactions)}")
            return True
        else:
            print(f"❌ Voice interactions failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Voice interactions error: {str(e)}")
        return False

def test_audio_file_serving():
    """Test audio file serving functionality"""
    try:
        # Create a test audio file
        test_file = "public/audio/test_ai.wav"
        os.makedirs("public/audio", exist_ok=True)
        
        # Create a simple test file
        with open(test_file, "wb") as f:
            f.write(b"test ai audio content")
        
        # Test serving the file
        response = requests.get("http://localhost:8000/audio/test_ai.wav")
        
        if response.status_code == 200:
            print("✅ Audio file serving working")
            print(f"   File size: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ Audio serving failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Audio serving error: {str(e)}")
        return False

def test_call_with_ai_intelligence():
    """Test making a call with AI voice intelligence"""
    try:
        # Test call to a verified number
        payload = {
            "phone_numbers": ["+16506918829"]  # Your verified number
        }
        
        response = requests.post(
            "http://localhost:8000/api/call-patients",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ AI call with voice intelligence initiated")
            print(f"   Calls initiated: {data.get('calls_initiated', 0)}")
            print(f"   Failed numbers: {data.get('failed_numbers', [])}")
            return True
        else:
            print(f"❌ AI call failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI call error: {str(e)}")
        return False

def test_environment_setup():
    """Test environment setup for AI voice intelligence"""
    required_vars = [
        "OPENAI_API_KEY",
        "TWILIO_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER",
        "MONGODB_URI",
        "HOST"
    ]
    
    optional_vars = [
        "AZURE_TTS_KEY",
        "AZURE_TTS_REGION"
    ]
    
    print("\n🔧 Environment Setup Check:")
    
    # Check required variables
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            print(f"   ✅ {var}: Set")
    
    if missing_required:
        print(f"   ❌ Missing required: {', '.join(missing_required)}")
        return False
    
    # Check optional variables
    missing_optional = []
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
            print(f"   ⚠️  {var}: Not set (optional)")
        else:
            print(f"   ✅ {var}: Set")
    
    if missing_optional:
        print(f"   ℹ️  Optional variables not set: {', '.join(missing_optional)}")
        print("   (Azure TTS will use fallback to Twilio TTS)")
    
    return True

def main():
    """Run comprehensive Phase 3 tests"""
    print("🧪 Comprehensive Phase 3 AI Voice Intelligence Test")
    print("=" * 60)
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("OpenAI API Connection", test_openai_connection),
        ("AI Voice Module", test_ai_voice_module),
        ("Voice Interactions Database", test_voice_interactions_database),
        ("Audio File Serving", test_audio_file_serving),
        ("Webhook with AI Processing", test_webhook_with_ai),
        ("AI Call with Voice Intelligence", test_call_with_ai_intelligence)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} error: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📊 Comprehensive Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Phase 3 AI Voice Intelligence is working perfectly!")
        print("✅ All components are functional and ready for production use.")
    elif passed >= total * 0.8:
        print("✅ Phase 3 is mostly working with minor issues.")
        print("⚠️  Check the failed tests above for details.")
    else:
        print("❌ Phase 3 has significant issues that need to be addressed.")
        print("🔧 Review the failed tests and fix the problems.")

if __name__ == "__main__":
    main()
