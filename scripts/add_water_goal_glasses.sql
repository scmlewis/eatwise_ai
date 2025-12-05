-- Add water_goal_glasses column to health_profiles table
-- This stores the user's daily water intake target in glasses

ALTER TABLE health_profiles ADD COLUMN IF NOT EXISTS water_goal_glasses INTEGER DEFAULT 8;

-- Create index for potential filtering by water goals
CREATE INDEX IF NOT EXISTS idx_health_profiles_water_goal ON health_profiles(water_goal_glasses);
