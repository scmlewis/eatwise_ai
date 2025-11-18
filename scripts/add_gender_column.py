"""Add gender column to health_profiles table"""

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    # Execute raw SQL to add the gender column
    result = supabase.rpc("add_gender_column", {}).execute()
    print("✅ Gender column added successfully!")
except Exception as e:
    print(f"⚠️  Attempting SQL approach...")
    # If RPC doesn't work, we'll need to use SQL directly through admin API
    # For now, let's try via the client
    try:
        # Try to add the column via a PostgreSQL query
        # This might require admin privileges
        sql = """
        ALTER TABLE health_profiles
        ADD COLUMN IF NOT EXISTS gender VARCHAR(50) DEFAULT NULL;
        """
        print(f"Please add this SQL to Supabase SQL Editor:")
        print(sql)
        print("\nOr use the Supabase Dashboard:")
        print("1. Go to Database > health_profiles")
        print("2. Click 'New Column'")
        print("3. Name: gender")
        print("4. Type: text")
        print("5. Default value: NULL (optional)")
    except Exception as e2:
        print(f"Error: {str(e2)}")
