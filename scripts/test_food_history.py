#!/usr/bin/env python3
"""Test food_history table functionality"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

load_dotenv()

# Initialize Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def test_food_history():
    """Test food_history table"""
    print("=" * 60)
    print("Testing food_history Table")
    print("=" * 60)
    
    try:
        # Get current food history entries
        response = supabase.table("food_history").select("*").execute()
        entries = response.data
        
        print(f"\n✅ food_history table is accessible")
        print(f"Total entries: {len(entries)}")
        
        if entries:
            print("\nCurrent entries:")
            for entry in entries:
                print(f"\n  - ID: {entry.get('id')}")
                print(f"    User: {entry.get('user_id')[:20]}...")
                print(f"    Food: {entry.get('food_name')}")
                print(f"    Calories: {entry.get('calories')} kcal")
                print(f"    Protein: {entry.get('protein')}g")
                print(f"    Date: {entry.get('created_at')}")
        else:
            print("\n⚠️  No entries yet in food_history table")
            print("\nTo populate food_history:")
            print("  1. Go to 'Log Meal' page in the app")
            print("  2. Enter a food item (e.g., 'chicken breast')")
            print("  3. Click 'Analyze' to get nutritional info")
            print("  4. Click 'Save This Meal' to save to database")
            print("  5. This will create entries in both 'meals' and 'food_history' tables")
        
        return True
    except Exception as e:
        print(f"❌ Error accessing food_history: {e}")
        return False

if __name__ == "__main__":
    test_food_history()
