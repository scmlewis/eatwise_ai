#!/usr/bin/env python3
"""
Test script to debug profile loading issues
Checks if profiles are being created and loaded correctly on login
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

def test_supabase_connection():
    """Test Supabase connection"""
    print("=" * 60)
    print("1. Testing Supabase Connection")
    print("=" * 60)
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ SUPABASE_URL or SUPABASE_KEY not configured")
        return False
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Try a simple query
        result = supabase.table("users").select("count", count="exact").execute()
        print(f"✅ Supabase connection successful")
        print(f"   Users table has {result.count} records")
        return True
    except Exception as e:
        print(f"❌ Supabase connection failed: {str(e)}")
        return False

def test_health_profiles_table():
    """Test if health_profiles table exists and has data"""
    print("\n" + "=" * 60)
    print("2. Testing health_profiles Table")
    print("=" * 60)
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        result = supabase.table("health_profiles").select("count", count="exact").execute()
        print(f"✅ health_profiles table exists")
        print(f"   Contains {result.count} profiles")
        
        # Show a sample
        if result.count > 0:
            samples = supabase.table("health_profiles").select("*").limit(3).execute()
            print(f"\n   Sample profiles:")
            for profile in samples.data:
                print(f"   - User {profile.get('user_id', 'unknown')[:8]}...: age={profile.get('age_group', 'N/A')}, goal={profile.get('health_goal', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"❌ health_profiles table error: {str(e)}")
        return False

def test_specific_user(test_user_id):
    """Test profile loading for a specific user"""
    print("\n" + "=" * 60)
    print(f"3. Testing Profile Loading for User: {test_user_id[:8]}...")
    print("=" * 60)
    
    try:
        db = DatabaseManager()
        
        # Try to fetch profile
        profile = db.get_health_profile(test_user_id)
        
        if profile:
            print(f"✅ Profile found for user")
            print(f"   age_group: {profile.get('age_group', 'N/A')}")
            print(f"   health_goal: {profile.get('health_goal', 'N/A')}")
            print(f"   health_conditions: {profile.get('health_conditions', [])}")
            print(f"   dietary_preferences: {profile.get('dietary_preferences', [])}")
            print(f"   timezone: {profile.get('timezone', 'N/A')}")
            return True
        else:
            print(f"❌ No profile found for user")
            return False
    except Exception as e:
        print(f"❌ Error loading profile: {str(e)}")
        return False

def list_recent_logins():
    """List recent user records from the users table"""
    print("\n" + "=" * 60)
    print("4. Recent User Records (All)")
    print("=" * 60)
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        result = supabase.table("users").select("*").order("created_at", desc=True).execute()
        
        if result.data:
            print(f"\nFound {len(result.data)} total users:")
            for user in result.data:
                user_id = user.get('user_id', 'unknown')
                # Check if this user has a profile
                profiles = supabase.table("health_profiles").select("user_id").eq("user_id", user_id).execute()
                has_profile = "✓" if profiles.data else "✗"
                print(f"\n{has_profile} User: {user.get('email', 'unknown')}")
                print(f"    ID: {user_id}")
                print(f"    Full Name: {user.get('full_name', 'N/A')}")
                if profiles.data:
                    print(f"    Profile: EXISTS")
                else:
                    print(f"    Profile: MISSING")
            return result.data
        else:
            print("No users found")
            return []
    except Exception as e:
        print(f"❌ Error listing users: {str(e)}")
        return []

if __name__ == "__main__":
    print("\n🔍 EatWise Profile Loading Diagnostics\n")
    
    success = True
    success = test_supabase_connection() and success
    success = test_health_profiles_table() and success
    
    # Get a recent user to test
    recent_users = list_recent_logins()
    if recent_users:
        test_user = recent_users[0]['user_id']
        success = test_specific_user(test_user) and success
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All diagnostics passed!")
    else:
        print("❌ Some diagnostics failed - check above for details")
    print("=" * 60 + "\n")
