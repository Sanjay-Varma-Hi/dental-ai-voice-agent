#!/usr/bin/env python3
"""
Test script for Twilio integration in Dental AI Voice Agent
This script tests the Twilio calling functionality
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint with Twilio status"""
    print("🏥 Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_call_patients_by_pincode():
    """Test calling patients by pincode"""
    print(f"\n📞 Testing call patients by pincode...")
    
    payload = {"pincode": "12345"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/call-patients",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Call patients successful:")
            print(f"   Message: {data['message']}")
            print(f"   Calls initiated: {data['calls_initiated']}")
            if data.get('failed_numbers'):
                print(f"   Failed numbers: {data['failed_numbers']}")
            return True
        else:
            error_text = response.text
            print(f"❌ Call patients failed: {response.status_code} - {error_text}")
            return False
    except Exception as e:
        print(f"❌ Call patients error: {str(e)}")
        return False

def test_call_patients_by_phone_numbers():
    """Test calling specific phone numbers"""
    print(f"\n📞 Testing call patients by phone numbers...")
    
    # Test with mock phone numbers (replace with real numbers for actual testing)
    payload = {
        "phone_numbers": ["+1234567890", "+1234567891"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/call-patients",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Call patients successful:")
            print(f"   Message: {data['message']}")
            print(f"   Calls initiated: {data['calls_initiated']}")
            if data.get('failed_numbers'):
                print(f"   Failed numbers: {data['failed_numbers']}")
            return True
        else:
            error_text = response.text
            print(f"❌ Call patients failed: {response.status_code} - {error_text}")
            return False
    except Exception as e:
        print(f"❌ Call patients error: {str(e)}")
        return False

def test_call_logs():
    """Test getting call logs"""
    print(f"\n📋 Testing call logs endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/call-logs")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Call logs retrieved: {len(data)} logs found")
            for log in data[:3]:  # Show first 3 logs
                print(f"   - {log.get('phone_number')}: {log.get('status')} at {log.get('timestamp')}")
            return True
        else:
            error_text = response.text
            print(f"❌ Call logs failed: {response.status_code} - {error_text}")
            return False
    except Exception as e:
        print(f"❌ Call logs error: {str(e)}")
        return False

def check_twilio_config():
    """Check if Twilio is properly configured"""
    print("🔧 Checking Twilio configuration...")
    
    twilio_sid = os.getenv("TWILIO_SID")
    twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
    
    if twilio_sid and twilio_auth_token and twilio_phone:
        print("✅ Twilio credentials found")
        print(f"   SID: {twilio_sid[:10]}...")
        print(f"   Phone: {twilio_phone}")
        return True
    else:
        print("❌ Twilio credentials missing")
        print("   Please add TWILIO_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER to your .env file")
        return False

def run_all_tests():
    """Run all Twilio tests"""
    print("🧪 Starting Twilio integration tests...")
    print("=" * 60)
    
    # Check configuration
    config_ok = check_twilio_config()
    
    # Test health check
    health_ok = test_health_check()
    
    # Test call patients by pincode
    pincode_ok = test_call_patients_by_pincode()
    
    # Test call patients by phone numbers
    phone_ok = test_call_patients_by_phone_numbers()
    
    # Test call logs
    logs_ok = test_call_logs()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Twilio Test Summary:")
    print(f"   Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"   Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   Call by Pincode: {'✅ PASS' if pincode_ok else '❌ FAIL'}")
    print(f"   Call by Phone: {'✅ PASS' if phone_ok else '❌ FAIL'}")
    print(f"   Call Logs: {'✅ PASS' if logs_ok else '❌ FAIL'}")
    
    if config_ok and health_ok:
        print("\n🎉 Twilio integration is working!")
        print("📞 You can now make voice calls to patients")
    else:
        print("\n⚠️  Some tests failed. Please check your Twilio configuration.")

if __name__ == "__main__":
    print("🚀 Starting Twilio integration tests...")
    print("Make sure your server is running on http://localhost:8000")
    print("Press Ctrl+C to stop the tests\n")
    
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n⏹️  Tests stopped by user")
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        print("Make sure your server is running and accessible")
