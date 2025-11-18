#!/usr/bin/env python3
"""Debug script to check meal timestamps in database"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

try:
    # Get all meals
    response = supabase.table("meals").select("user_id, meal_name, logged_at, nutrition").execute()
    meals = response.data
    
    print("=" * 80)
    print("All Meals in Database")
    print("=" * 80)
    
    if not meals:
        print("No meals found")
    else:
        for meal in meals:
            logged_at = meal.get("logged_at", "N/A")
            meal_date = logged_at.split("T")[0] if logged_at != "N/A" else "N/A"
            calories = meal.get("nutrition", {}).get("calories", "N/A")
            
            print(f"\nMeal: {meal.get('meal_name')}")
            print(f"  Logged At: {logged_at}")
            print(f"  Date Only: {meal_date}")
            print(f"  Calories: {calories}")
            print(f"  User ID: {meal.get('user_id')[:20]}...")
    
    print("\n" + "=" * 80)
    print("Testing Date Filters")
    print("=" * 80)
    
    today = date.today()
    yesterday = date(2025, 11, 17)
    
    print(f"\nToday's date: {today}")
    print(f"Yesterday's date: {yesterday}")
    
    # Test filtering for today
    today_str = today.isoformat()
    response_today = supabase.table("meals").select("meal_name, logged_at").gte("logged_at", f"{today_str}T00:00:00").lte("logged_at", f"{today_str}T23:59:59").execute()
    print(f"\nMeals for {today}: {len(response_today.data)} found")
    for meal in response_today.data:
        print(f"  - {meal.get('meal_name')} at {meal.get('logged_at')}")
    
    # Test filtering for yesterday
    yesterday_str = yesterday.isoformat()
    response_yesterday = supabase.table("meals").select("meal_name, logged_at").gte("logged_at", f"{yesterday_str}T00:00:00").lte("logged_at", f"{yesterday_str}T23:59:59").execute()
    print(f"\nMeals for {yesterday}: {len(response_yesterday.data)} found")
    for meal in response_yesterday.data:
        print(f"  - {meal.get('meal_name')} at {meal.get('logged_at')}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
