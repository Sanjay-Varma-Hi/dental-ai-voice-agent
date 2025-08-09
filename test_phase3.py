#!/usr/bin/env python3
"""
Test script for Phase 3: AI Voice Intelligence
Tests OpenAI Whisper, GPT-4o, and Azure TTS integration
"""

import os
import asyncio
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_health():
    """Test if the server is running and healthy"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Database: {data.get('database', 'unknown')}")
            print(f"   Twilio: {data.get('twilio', 'unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_voice_interactions():
    """Test voice interactions endpoint"""
    try:
        response = requests.get("http://localhost:8000/api/voice-interactions")
        if response.status_code == 200:
            interactions = response.json()
            print(f"✅ Voice interactions endpoint working")
            print(f"   Found {len(interactions)} interactions")
            return True
        else:
            print(f"❌ Voice interactions failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Voice interactions error: {str(e)}")
        return False

def test_audio_endpoint():
    """Test audio file serving endpoint"""
    try:
        # Create a test audio file
        test_file = "public/audio/test.wav"
        os.makedirs("public/audio", exist_ok=True)
        
        # Create a simple test file
        with open(test_file, "wb") as f:
            f.write(b"test audio content")
        
        response = requests.get("http://localhost:8000/audio/test.wav")
        if response.status_code == 200:
            print("✅ Audio endpoint working")
            return True
        else:
            print(f"❌ Audio endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Audio endpoint error: {str(e)}")
        return False

def test_call_with_ai():
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
            print("✅ AI call initiated successfully")
            print(f"   Calls initiated: {data.get('calls_initiated', 0)}")
            print(f"   Failed numbers: {data.get('failed_numbers', [])}")
            return True
        else:
            print(f"❌ AI call failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI call error: {str(e)}")
        return False

def check_environment():
    """Check if required environment variables are set"""
    required_vars = [
        "OPENAI_API_KEY",
        "AZURE_TTS_KEY", 
        "AZURE_TTS_REGION"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("   Please add them to your .env file")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def main():
    """Run all Phase 3 tests"""
    print("🧪 Testing Phase 3: AI Voice Intelligence")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", check_environment),
        ("Health Check", test_health),
        ("Voice Interactions Endpoint", test_voice_interactions),
        ("Audio Endpoint", test_audio_endpoint),
        ("AI Call Test", test_call_with_ai)
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
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Phase 3 is ready! All tests passed.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    main()
