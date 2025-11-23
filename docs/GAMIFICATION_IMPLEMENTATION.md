# Gamification Implementation Guide

## 📋 Overview

EatWise now includes a complete **gamification system** to boost user engagement and habit formation. This guide explains the three core features implemented:

1. **⭐ XP & Levels** - Users gain XP for logged meals and completing challenges
2. **🎯 Daily Challenges** - 4 rotating daily challenges to encourage consistent logging
3. **🎖️ Weekly Goals** - Complete 5 days of nutrition goals to earn bonus XP

## 🎮 Features Implemented

### ⭐ XP & Leveling System

**How It Works:**
- Users start at Level 1 with 0 XP
- 100 XP = 1 level progression
- XP is awarded for various actions

**XP Reward Structure:**
- **Meal Logged**: +25 XP (every logged meal)
- **Nutrition Target Met**: +50 XP (hitting all targets for a day)
- **Daily Challenge Completed**: +50 XP (per challenge)
- **Weekly Goal Completed**: +200 XP (after 5 days)
- **3-Day Streak**: +100 XP
- **7-Day Streak**: +200 XP
- **30-Day Streak**: +500 XP

**Display:**
- Level and XP progress shown on dashboard (⭐ Experience & Level section)
- Visual progress bar showing XP toward next level
- Current XP / XP needed displayed

### 🎯 Daily Challenges

**Available Challenges:**

1. **Meal Logger** - Log 3 meals today
   - Target: 3 meals
   - Reward: +50 XP
   - Progress: Updates as meals are logged

2. **Calorie Control** - Stay under your calorie target
   - Target: 100% of daily calorie allowance
   - Reward: +50 XP
   - Progress: Calculates from logged meals

3. **Protein Power** - Hit your protein target
   - Target: 100% of daily protein goal
   - Reward: +40 XP
   - Progress: Calculates from meal nutrition data

4. **Hydration Hero** - Drink 8 glasses of water
   - Target: 8 glasses
   - Reward: +30 XP
   - Progress: Updates from water tracking

**How It Works:**
- New challenges generated daily at first login
- Progress automatically updates as user logs meals/water
- Completed challenges marked with ✅ and turn green
- In-progress challenges show 🔥 emoji when 75%+ complete
- Not started challenges show 📌 emoji

**Display:**
- 🎯 Daily Challenges section on dashboard
- Shows progress bars, completion status, and XP reward for each
- Visual status indicators (colors change based on progress)

### 🎖️ Weekly Goals

**How It Works:**
- Goal: Complete nutrition logging for 5 days in a week
- Automatically created every Monday
- Tracks days with complete nutrition data
- Completing all 5 days awards +200 XP

**Progress Tracking:**
- Visual progress bar showing days completed
- Trophy emoji (🏆) when goal is completed
- Shows target (5 days) vs actual days completed
- XP reward clearly displayed

**Display:**
- 🎯 Weekly Goal section on dashboard
- Large trophy icon when completed
- Goal progress bar with clear target

## 🗄️ Database Schema

### Tables Required

**daily_challenges**
```sql
id, user_id, challenge_date, challenge_type, challenge_name,
description, target, current_progress, xp_reward, completed,
created_at, updated_at
```

**weekly_goals**
```sql
id, user_id, week_start_date, target_days_with_nutrition_goals,
days_completed, completed, xp_reward, created_at, updated_at
```

**water_intake** (already created)
```sql
id, user_id, water_date, glasses_count, created_at, updated_at
```

**health_profiles** (updated columns)
```sql
total_xp (INTEGER DEFAULT 0)
timezone (VARCHAR(50) DEFAULT 'UTC')
```

## 🚀 Setup Instructions

### Step 1: Apply Database Migration

1. Open your Supabase dashboard
2. Go to **SQL Editor**
3. Create a new query
4. Copy the contents of `scripts/gamification_migration.sql`
5. Paste and run the migration

**What it does:**
- Creates `daily_challenges` table
- Creates `weekly_goals` table
- Creates `water_intake` table (if missing)
- Adds `total_xp` and `timezone` columns to `health_profiles`
- Sets up Row Level Security policies
- Creates indexes for performance

### Step 2: Verify Integration

The following files have already been updated:

**app.py:**
- ✅ GamificationManager imported
- ✅ Dashboard displays XP level, daily challenges, weekly goals
- ✅ XP awarded when meals logged (all tabs)
- ✅ Toast notifications show "+25 XP" when meals added

**gamification.py:** (New file)
- ✅ GamificationManager class with all logic
- ✅ Challenge templates defined
- ✅ Progress calculation methods
- ✅ UI rendering components

**database.py:** (Extended)
- ✅ `add_xp(user_id, amount)` - Award XP
- ✅ `get_user_level(user_id)` - Get current level
- ✅ `get_user_xp_progress(user_id)` - Get XP details
- ✅ `get_daily_challenges(user_id, date)` - Retrieve challenges
- ✅ `create_daily_challenges(user_id, date, challenges)` - Create challenges
- ✅ `update_challenge_progress(user_id, date, name, progress)` - Update progress
- ✅ `complete_challenge(user_id, date, name)` - Mark complete
- ✅ `create_weekly_goals(user_id, week_start)` - Create goals
- ✅ `get_weekly_goals(user_id, week_start)` - Retrieve goals
- ✅ `increment_weekly_days_completed(user_id, week_start)` - Track days

## 📊 How Gamification Flows

### User Journey - Day 1

1. **First Login** → Dashboard loads
2. **Dashboard Renders**:
   - XP Level: 1 (0/100 XP)
   - Daily Challenges: All 4 challenges created and displayed
   - Weekly Goal: Created (0/5 days)
3. **User Logs Breakfast** → +25 XP (now 1/1 meal logged)
4. **Meal Logger Challenge** → Updates to show 1/3 meals complete
5. **User Logs Lunch** → +25 XP (now 2/2 meals logged)
6. **Meal Logger Challenge** → Updates to show 2/3 meals complete
7. **User Logs Dinner** → +25 XP (now 3/3 meals logged)
8. **Meal Logger Challenge** → Completes! ✅ +50 XP
9. **User Level Up?** → If total XP ≥ 100, becomes Level 2
10. **End of Day Summary** → All progress saved

### Challenge Progress Calculation

**Meal Logger Challenge:**
```
Progress = Number of meals logged today
Completed when: meals_logged >= 3
```

**Calorie Control Challenge:**
```
Progress = (Total calories / Daily calorie target) * 100
Completed when: progress <= 100% (at or under target)
```

**Protein Power Challenge:**
```
Progress = (Total protein / Daily protein goal) * 100
Completed when: progress >= 100% (hit target or above)
```

**Hydration Hero Challenge:**
```
Progress = Glasses of water logged
Completed when: water_intake >= 8 glasses
```

### Weekly Goal Tracking

**What counts as a "day with nutrition goals":**
- Day must have nutrition data logged (meals)
- Database tracks this via meals table

**Completion:**
- Track days that have meals logged
- When count reaches 5, mark goal as completed
- Award +200 XP automatically

## 🎨 UI Components

### Dashboard Layout (Updated)

```
Dashboard
├── 📍 User Profile / Date
├── 🔥 Nutrition Summary
├── 📊 Streak Cards (calories, protein, hydration)
├── ⭐ Experience & Level          [NEW]
│   └── Level indicator + XP progress bar
├── 🎯 Daily Challenges            [NEW]
│   ├── Challenge 1 (Meal Logger)
│   ├── Challenge 2 (Calorie Control)
│   ├── Challenge 3 (Protein Power)
│   └── Challenge 4 (Hydration Hero)
├── 🎖️ Weekly Goal                 [NEW]
│   └── Progress toward 5-day goal
├── 💧 Water Tracker
├── 🎖️ Earned Badges
└── ... rest of dashboard
```

### Visual Design

**Colors:**
- **Teal (#10A19D)** - Active/healthy state
- **Green (#51CF66)** - Completed challenges
- **Yellow (#FFD43B)** - In progress (75%+)
- **Blue (#3B82F6)** - Not started

**Icons:**
- ⭐ XP/Level
- 🎯 Daily challenges
- 🎖️ Weekly goals
- ✅ Completed
- 🔥 Hot (75%+ progress)
- 📌 Not started
- 🏆 Achievement/Weekly goal complete

## 🔧 Code Integration Points

### 1. XP Rewards (app.py)

**Quick Add from History:**
```python
if db_manager.log_meal(meal_data):
    db_manager.add_xp(st.session_state.user_id, GamificationManager.XP_REWARDS['meal_logged'])
    st.toast("Meal added! +25 XP", icon="✅")
```

**Text Description:**
```python
if db_manager.log_meal(meal_data):
    db_manager.add_xp(st.session_state.user_id, GamificationManager.XP_REWARDS['meal_logged'])
    st.toast("Meal saved! +25 XP", icon="✅")
```

**Photo Upload:**
```python
if db_manager.log_meal(meal_data):
    db_manager.add_xp(st.session_state.user_id, GamificationManager.XP_REWARDS['meal_logged'])
    st.toast("Meal saved! +25 XP", icon="✅")
```

**Batch Log:**
```python
if db_manager.log_meal(meal_data):
    db_manager.add_xp(st.session_state.user_id, GamificationManager.XP_REWARDS['meal_logged'])
    total_saved += 1
```

### 2. Dashboard Display (app.py)

```python
# Display XP Level
user_level = db_manager.get_user_level(st.session_state.user_id)
xp_progress = db_manager.get_user_xp_progress(st.session_state.user_id)
GamificationManager.render_xp_progress(
    user_level,
    xp_progress.get("current_xp", 0),
    xp_progress.get("xp_needed", 100)
)

# Display Daily Challenges
daily_challenges = GamificationManager.calculate_daily_challenges(db_manager, st.session_state.user_id, user_profile)
daily_nutrition = db_manager.get_daily_nutrition_summary(st.session_state.user_id, today)
water_intake = db_manager.get_daily_water_intake(st.session_state.user_id, today)

completed_challenges = GamificationManager.update_challenge_progress(
    db_manager, st.session_state.user_id, daily_nutrition, targets, water_intake
)

GamificationManager.render_daily_challenges(daily_challenges, completed_challenges)

# Display Weekly Goals
week_start = GamificationManager.get_week_start_date(today)
db_manager.create_weekly_goals(st.session_state.user_id, week_start)
weekly_goal = db_manager.get_weekly_goals(st.session_state.user_id, week_start)
GamificationManager.render_weekly_goals(weekly_goal)
```

## 📈 Metrics & Analytics

### User Engagement Metrics

**Trackable:**
- Daily active users completing challenges
- Average XP earned per user per day
- Challenge completion rates
- Weekly goal completion rate
- Meal logging frequency
- Water intake tracking

**Recommended Analytics:**
- Track daily challenges completion % (expect 40-60% initially)
- Monitor XP growth patterns (should show consistent progression)
- Weekly goal completion helps with habit formation

## 🐛 Troubleshooting

### Issue: Challenges not appearing on dashboard

**Solution:**
1. Verify `daily_challenges` table exists: `SELECT * FROM daily_challenges LIMIT 1;`
2. Check that migration was applied completely
3. Verify user has meals logged for the day
4. Check app.py dashboard_page() has the render calls

### Issue: XP not being awarded

**Solution:**
1. Verify `health_profiles.total_xp` column exists
2. Check that `db_manager.add_xp()` is being called (should see "+25 XP" toast)
3. Verify database connection is working
4. Check Supabase RLS policies allow updates to health_profiles

### Issue: Weekly goal not tracking days

**Solution:**
1. Ensure meals are logged with complete nutrition data
2. Check `weekly_goals` table exists in Supabase
3. Verify `db_manager.create_weekly_goals()` is called on dashboard
4. Check that `challenge_date` in challenges matches today's date

## 🎯 Future Enhancements

Potential features to add:
- **Streaks**: Track consecutive days of meal logging
- **Badges & Achievements**: Unlock special badges
- **Leaderboards**: Social competition (optional)
- **Notifications**: Remind users about incomplete challenges
- **Seasonal Events**: Special seasonal challenges
- **XP Multipliers**: Weekend or holiday bonuses
- **Challenge Customization**: Let users choose challenges
- **AI Coaching**: Recommendations based on challenges

## 📚 File Reference

**Modified Files:**
- `app.py` - Dashboard integration, XP rewards on meal logging
- `database.py` - Added 10+ gamification methods
- `gamification.py` - NEW: Core gamification logic

**New Files:**
- `scripts/gamification_migration.sql` - Database setup
- `docs/GAMIFICATION_IMPLEMENTATION.md` - This guide

**Documentation:**
- `scripts/README.md` - Updated with migration instructions
- `PRESENTATION_OUTLINE.md` - Updated with gamification slides

## ✅ Implementation Checklist

- [x] Database tables created (daily_challenges, weekly_goals)
- [x] GamificationManager class implemented
- [x] XP reward system integrated
- [x] Dashboard displays XP level
- [x] Dashboard displays daily challenges
- [x] Dashboard displays weekly goals
- [x] XP awarded when meals logged
- [x] Challenge progress calculated automatically
- [x] Toast notifications show XP gained
- [x] All code committed and pushed to GitHub
- [ ] Gamification migration applied to Supabase (⚠️ MANUAL STEP REQUIRED)
- [ ] Testing in production environment
- [ ] User feedback collection

---

**Last Updated**: November 20, 2025  
**Status**: ✅ Complete - Ready for deployment

For questions or issues, refer to the troubleshooting section or check the GitHub issues page.
