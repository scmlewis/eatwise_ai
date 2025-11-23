-- ==================== GAMIFICATION MIGRATION ====================
-- This migration adds support for gamification features to EatWise
-- Run this in your Supabase SQL editor AFTER the main database_setup.sql

-- ==================== CREATE MISSING TABLES ====================

-- Create daily_challenges table
CREATE TABLE IF NOT EXISTS daily_challenges (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  challenge_date DATE NOT NULL,
  challenge_type VARCHAR(50),
  challenge_name VARCHAR(255),
  description TEXT,
  target INTEGER DEFAULT 0,
  current_progress INTEGER DEFAULT 0,
  xp_reward INTEGER DEFAULT 0,
  completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  UNIQUE(user_id, challenge_date, challenge_name)
);

-- Create weekly_goals table
CREATE TABLE IF NOT EXISTS weekly_goals (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  week_start_date DATE NOT NULL,
  target_days_with_nutrition_goals INTEGER DEFAULT 5,
  days_completed INTEGER DEFAULT 0,
  completed BOOLEAN DEFAULT FALSE,
  xp_reward INTEGER DEFAULT 200,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  UNIQUE(user_id, week_start_date)
);

-- Note: water_intake table should already exist from create_water_intake_table.sql
-- It uses: logged_date (not water_date), glasses (not glasses_count)
-- If you need to create it manually, use the schema from create_water_intake_table.sql

-- ==================== ADD MISSING COLUMNS ====================

-- Add XP tracking columns to health_profiles
ALTER TABLE health_profiles ADD COLUMN IF NOT EXISTS total_xp INTEGER DEFAULT 0;
ALTER TABLE health_profiles ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'UTC';

-- ==================== CREATE INDEXES ====================

-- Indexes for daily_challenges
CREATE INDEX IF NOT EXISTS idx_daily_challenges_user_id ON daily_challenges(user_id);
CREATE INDEX IF NOT EXISTS idx_daily_challenges_date ON daily_challenges(challenge_date);

-- Indexes for weekly_goals
CREATE INDEX IF NOT EXISTS idx_weekly_goals_user_id ON weekly_goals(user_id);
CREATE INDEX IF NOT EXISTS idx_weekly_goals_week_start ON weekly_goals(week_start_date);

-- ==================== ENABLE ROW LEVEL SECURITY ====================

-- Enable RLS on new tables
ALTER TABLE daily_challenges ENABLE ROW LEVEL SECURITY;
ALTER TABLE weekly_goals ENABLE ROW LEVEL SECURITY;
-- water_intake RLS should already be enabled from create_water_intake_table.sql

-- ==================== CREATE RLS POLICIES ====================

-- Daily challenges policies
DROP POLICY IF EXISTS "Users can view their daily challenges" ON daily_challenges;
CREATE POLICY "Users can view their daily challenges"
  ON daily_challenges FOR SELECT
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert daily challenges" ON daily_challenges;
CREATE POLICY "Users can insert daily challenges"
  ON daily_challenges FOR INSERT
  WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update daily challenges" ON daily_challenges;
CREATE POLICY "Users can update daily challenges"
  ON daily_challenges FOR UPDATE
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete daily challenges" ON daily_challenges;
CREATE POLICY "Users can delete daily challenges"
  ON daily_challenges FOR DELETE
  USING (auth.uid() = user_id);

-- Weekly goals policies
DROP POLICY IF EXISTS "Users can view their weekly goals" ON weekly_goals;
CREATE POLICY "Users can view their weekly goals"
  ON weekly_goals FOR SELECT
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert weekly goals" ON weekly_goals;
CREATE POLICY "Users can insert weekly goals"
  ON weekly_goals FOR INSERT
  WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update weekly goals" ON weekly_goals;
CREATE POLICY "Users can update weekly goals"
  ON weekly_goals FOR UPDATE
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete weekly goals" ON weekly_goals;
CREATE POLICY "Users can delete weekly goals"
  ON weekly_goals FOR DELETE
  USING (auth.uid() = user_id);

-- ==================== GAMIFICATION MIGRATION COMPLETE ====================
-- All gamification tables and policies are now set up
-- You can now run the EatWise app with full gamification support
