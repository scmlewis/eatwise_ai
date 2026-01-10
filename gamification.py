"""
Gamification Module for EatWise
Handles points, XP, challenges, and rewards
"""

from datetime import date, timedelta
from typing import List, Dict, Optional
import streamlit as st
from icons import (
    icon_zap, icon_trophy, icon_medal, icon_target, icon_fire,
    icon_check_circle, icon_star, icon_crown, icon_water,
    icon_flame, icon_protein, radial_progress
)


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
            "description": "Drink your daily water goal",
            "target": 8,  # Default, will be overridden by user's water_goal_glasses
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
            challenge = template.copy()  # Create a copy so we don't modify the template
            
            # Adapt Hydration Hero target to user's water goal
            if challenge.get("type") == "water_goal":
                user_water_goal = profile.get("water_goal_glasses", 8)
                challenge["target"] = int(user_water_goal)
                challenge["description"] = f"Drink {user_water_goal} glasses of water"
            
            challenges.append(challenge)
        
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
        
        # Get meal count for the day
        meal_count = len(db_manager.get_meals_by_date(user_id, today))
        
        for challenge in challenges:
            challenge_type = challenge.get("challenge_type")
            target = challenge.get("target")
            
            # Meal count challenge
            if challenge_type == "meal_count":
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
                # Must have logged at least one meal AND stay under or at target
                if meal_count > 0 and calorie_pct <= 100:
                    db_manager.complete_challenge(user_id, today, challenge.get("challenge_name"))
                    completed_challenges[challenge.get("challenge_name")] = True
                else:
                    completed_challenges[challenge.get("challenge_name")] = False
            
            # Protein goal challenge
            elif challenge_type == "protein_goal":
                protein_pct = (daily_nutrition.get("protein", 0) / targets.get("protein", 50)) * 100
                current_progress = int(protein_pct)
                db_manager.update_challenge_progress(user_id, today, challenge.get("challenge_name"), current_progress)
                # Must have logged at least one meal AND meet protein target
                if meal_count > 0 and protein_pct >= 100:
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
        """Render XP progress bar with SVG icons and animations"""
        xp_percentage = min((current_xp / xp_needed) * 100, 100)
        
        # Use SVG icons
        zap_icon = icon_zap(size="md", color="#FBBF24")
        star_icon = icon_star(size="sm", color="#FBBF24", filled=True)
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);
            border: 1px solid rgba(251, 191, 36, 0.3);
            border-radius: 16px;
            padding: 16px 20px;
            margin-bottom: 16px;
            position: relative;
            overflow: hidden;
        ">
            <div style="position: absolute; top: -20px; right: -20px; opacity: 0.1; font-size: 80px;">⚡</div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; position: relative; z-index: 1;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    {zap_icon}
                    <span style="color: #FBBF24; font-weight: 800; font-size: 18px;">Level {user_level}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 6px;">
                    {star_icon}
                    <span style="color: #F59E0B; font-size: 13px; font-weight: 600;">{current_xp} / {xp_needed} XP</span>
                </div>
            </div>
            <div style="background: rgba(0, 0, 0, 0.3); border-radius: 6px; height: 10px; overflow: hidden; box-shadow: inset 0 2px 4px rgba(0,0,0,0.3); position: relative; z-index: 1;">
                <div style="
                    background: linear-gradient(90deg, #FBBF24 0%, #F59E0B 50%, #D97706 100%);
                    height: 100%;
                    width: {xp_percentage}%;
                    border-radius: 6px;
                    transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
                    box-shadow: 0 0 12px rgba(251, 191, 36, 0.5);
                    position: relative;
                ">
                    <div style="
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
                        animation: shimmer 2s infinite;
                    "></div>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 8px; position: relative; z-index: 1;">
                <span style="font-size: 10px; color: #94A3B8;">Next level: {xp_needed - current_xp} XP needed</span>
                <span style="font-size: 10px; color: #F59E0B; font-weight: 600;">{xp_percentage:.0f}%</span>
            </div>
        </div>
        <style>
            @keyframes shimmer {{
                0% {{ transform: translateX(-100%); }}
                100% {{ transform: translateX(100%); }}
            }}
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_daily_challenges(challenges: List[Dict], completed: Dict[str, bool]) -> None:
        """Render daily challenges display with SVG icons in 1 row x 4 columns"""
        target_icon = icon_target(size="md", color="#10A19D")
        st.markdown(f"""
        <h3 style="color: white; display: flex; align-items: center; gap: 10px; margin-bottom: 16px;">
            {target_icon} Daily Challenges
        </h3>
        """, unsafe_allow_html=True)
        
        # Create 4 columns for the challenges
        cols = st.columns(4)
        
        # Challenge type to icon mapping
        challenge_icons = {
            "meal_count": icon_flame(size="sm", color="#FF6B35"),
            "calorie_goal": icon_flame(size="sm", color="#FF6B35"),
            "protein_goal": icon_protein(size="sm", color="#51CF66"),
            "water_goal": icon_water(size="sm", color="#3B82F6"),
        }
        
        for idx, challenge in enumerate(challenges):
            if idx >= 4:
                break
            
            with cols[idx]:
                name = challenge.get("challenge_name")
                description = challenge.get("description")
                current = challenge.get("current_progress", 0)
                target = challenge.get("target", 1)
                xp_reward = challenge.get("xp_reward", 0)
                challenge_type = challenge.get("challenge_type", "")
                is_completed = completed.get(name, False)
                
                # Get appropriate icon
                status_icon_html = challenge_icons.get(challenge_type, icon_target(size="sm", color="#3B82F6"))
                
                # Calculate progress percentage
                progress_pct = min((current / target) * 100, 100) if target > 0 else 0
                
                # Determine color based on completion
                if is_completed:
                    bg_color = "linear-gradient(135deg, rgba(81, 207, 102, 0.12) 0%, rgba(128, 195, 66, 0.06) 100%)"
                    border_color = "#51CF66"
                    status_badge = icon_check_circle(size="sm", color="#51CF66")
                elif progress_pct >= 75:
                    bg_color = "linear-gradient(135deg, rgba(255, 212, 59, 0.12) 0%, rgba(252, 196, 25, 0.06) 100%)"
                    border_color = "#FFD43B"
                    status_badge = icon_fire(size="sm", color="#FFD43B")
                else:
                    bg_color = "linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(96, 165, 250, 0.05) 100%)"
                    border_color = "#3B82F6"
                    status_badge = status_icon_html
                
                # XP badge with zap icon
                xp_icon = icon_zap(size="xs", color=border_color)
                
                st.markdown(f"""
                <div style="
                    background: {bg_color};
                    border: 1px solid {border_color};
                    border-radius: 12px;
                    padding: 14px;
                    min-height: 150px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                    cursor: pointer;
                " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 20px rgba(0,0,0,0.2)';" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; margin-bottom: 8px;">
                            <div style="display: flex; align-items: center; gap: 6px;">
                                {status_badge}
                                <span style="color: #e0f2f1; font-weight: 600; font-size: 12px;">{name}</span>
                            </div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 4px; margin-bottom: 8px;">
                            {xp_icon}
                            <span style="color: {border_color}; font-size: 10px; font-weight: 700;">+{xp_reward} XP</span>
                        </div>
                        <div style="color: #a0a0a0; font-size: 11px; line-height: 1.4;">{description}</div>
                    </div>
                    <div style="margin-top: 12px;">
                        <div style="background: rgba(0, 0, 0, 0.3); border-radius: 4px; height: 6px; overflow: hidden; margin-bottom: 6px;">
                            <div style="background: linear-gradient(90deg, {border_color} 0%, {border_color}80 100%); height: 100%; width: {progress_pct}%; transition: width 0.5s ease; border-radius: 4px;"></div>
                        </div>
                        <div style="font-size: 10px; color: #a0a0a0; text-align: right; font-weight: 500;">{int(current)}/{target}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    @staticmethod
    def render_weekly_goals(weekly_goal: Optional[Dict]) -> None:
        """Render weekly goals display with SVG icons"""
        medal_icon = icon_medal(size="md", color="#F59E0B")
        st.markdown(f"""
        <h3 style="color: white; display: flex; align-items: center; gap: 10px; margin-bottom: 16px;">
            {medal_icon} Weekly Goal
        </h3>
        """, unsafe_allow_html=True)
        
        if not weekly_goal:
            st.info("Weekly goal not initialized. Log some meals to get started!")
            return
        
        target = weekly_goal.get("target_days_with_nutrition_goals", 5)
        completed = weekly_goal.get("days_completed", 0)
        is_complete = weekly_goal.get("completed", False)
        xp_reward = weekly_goal.get("xp_reward", 200)
        
        progress_pct = (completed / target) * 100 if target > 0 else 0
        
        if is_complete:
            bg_color = "linear-gradient(135deg, rgba(81, 207, 102, 0.15) 0%, rgba(128, 195, 66, 0.08) 100%)"
            border_color = "#51CF66"
            status_icon = icon_trophy(size="xl", color="#FFD43B")
        else:
            bg_color = "linear-gradient(135deg, rgba(255, 212, 59, 0.12) 0%, rgba(252, 196, 25, 0.06) 100%)"
            border_color = "#FFD43B"
            status_icon = icon_crown(size="xl", color="#FFD43B")
        
        # XP icon
        xp_icon = icon_zap(size="sm", color=border_color)
        
        st.markdown(f"""
        <div style="
            background: {bg_color};
            border: 2px solid {border_color};
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            position: relative;
            overflow: hidden;
        ">
            <div style="position: absolute; top: -30px; right: -30px; opacity: 0.1; font-size: 100px;">🏆</div>
            <div style="margin-bottom: 12px; position: relative; z-index: 1;">{status_icon}</div>
            <div style="color: #e0f2f1; font-weight: 700; margin-bottom: 8px; font-size: 16px; position: relative; z-index: 1;">
                Complete Nutrition Goals {target} Days
            </div>
            <div style="display: flex; align-items: center; justify-content: center; gap: 6px; margin-bottom: 14px; position: relative; z-index: 1;">
                {xp_icon}
                <span style="color: {border_color}; font-weight: 700; font-size: 14px;">+{xp_reward} XP</span>
            </div>
            <div style="background: rgba(0, 0, 0, 0.3); border-radius: 8px; height: 14px; overflow: hidden; margin-bottom: 10px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.3); position: relative; z-index: 1;">
                <div style="
                    background: linear-gradient(90deg, {border_color} 0%, {border_color}80 100%);
                    height: 100%;
                    width: {progress_pct}%;
                    border-radius: 8px;
                    transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
                    box-shadow: 0 0 10px {border_color}80;
                "></div>
            </div>
            <div style="color: #a0a0a0; font-size: 14px; font-weight: 600; position: relative; z-index: 1;">
                {completed} / {target} days completed
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_streak_calendar(streak_days: List[date], current_streak: int) -> None:
        """
        Render a visual streak calendar showing logging history.
        
        Args:
            streak_days: List of dates when meals were logged
            current_streak: Current consecutive day streak
        """
        fire_icon = icon_fire(size="md", color="#FF6B35")
        
        # Get last 14 days
        today = date.today()
        days = [(today - timedelta(days=i)) for i in range(13, -1, -1)]
        
        # Build day boxes
        day_boxes = ""
        for d in days:
            is_logged = d in streak_days
            if is_logged:
                box_bg = "linear-gradient(135deg, #FF6B35 0%, #FF8C46 100%)"
                box_border = "#FF6B35"
                box_shadow = "0 0 8px rgba(255, 107, 53, 0.4)"
            else:
                box_bg = "rgba(255, 255, 255, 0.05)"
                box_border = "rgba(255, 255, 255, 0.1)"
                box_shadow = "none"
            
            day_boxes += f'''
            <div style="
                width: 32px;
                height: 32px;
                border-radius: 6px;
                background: {box_bg};
                border: 1px solid {box_border};
                box-shadow: {box_shadow};
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 10px;
                color: {'white' if is_logged else '#64748B'};
                font-weight: 600;
            ">{d.day}</div>
            '''
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(255, 107, 53, 0.1) 0%, rgba(255, 140, 70, 0.05) 100%);
            border: 1px solid rgba(255, 107, 53, 0.3);
            border-radius: 16px;
            padding: 16px;
        ">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                {fire_icon}
                <span style="color: #FF6B35; font-weight: 700; font-size: 14px;">{current_streak} Day Streak</span>
            </div>
            <div style="display: flex; gap: 6px; flex-wrap: wrap; justify-content: center;">
                {day_boxes}
            </div>
            <div style="text-align: center; margin-top: 10px; font-size: 11px; color: #94A3B8;">
                Last 14 days
            </div>
        </div>
        """, unsafe_allow_html=True)
