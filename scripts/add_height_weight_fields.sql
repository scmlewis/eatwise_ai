-- ==================== ADD HEIGHT AND WEIGHT FIELDS ====================
-- This migration adds optional height and weight fields to health_profiles table
-- Run this in your Supabase SQL editor to update existing deployments

-- Add height column (in cm, optional)
ALTER TABLE health_profiles
ADD COLUMN IF NOT EXISTS height_cm FLOAT;

-- Add weight column (in kg, optional)
ALTER TABLE health_profiles
ADD COLUMN IF NOT EXISTS weight_kg FLOAT;

-- Add comment to document the fields
COMMENT ON COLUMN health_profiles.height_cm IS 'User height in centimeters (optional)';
COMMENT ON COLUMN health_profiles.weight_kg IS 'User weight in kilograms (optional)';

-- Create an index on user_id for faster lookups (if not already present)
CREATE INDEX IF NOT EXISTS idx_health_profiles_user_id ON health_profiles(user_id);
