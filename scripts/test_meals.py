#!/usr/bin/env python3
"""Test meal saving functionality"""

from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY
from datetime import datetime
import uuid

def test_meal_saving():
    """Test if we can save meals to the database"""
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("=" * 60)
    print("MEAL SAVING TEST")
    print("=" * 60)
    
    # First, check if users exist
    print("\n1. Checking users in database...")
    try:
        users = supabase.table("users").select("*").execute()
        if users.data:
            print(f"✓ Found {len(users.data)} user(s)")
            for user in users.data:
                print(f"  - {user['email']} (ID: {user['user_id']})")
                user_id = user['user_id']
        else:
            print("❌ No users found in database")
            print("\nTo fix this:")
            print("1. Go to your Supabase Auth tab")
            print("2. Create a new user or confirm you've signed up in the app")
            return False
    except Exception as e:
        print(f"❌ Error fetching users: {e}")
        return False
    
    # Test inserting a meal
    print("\n2. Testing meal insertion...")
    try:
        test_meal = {
            "user_id": user_id,
            "meal_name": "Test Meal",
            "description": "A test meal entry",
            "meal_type": "breakfast",
            "nutrition": {
                "calories": 300,
                "protein": 15,
                "carbs": 40,
                "fat": 10,
                "sodium": 500,
                "sugar": 5,
                "fiber": 3
            },
            "healthiness_score": 75,
            "health_notes": "Test entry",
            "logged_at": datetime.now().isoformat()
        }
        
        result = supabase.table("meals").insert(test_meal).execute()
        
        if result.data:
            print(f"✓ Meal saved successfully!")
            print(f"  Meal ID: {result.data[0]['id']}")
        else:
            print("❌ Failed to save meal")
            return False
            
    except Exception as e:
        print(f"❌ Error saving meal: {e}")
        print("\nTroubleshooting:")
        print("- Check if Row Level Security (RLS) is enabled on the meals table")
        print("- Verify the RLS policy allows authenticated users to insert meals")
        return False
    
    # Verify the meal was saved
    print("\n3. Verifying meal was saved...")
    try:
        meals = supabase.table("meals").select("*").eq("user_id", user_id).execute()
        if meals.data:
            print(f"✓ Found {len(meals.data)} meal(s) for this user")
            for meal in meals.data:
                print(f"  - {meal['meal_name']} ({meal['meal_type']})")
        else:
            print("❌ No meals found for this user")
            return False
            
    except Exception as e:
        print(f"❌ Error fetching meals: {e}")
        return False
    
    print("\n✅ All tests passed! Meals are being saved correctly.")
    return True

if __name__ == "__main__":
    success = test_meal_saving()
    import sys
    sys.exit(0 if success else 1)
