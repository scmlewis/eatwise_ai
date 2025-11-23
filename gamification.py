"""
Gamification Module for EatWise
Handles points, XP, challenges, and rewards
"""

from datetime import date, timedelta
from typing import List, Dict, Optional
import streamlit as st


class GamificationManager:
    """Manages gamification features: XP, challenges, goals"""
    
    # XP Rewards
    XP_REWARDS = {
        "meal_logged": 25,           # Base reward for logging a meal
        "nutrition_target_met": 50,  # Reward for hitting all targets
        "streak_3_days": 100,        # Bonus for 3-day streak
        "streak_7_days": 200,        # Bonus for 7-day streak
        "streak_30_days": 500,       # Bonus for 30-day streak
        "daily_challenge": 50,       # Per challenge completed
        "weekly_goal": 200,          # For completing weekly goal
    }
    
    # Challenge Templates
    CHALLENGE_TEMPLATES = [
        {
            "type": "meal_count",
            "name": "Meal Logger",
            "description": "Log 3 meals today",
            "target": 3,
            "xp_reward": 50,
        },
        {
            "type": "calorie_goal",
            "name": "Calorie Control",
            "description": "Stay under your calorie target",
            "target": 100,  # 100% of target
            "xp_reward": 50,
        },
        {
            "type": "protein_goal",
            "name": "Protein Power",
            "description": "Hit your protein target",
            "target": 100,  # 100% of target
            "xp_reward": 40,
        },
        {
            "type": "water_goal",
            "name": "Hydration Hero",
            "description": "Drink 8 glasses of water",
            "target": 8,
            "xp_reward": 30,
        },
    ]
    
    @staticmethod
    def calculate_daily_challenges(db_manager, user_id: str, profile: Dict) -> List[Dict]:
        """Generate daily challenges for a user based on their profile"""
        today = date.today()
        
        # Check if challenges already exist for today
        existing = db_manager.get_daily_challenges(user_id, today)
        if existing:
            return existing
        
        # Generate new challenges
        challenges = []
        for template in GamificationManager.CHALLENGE_TEMPLATES:
            challenges.append(template)
        
        # Create challenges in database
        db_manager.create_daily_challenges(user_id, today, challenges)
        
        return challenges
    
    @staticmethod
    def update_challenge_progress(db_manager, user_id: str, daily_nutrition: Dict, targets: Dict, water_intake: int) -> Dict[str, bool]:
        """
        Update progress on daily challenges
        Returns dict of challenge_name: completed status
        """
        today = date.today()
        challenges = db_manager.get_daily_challenges(user_id, today)
        completed_challenges = {}
        
        for challenge in challenges:
            challenge_type = challenge.get("challenge_type")
            target = challenge.get("target")
            
            # Meal count challenge
            if challenge_type == "meal_count":
                meal_count = len(db_manager.get_meals_by_date(user_id, today))
                current_progress = meal_count
                db_manager.update_challenge_progress(user_id, today, challenge.get("challenge_name"), current_progress)
                if meal_count >= target:
                    db_manager.complete_challenge(user_id, today, challenge.get("challenge_name"))
                    completed_challenges[challenge.get("challenge_name")] = True
                else:
                    completed_challenges[challenge.get("challenge_name")] = False
            
            # Calorie goal challenge
            elif challenge_type == "calorie_goal":
                calorie_pct = (daily_nutrition.get("calories", 0) / targets.get("calories", 2000)) * 100
                current_progress = min(int(calorie_pct), 100)
                db_manager.update_challenge_progress(user_id, today, challenge.get("challenge_name"), current_progress)
                if calorie_pct <= 100:  # At or under target
                    db_manager.complete_challenge(user_id, today, challenge.get("challenge_name"))
                    completed_challenges[challenge.get("challenge_name")] = True
                else:
                    completed_challenges[challenge.get("challenge_name")] = False
            
            # Protein goal challenge
            elif challenge_type == "protein_goal":
                protein_pct = (daily_nutrition.get("protein", 0) / targets.get("protein", 50)) * 100
                current_progress = int(protein_pct)
                db_manager.update_challenge_progress(user_id, today, challenge.get("challenge_name"), current_progress)
                if protein_pct >= 100:  # At or above target
                    db_manager.complete_challenge(user_id, today, challenge.get("challenge_name"))
                    completed_challenges[challenge.get("challenge_name")] = True
                else:
                    completed_challenges[challenge.get("challenge_name")] = False
            
            # Water goal challenge
            elif challenge_type == "water_goal":
                current_progress = water_intake
                db_manager.update_challenge_progress(user_id, today, challenge.get("challenge_name"), current_progress)
                if water_intake >= target:
                    db_manager.complete_challenge(user_id, today, challenge.get("challenge_name"))
                    completed_challenges[challenge.get("challenge_name")] = True
                else:
                    completed_challenges[challenge.get("challenge_name")] = False
        
        return completed_challenges
    
    @staticmethod
    def get_week_start_date(target_date: Optional[date] = None) -> date:
        """Get the start date (Monday) of the week"""
        if target_date is None:
            target_date = date.today()
        
        # Calculate days since Monday
        days_since_monday = target_date.weekday()  # Monday = 0
        week_start = target_date - timedelta(days=days_since_monday)
        return week_start
    
    @staticmethod
    def check_weekly_goal(db_manager, user_id: str) -> bool:
        """Check if weekly goal should be completed"""
        today = date.today()
        week_start = GamificationManager.get_week_start_date(today)
        
        # Create weekly goal if it doesn't exist
        db_manager.create_weekly_goals(user_id, week_start)
        
        weekly_goal = db_manager.get_weekly_goals(user_id, week_start)
        if weekly_goal:
            target = weekly_goal.get("target_days_with_nutrition_goals", 5)
            completed = weekly_goal.get("days_completed", 0)
            
            return completed >= target
        
        return False
    
    @staticmethod
    def render_xp_progress(user_level: int, current_xp: int, xp_needed: int) -> None:
        """Render XP progress bar"""
        xp_percentage = min((current_xp / xp_needed) * 100, 100)
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #10A19D20 0%, #52C4B840 100%);
            border: 1px solid #10A19D;
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 12px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="color: #e0f2f1; font-weight: 700;">🎮 Level {user_level}</span>
                <span style="color: #52C4B8; font-size: 12px; font-weight: 600;">{current_xp}/{xp_needed} XP</span>
            </div>
            <div style="background: #0a0e27; border-radius: 4px; height: 8px; overflow: hidden;">
                <div style="background: linear-gradient(90deg, #10A19D 0%, #52C4B8 100%); height: 100%; width: {xp_percentage}%; transition: width 0.3s ease;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_daily_challenges(challenges: List[Dict], completed: Dict[str, bool]) -> None:
        """Render daily challenges display in 2x2 grid"""
        st.markdown("### 🎯 Daily Challenges")
        
        # Create 2-column layout for 2x2 grid
        cols = st.columns(2, gap="medium")
        
        for idx, challenge in enumerate(challenges):
            name = challenge.get("challenge_name")
            description = challenge.get("description")
            current = challenge.get("current_progress", 0)
            target = challenge.get("target", 1)
            xp_reward = challenge.get("xp_reward", 0)
            is_completed = completed.get(name, False)
            
            # Calculate progress percentage
            progress_pct = min((current / target) * 100, 100) if target > 0 else 0
            
            # Determine color based on completion
            if is_completed:
                bg_color = "linear-gradient(135deg, #51CF6620 0%, #80C34240 100%)"
                border_color = "#51CF66"
                status_icon = "✅"
            elif progress_pct >= 75:
                bg_color = "linear-gradient(135deg, #FFD43B20 0%, #FCC41940 100%)"
                border_color = "#FFD43B"
                status_icon = "🔥"
            else:
                bg_color = "linear-gradient(135deg, #3B82F620 0%, #60A5FA40 100%)"
                border_color = "#3B82F6"
                status_icon = "📌"
            
            # Use column index to place in grid (2x2)
            with cols[idx % 2]:
                st.markdown(f"""
                <div style="
                    background: {bg_color};
                    border: 1px solid {border_color};
                    border-radius: 8px;
                    padding: 12px;
                    margin-bottom: 12px;
                    min-height: 130px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                ">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="color: #e0f2f1; font-weight: 600;">{status_icon} {name}</span>
                            <span style="color: {border_color}; font-size: 10px; font-weight: 700;">+{xp_reward} XP</span>
                        </div>
                        <div style="color: #a0a0a0; font-size: 11px; margin-bottom: 8px;">{description}</div>
                    </div>
                    <div>
                        <div style="background: #0a0e27; border-radius: 3px; height: 6px; overflow: hidden; margin-bottom: 6px;">
                            <div style="background: {border_color}; height: 100%; width: {progress_pct}%;"></div>
                        </div>
                        <div style="font-size: 9px; color: #a0a0a0; text-align: right;">{int(current)}/{target}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    @staticmethod
    def render_weekly_goals(weekly_goal: Optional[Dict]) -> None:
        """Render weekly goals display"""
        st.markdown("### 🎯 Weekly Goal")
        
        if not weekly_goal:
            st.info("Weekly goal not initialized. Log some meals to get started!")
            return
        
        target = weekly_goal.get("target_days_with_nutrition_goals", 5)
        completed = weekly_goal.get("days_completed", 0)
        is_complete = weekly_goal.get("completed", False)
        xp_reward = weekly_goal.get("xp_reward", 200)
        
        progress_pct = (completed / target) * 100 if target > 0 else 0
        
        if is_complete:
            bg_color = "linear-gradient(135deg, #51CF6620 0%, #80C34240 100%)"
            border_color = "#51CF66"
            status_icon = "🏆"
        else:
            bg_color = "linear-gradient(135deg, #FFD43B20 0%, #FCC41940 100%)"
            border_color = "#FFD43B"
            status_icon = "🎖️"
        
        st.markdown(f"""
        <div style="
            background: {bg_color};
            border: 2px solid {border_color};
            border-radius: 10px;
            padding: 14px;
            text-align: center;
        ">
            <div style="font-size: 24px; margin-bottom: 8px;">{status_icon}</div>
            <div style="color: #e0f2f1; font-weight: 700; margin-bottom: 4px;">Complete Nutrition Goals {target} Days</div>
            <div style="color: {border_color}; font-weight: 600; margin-bottom: 10px; font-size: 12px;">+{xp_reward} XP</div>
            <div style="background: #0a0e27; border-radius: 6px; height: 12px; overflow: hidden; margin-bottom: 8px;">
                <div style="background: linear-gradient(90deg, {border_color} 0%, {border_color} 100%); height: 100%; width: {progress_pct}%;"></div>
            </div>
            <div style="color: #a0a0a0; font-size: 13px; font-weight: 600;">{completed}/{target} days completed</div>
        </div>
        """, unsafe_allow_html=True)
