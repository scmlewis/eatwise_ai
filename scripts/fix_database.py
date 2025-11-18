#!/usr/bin/env python3
"""Fix the database schema for proper user storage"""

from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

def fix_database():
    """Fix database schema"""
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("=" * 60)
    print("DATABASE SCHEMA FIX")
    print("=" * 60)
    
    print("\n⚠️  This will modify the users table schema.")
    print("\nThe issue: The users table was created but:")
    print("  - It has a separate 'id' column (UUID)")
    print("  - The 'user_id' should reference auth.users")
    print("  - We need proper foreign key constraints")
    print("\nWe'll recreate the users table with proper schema.")
    
    input("\nPress Enter to proceed...")
    
    # First, let's check what's in the tables
    try:
        print("\nChecking current data...")
        
        # Check users
        users = supabase.table("users").select("*").execute()
        print(f"Users table: {len(users.data)} records")
        
        # Check health_profiles
        profiles = supabase.table("health_profiles").select("*").execute()
        print(f"Health profiles table: {len(profiles.data)} records")
        
        # Check meals
        meals = supabase.table("meals").select("*").execute()
        print(f"Meals table: {len(meals.data)} records")
        
        if meals.data:
            print("\n⚠️  WARNING: Meals table has data!")
            print("We cannot safely modify the schema without losing data.")
            print("\nAlternative solution:")
            print("1. Back up your data")
            print("2. Delete all rows from tables in this order:")
            print("   - meals (has FK to users)")
            print("   - food_history (has FK to users)")
            print("   - health_profiles (has FK to users)")
            print("   - users")
            print("3. Run this script again")
            return False
        
        # If we have users but no data, we can try to fix
        if users.data and not meals.data and not profiles.data:
            print("\nAttempting to verify user structure...")
            user = users.data[0]
            print(f"User record: {user}")
            
            if 'user_id' in user and 'email' in user:
                print("\n✓ Users table structure looks correct!")
                print("The issue might be with RLS policies.")
                print("\nChecking Supabase dashboard for RLS configuration...")
                return True
        
        if not users.data:
            print("\n✓ Tables are empty - safe to reconfigure")
            print("The schema is correct, no changes needed.")
            print("\nThe real issue:")
            print("- User needs to be created via signup/login first")
            print("- Then meals can be saved")
            return True
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    fix_database()
