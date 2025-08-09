#!/usr/bin/env python3
"""
Sample data setup script for Dental AI Voice Agent
This script populates the MongoDB database with sample patient data
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Sample patient data
SAMPLE_PATIENTS = [
    {
        "name": "Sanjay",
        "phone_number": "+15109603865",
        "pincode": "95050",
        "email": "sanjayvarmacol@gmail.com",
        "last_visit": "2024-01-15",
        "next_appointment": "2024-03-20"
    },
    {
        "name": "Jane Smith",
        "phone_number": "+16506918829",
        "pincode": "12121",
        "email": "jane.smith@email.com",
        "last_visit": "2024-02-01",
        "next_appointment": "2024-04-10"
    },
    {
        "name": "Mike Johnson",
        "phone_number": "+1234567892",
        "pincode": "12345",
        "email": "mike.johnson@email.com",
        "last_visit": "2024-01-30",
        "next_appointment": "2024-03-25"
    },
    {
        "name": "Sarah Wilson",
        "phone_number": "+1234567893",
        "pincode": "54321",
        "email": "sarah.wilson@email.com",
        "last_visit": "2024-02-10",
        "next_appointment": "2024-04-15"
    },
    {
        "name": "David Brown",
        "phone_number": "+1234567894",
        "pincode": "54321",
        "email": "david.brown@email.com",
        "last_visit": "2024-01-25",
        "next_appointment": "2024-03-30"
    }
]

async def setup_sample_data():
    """Setup sample patient data in MongoDB"""
    
    # Get MongoDB connection string
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        print("❌ Error: MONGODB_URI environment variable is required")
        print("Please set up your .env file with the MongoDB connection string")
        return
    
    try:
        # Connect to MongoDB
        print("🔌 Connecting to MongoDB...")
        client = AsyncIOMotorClient(mongodb_uri)
        db = client.dental_clinic
        
        # Test connection
        await client.admin.command('ping')
        print("✅ Successfully connected to MongoDB")
        
        # Clear existing data (optional)
        print("🧹 Clearing existing patient data...")
        await db.patients.delete_many({})
        
        # Insert sample data
        print("📝 Inserting sample patient data...")
        result = await db.patients.insert_many(SAMPLE_PATIENTS)
        
        print(f"✅ Successfully inserted {len(result.inserted_ids)} patients")
        
        # Display inserted data
        print("\n📋 Sample patients inserted:")
        for patient in SAMPLE_PATIENTS:
            print(f"  - {patient['name']} ({patient['phone_number']}) - Pincode: {patient['pincode']}")
        
        print(f"\n🎯 You can now test the API with pincodes: 12345, 54321")
        print("   Example: POST /api/trigger-call with body: {\"pincode\": \"12345\"}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("Please check your MongoDB connection string and network connectivity")
    
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    print("🚀 Setting up sample data for Dental AI Voice Agent...")
    asyncio.run(setup_sample_data())
