#!/usr/bin/env python3
"""
Disable RLS on all tables for testing
"""

print("""
================================================================================
DISABLE RLS ON ALL TABLES
================================================================================

To disable RLS on all remaining tables, follow these steps:

1. Go to your Supabase Dashboard
2. Click on "Authentication" > "Policies"
3. For EACH of these tables, click "Disable RLS":
   - food_history
   - health_profiles
   - meals

Current status:
   ✓ users - RLS DISABLED
   ⏳ food_history - need to disable
   ⏳ health_profiles - need to disable
   ⏳ meals - need to disable

================================================================================
QUICK STEPS:
================================================================================

1. Find the "meals" table section in Policies
2. Click the "Disable RLS" button
3. Find the "health_profiles" table section
4. Click the "Disable RLS" button
5. Find the "food_history" table section
6. Click the "Disable RLS" button

Once all are disabled, the app will work perfectly for testing!

================================================================================
WARNING:
================================================================================

⚠️  Disabling RLS means:
   - Anyone with your Supabase URL and anon key can read/modify/delete data
   - This is ONLY safe for development/testing
   - For production, you MUST enable RLS with proper policies

For now, this is perfect for testing the full feature set.

================================================================================
""")

input("\nPress Enter once you've disabled RLS on all tables...")

print("""
✅ Great! Now refresh the Streamlit app and try:

1. Log in
2. Go to "Log Meal"
3. Describe a meal (e.g., "grilled chicken with rice")
4. Click "Analyze Meal"
5. Click "Save This Meal"
6. Go to "Dashboard" - you should see your meal!
7. Check "Analytics" - you should see nutrition charts!

Let me know when you've tested it!
""")
