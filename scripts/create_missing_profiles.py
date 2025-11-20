#!/usr/bin/env python3
"""
Script to create missing health profiles for users
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

def create_profile_for_user(user_id, email, full_name=""):
    """Create a default health profile for a user"""
    try:
        db = DatabaseManager()
        
        profile_data = {
            "user_id": user_id,
            "full_name": full_name,
            "age_group": "26-35",
            "gender": "Prefer not to say",
            "timezone": "UTC",
            "health_conditions": [],
            "dietary_preferences": [],
            "health_goal": "general_health",
            "water_goal_glasses": 8
        }
        
        if db.create_health_profile(user_id, profile_data):
            print(f"✅ Created profile for {email}")
            return True
        else:
            print(f"❌ Failed to create profile for {email}")
            return False
    except Exception as e:
        print(f"❌ Error creating profile: {str(e)}")
        return False

def list_and_fix_missing_profiles():
    """List all users and create profiles for those missing them"""
    print("\n" + "=" * 60)
    print("Creating Missing Health Profiles")
    print("=" * 60 + "\n")
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        users = supabase.table("users").select("*").execute()
        
        missing_count = 0
        created_count = 0
        
        for user in users.data:
            user_id = user.get('user_id')
            email = user.get('email')
            full_name = user.get('full_name', '')
            
            # Check if user has profile
            profiles = supabase.table("health_profiles").select("user_id").eq("user_id", user_id).execute()
            
            if not profiles.data:
                print(f"Missing profile for: {email}")
                missing_count += 1
                if create_profile_for_user(user_id, email, full_name):
                    created_count += 1
            else:
                print(f"✓ Has profile: {email}")
        
        print("\n" + "=" * 60)
        print(f"Summary: {missing_count} missing profiles, {created_count} created")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    list_and_fix_missing_profiles()
