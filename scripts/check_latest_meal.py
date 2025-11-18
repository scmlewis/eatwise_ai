#!/usr/bin/env python3
"""Debug script to check the latest meal and its timestamp"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

try:
    # Get the latest meal
    response = supabase.table("meals").select("meal_name, logged_at, nutrition").order("logged_at", desc=True).limit(5).execute()
    meals = response.data
    
    print("=" * 80)
    print("Latest 5 Meals")
    print("=" * 80)
    
    for meal in meals:
        logged_at = meal.get("logged_at", "N/A")
        meal_date = logged_at.split("T")[0] if logged_at != "N/A" else "N/A"
        meal_time = logged_at.split("T")[1][:8] if logged_at != "N/A" else "N/A"
        calories = meal.get("nutrition", {}).get("calories", "N/A")
        
        print(f"\nMeal: {meal.get('meal_name')}")
        print(f"  Logged At: {logged_at}")
        print(f"  Date: {meal_date}, Time: {meal_time}")
        print(f"  Calories: {calories}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
