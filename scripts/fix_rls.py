#!/usr/bin/env python3
"""
Check and fix RLS policies for the users table
"""

print("""
================================================================================
SUPABASE RLS POLICY FIX
================================================================================

The issue is likely that the RLS (Row Level Security) policies are too
restrictive on the 'users' table.

The 'users' table needs policies that allow:
1. Authenticated users to INSERT their own record
2. Authenticated users to SELECT/UPDATE their own records
3. Service role to bypass RLS (for admin operations)

================================================================================
MANUAL FIX REQUIRED
================================================================================

Please follow these steps in your Supabase Dashboard:

1. Go to Authentication > Policies (under your EatWise project)
2. Select the 'users' table
3. Check the existing policies - they might be too restrictive

If you see a policy like:
   "Users can view their own data" 
   ON users FOR SELECT
   USING (auth.uid() = user_id)

This policy is CORRECT for SELECT.

But you ALSO NEED an INSERT policy like this:

   Name: "Users can create their own record"
   Table: users
   Target roles: authenticated
   Command: INSERT
   Policy:
     WITH CHECK (auth.uid() = user_id)

4. If this INSERT policy doesn't exist, create it:
   - Click "+ Create Policy"
   - Choose "Create a policy from scratch"
   - Name: "Users can create their own record"
   - Action: INSERT
   - Target roles: authenticated
   - WITH CHECK expression: auth.uid() = user_id

5. Also check for an UPDATE policy - add if missing:
   Name: "Users can update their own record"
   Table: users
   Target roles: authenticated
   Command: UPDATE
   Policy: (same as SELECT policy)
   USING (auth.uid() = user_id)

6. Once these policies are added, try logging in again in the app.

================================================================================
ALTERNATIVE: Disable RLS temporarily (NOT RECOMMENDED for production)
================================================================================

If you want to test without RLS:
1. Go to your users table in Supabase
2. Click the "lock" icon (RLS badge)
3. Toggle "Enable RLS" OFF
4. Test in the app
5. When working, re-enable RLS with proper policies

================================================================================
""")

input("\nPress Enter when you've completed the policy setup...")

print("\nNow try logging in to the app again and saving a meal.")
print("The user record should be created and meals should save.")
