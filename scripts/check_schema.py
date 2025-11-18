#!/usr/bin/env python3
"""Check food_history table schema"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

try:
    # Try to get one record to see schema
    response = supabase.table("food_history").select("*").limit(1).execute()
    print("food_history table columns:")
    if response.data:
        for key in response.data[0].keys():
            print(f"  - {key}")
    else:
        print("Table is empty, checking with insert attempt...")
        # Try a minimal insert to see what columns are required
        test_data = {
            "user_id": "test-user",
            "food_name": "test",
        }
        print(f"Attempting minimal insert with: {test_data}")
except Exception as e:
    print(f"Error: {e}")
