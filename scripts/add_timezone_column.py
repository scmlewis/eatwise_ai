"""
Migration script to add timezone column to health_profiles table in Supabase
Run this script once to add the timezone column
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def add_timezone_column():
    """Add timezone column to health_profiles table"""
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # SQL to add timezone column
    sql = """
    ALTER TABLE health_profiles 
    ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'UTC';
    """
    
    try:
        # Execute the SQL via Supabase's Python client using raw query
        response = supabase.postgrest.raw(sql)
        print("✅ Timezone column added successfully!")
        return True
    except Exception as e:
        print(f"❌ Error adding timezone column: {e}")
        return False

def add_timezone_column_manual():
    """
    Manual method: Go to Supabase dashboard and run this SQL in the SQL Editor:
    
    ALTER TABLE health_profiles 
    ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'UTC';
    """
    print("""
    ===== MANUAL METHOD =====
    
    If the automatic method fails, please manually add the timezone column:
    
    1. Go to: https://supabase.com/dashboard
    2. Select your project
    3. Click "SQL Editor" in the left sidebar
    4. Click "New Query"
    5. Copy and paste this SQL:
    
    ALTER TABLE health_profiles 
    ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'UTC';
    
    6. Click "Run"
    
    That's it! The timezone column will be added to all existing profiles with 'UTC' as default.
    """)

if __name__ == "__main__":
    print("Adding timezone column to health_profiles table...")
    
    if add_timezone_column():
        print("\nTimezone column has been added successfully!")
    else:
        print("\nAutomatic method failed. Using manual method instead:")
        add_timezone_column_manual()
