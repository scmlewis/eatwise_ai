-- ==================== SUPABASE DATABASE SETUP ====================
-- This file contains SQL queries to set up the EatWise database schema
-- Run these commands in your Supabase SQL editor

-- ==================== USERS TABLE ====================
CREATE TABLE users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL UNIQUE,
  email VARCHAR(255) NOT NULL UNIQUE,
  full_name VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================== HEALTH PROFILES TABLE ====================
CREATE TABLE health_profiles (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL UNIQUE,
  full_name VARCHAR(255),
  age_group VARCHAR(50),
  health_conditions TEXT[] DEFAULT '{}',
  dietary_preferences TEXT[] DEFAULT '{}',
  health_goal VARCHAR(100),
  badges_earned TEXT[] DEFAULT '{}',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ==================== MEALS TABLE ====================
CREATE TABLE meals (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  meal_name VARCHAR(255),
  description TEXT,
  meal_type VARCHAR(50),
  nutrition JSONB DEFAULT '{}',
  healthiness_score INTEGER DEFAULT 0,
  health_notes TEXT,
  logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ==================== FOOD HISTORY TABLE ====================
CREATE TABLE food_history (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  food_name VARCHAR(255),
  nutrition JSONB DEFAULT '{}',
  last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  usage_count INTEGER DEFAULT 1,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ==================== WATER INTAKE TABLE ====================
CREATE TABLE water_intake (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  water_date DATE NOT NULL,
  glasses_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
  UNIQUE(user_id, water_date)
);

-- ==================== DAILY CHALLENGES TABLE ====================
CREATE TABLE daily_challenges (
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

-- ==================== WEEKLY GOALS TABLE ====================
CREATE TABLE weekly_goals (
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

-- ==================== UPDATE HEALTH PROFILES TABLE ====================
-- Add total_xp column to track user experience points
ALTER TABLE health_profiles ADD COLUMN IF NOT EXISTS total_xp INTEGER DEFAULT 0;
ALTER TABLE health_profiles ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'UTC';

-- ==================== INDEXES ====================
CREATE INDEX idx_meals_user_id ON meals(user_id);
CREATE INDEX idx_meals_logged_at ON meals(logged_at);
CREATE INDEX idx_health_profiles_user_id ON health_profiles(user_id);
CREATE INDEX idx_food_history_user_id ON food_history(user_id);
CREATE INDEX idx_water_intake_user_id ON water_intake(user_id);
CREATE INDEX idx_water_intake_date ON water_intake(water_date);
CREATE INDEX idx_daily_challenges_user_id ON daily_challenges(user_id);
CREATE INDEX idx_daily_challenges_date ON daily_challenges(challenge_date);
CREATE INDEX idx_weekly_goals_user_id ON weekly_goals(user_id);
CREATE INDEX idx_weekly_goals_week_start ON weekly_goals(week_start_date);

-- ==================== ROW LEVEL SECURITY ====================
-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE meals ENABLE ROW LEVEL SECURITY;
ALTER TABLE food_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE water_intake ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_challenges ENABLE ROW LEVEL SECURITY;
ALTER TABLE weekly_goals ENABLE ROW LEVEL SECURITY;

-- Users table policies
CREATE POLICY "Users can view their own data"
  ON users FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own data"
  ON users FOR UPDATE
  USING (auth.uid() = user_id);

-- Health profiles policies
CREATE POLICY "Users can view their own health profile"
  ON health_profiles FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own health profile"
  ON health_profiles FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own health profile"
  ON health_profiles FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Meals policies
CREATE POLICY "Users can view their own meals"
  ON meals FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own meals"
  ON meals FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own meals"
  ON meals FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own meals"
  ON meals FOR DELETE
  USING (auth.uid() = user_id);

-- Food history policies
CREATE POLICY "Users can view their food history"
  ON food_history FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert food history"
  ON food_history FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update food history"
  ON food_history FOR UPDATE
  USING (auth.uid() = user_id);

-- Water intake policies
CREATE POLICY "Users can view their water intake"
  ON water_intake FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert water intake"
  ON water_intake FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update water intake"
  ON water_intake FOR UPDATE
  USING (auth.uid() = user_id);

-- Daily challenges policies
CREATE POLICY "Users can view their daily challenges"
  ON daily_challenges FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert daily challenges"
  ON daily_challenges FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update daily challenges"
  ON daily_challenges FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete daily challenges"
  ON daily_challenges FOR DELETE
  USING (auth.uid() = user_id);

-- Weekly goals policies
CREATE POLICY "Users can view their weekly goals"
  ON weekly_goals FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert weekly goals"
  ON weekly_goals FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update weekly goals"
  ON weekly_goals FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete weekly goals"
  ON weekly_goals FOR DELETE
  USING (auth.uid() = user_id);
