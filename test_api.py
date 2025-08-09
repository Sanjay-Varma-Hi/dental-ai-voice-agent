#!/usr/bin/env python3
"""
Test script for Dental AI Voice Agent API
This script tests the main API endpoints
"""

import asyncio
import json
import requests

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
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

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n🏠 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint: {data}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {str(e)}")
        return False

def test_trigger_call(pincode):
    """Test the trigger call endpoint"""
    print(f"\n📞 Testing trigger call endpoint with pincode: {pincode}")
    
    payload = {"pincode": pincode}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/trigger-call",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Trigger call successful:")
            print(f"   Total patients: {data['total_count']}")
            for patient in data['patients']:
                print(f"   - {patient['name']}: {patient['phone_number']}")
            return True
        else:
            error_text = response.text
            print(f"❌ Trigger call failed: {response.status_code} - {error_text}")
            return False
    except Exception as e:
        print(f"❌ Trigger call error: {str(e)}")
        return False

def run_all_tests():
    """Run all API tests"""
    print("🧪 Starting API tests for Dental AI Voice Agent...")
    print("=" * 50)
    
    # Test health check
    health_ok = test_health_check()
    
    # Test root endpoint
    root_ok = test_root_endpoint()
    
    # Test trigger call with different pincodes
    pincodes = ["12345", "54321", "99999"]  # Last one should return empty results
    
    trigger_results = []
    for pincode in pincodes:
        result = test_trigger_call(pincode)
        trigger_results.append(result)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   Root Endpoint: {'✅ PASS' if root_ok else '❌ FAIL'}")
    print(f"   Trigger Call Tests: {sum(trigger_results)}/{len(trigger_results)} PASS")
    
    if health_ok and root_ok and all(trigger_results):
        print("\n🎉 All tests passed! Your API is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check your setup.")

if __name__ == "__main__":
    print("🚀 Starting API tests...")
    print("Make sure your server is running on http://localhost:8000")
    print("Press Ctrl+C to stop the tests\n")
    
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n⏹️  Tests stopped by user")
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        print("Make sure your server is running and accessible")
