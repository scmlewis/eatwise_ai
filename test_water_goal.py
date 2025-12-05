#!/usr/bin/env python3
"""Test script to debug water_goal_glasses persistence"""

from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test with a specific user (change this to your actual user ID)
test_user_id = input("Enter your user ID (UUID): ").strip()

if not test_user_id:
    print("No user ID provided. Exiting.")
    exit(1)

try:
    # 1. Fetch current profile
    print(f"\n1. Fetching profile for user {test_user_id}...")
    response = supabase.table("health_profiles").select("*").eq("user_id", test_user_id).execute()
    
    if not response.data:
        print("ERROR: No profile found for this user")
        exit(1)
    
    profile = response.data[0]
    current_water_goal = profile.get("water_goal_glasses")
    print(f"   Current water_goal_glasses: {current_water_goal} (type: {type(current_water_goal).__name__})")
    
    # 2. Update water_goal_glasses to 9
    print(f"\n2. Updating water_goal_glasses to 9...")
    update_response = supabase.table("health_profiles").update({"water_goal_glasses": 9}).eq("user_id", test_user_id).execute()
    print(f"   Update response: {update_response}")
    
    # 3. Fetch again to verify
    print(f"\n3. Fetching profile again to verify update...")
    response2 = supabase.table("health_profiles").select("*").eq("user_id", test_user_id).execute()
    
    if response2.data:
        profile2 = response2.data[0]
        new_water_goal = profile2.get("water_goal_glasses")
        print(f"   New water_goal_glasses: {new_water_goal} (type: {type(new_water_goal).__name__})")
        
        if new_water_goal == 9:
            print("\n✅ SUCCESS: water_goal_glasses was updated to 9!")
        else:
            print(f"\n❌ FAILED: water_goal_glasses is still {new_water_goal}, not 9!")
    else:
        print("ERROR: Profile not found after update")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
