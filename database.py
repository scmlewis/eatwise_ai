"""Database module for EatWise"""
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import streamlit as st


class DatabaseManager:
    """Handles all database operations with Supabase"""
    
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # ==================== HEALTH PROFILE ====================
    
    def create_health_profile(self, user_id: str, profile_data: Dict) -> bool:
        """Create user health profile"""
        try:
            profile_data["user_id"] = user_id
            
            # Filter out fields that don't exist in the schema
            valid_fields = {
                "user_id", "full_name", "age_group", "gender", "timezone", 
                "health_conditions", "dietary_preferences", "health_goal"
            }
            
            filtered_data = {k: v for k, v in profile_data.items() if k in valid_fields}
            
            self.supabase.table("health_profiles").insert(filtered_data).execute()
            return True
        except Exception as e:
            st.error(f"Error creating health profile: {str(e)}")
            return False
    
    def get_health_profile(self, user_id: str) -> Optional[Dict]:
        """Get user health profile"""
        try:
            response = self.supabase.table("health_profiles").select("*").eq("user_id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error fetching health profile: {str(e)}")
            return None
    
    def update_health_profile(self, user_id: str, profile_data: Dict) -> bool:
        """Update user health profile"""
        try:
            # Filter out fields that don't exist in the schema
            # Only update fields that are known to exist in health_profiles table
            valid_fields = {
                "full_name", "age_group", "gender", "timezone", 
                "health_conditions", "dietary_preferences", "health_goal"
            }
            
            filtered_data = {k: v for k, v in profile_data.items() if k in valid_fields}
            
            if not filtered_data:
                st.error("No valid profile fields to update")
                return False
            
            self.supabase.table("health_profiles").update(filtered_data).eq("user_id", user_id).execute()
            return True
        except Exception as e:
            st.error(f"Error updating health profile: {str(e)}")
            return False
    
    # ==================== MEAL LOGGING ====================
    
    def log_meal(self, meal_data: Dict) -> bool:
        """Log a new meal and add to food history"""
        try:
            # Don't override logged_at - it's set by the app with the user's selected date
            # Only set it if not already provided
            if "logged_at" not in meal_data:
                meal_data["logged_at"] = datetime.now().isoformat()
            
            # Debug: Verify user_id is present
            if not meal_data.get("user_id"):
                st.error("Error: User ID is missing. Please log in again.")
                return False
            
            result = self.supabase.table("meals").insert(meal_data).execute()
            
            if result.data:
                # Also save to food_history
                food_history_entry = {
                    "user_id": meal_data.get("user_id"),
                    "food_name": meal_data.get("meal_name", "Unknown"),
                    "last_used": datetime.now().isoformat(),
                }
                
                try:
                    self.supabase.table("food_history").insert(food_history_entry).execute()
                except Exception as e:
                    # Food history save failed but meal saved, log warning but don't fail
                    print(f"Warning: Food history save failed: {e}")
                
                st.success("Meal saved successfully!")
                return True
            else:
                st.error("Failed to save meal. No response from server.")
                return False
                
        except Exception as e:
            error_msg = str(e)
            st.error(f"Error logging meal: {error_msg}")
            
            # Check for common issues
            if "user_id" in error_msg.lower():
                st.error("User not found in database. Please log in again.")
            elif "row level security" in error_msg.lower():
                st.error("Permission denied. Check your authentication.")
            
            return False
    
    def get_meals_by_date(self, user_id: str, meal_date: date) -> List[Dict]:
        """Get meals for a specific date"""
        try:
            date_str = meal_date.isoformat()
            # Use lte for the end time to include meals up to 23:59:59
            response = self.supabase.table("meals").select("*").eq("user_id", user_id).gte("logged_at", f"{date_str}T00:00:00").lte("logged_at", f"{date_str}T23:59:59").execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"Error fetching meals: {str(e)}")
            return []
    
    def get_meals_in_range(self, user_id: str, start_date: date, end_date: date) -> List[Dict]:
        """Get meals within a date range"""
        try:
            start_str = start_date.isoformat()
            end_str = end_date.isoformat()
            response = self.supabase.table("meals").select("*").eq("user_id", user_id).gte("logged_at", f"{start_str}T00:00:00").lte("logged_at", f"{end_str}T23:59:59").order("logged_at", desc=False).execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"Error fetching meals: {str(e)}")
            return []
    
    def get_recent_meals(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent meals"""
        try:
            response = self.supabase.table("meals").select("*").eq("user_id", user_id).order("logged_at", desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"Error fetching recent meals: {str(e)}")
            return []
    
    def update_meal(self, meal_id: str, meal_data: Dict) -> bool:
        """Update meal record"""
        try:
            self.supabase.table("meals").update(meal_data).eq("id", meal_id).execute()
            return True
        except Exception as e:
            st.error(f"Error updating meal: {str(e)}")
            return False
    
    def delete_meal(self, meal_id: str) -> bool:
        """Delete meal record"""
        try:
            self.supabase.table("meals").delete().eq("id", meal_id).execute()
            return True
        except Exception as e:
            st.error(f"Error deleting meal: {str(e)}")
            return False
    
    # ==================== MEAL HISTORY & TRENDS ====================
    
    def get_daily_nutrition_summary(self, user_id: str, meal_date: date) -> Dict[str, float]:
        """Calculate daily nutrition summary"""
        meals = self.get_meals_by_date(user_id, meal_date)
        
        summary = {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "sodium": 0,
            "sugar": 0,
            "fiber": 0,
        }
        
        for meal in meals:
            nutrition = meal.get("nutrition", {})
            summary["calories"] += nutrition.get("calories", 0)
            summary["protein"] += nutrition.get("protein", 0)
            summary["carbs"] += nutrition.get("carbs", 0)
            summary["fat"] += nutrition.get("fat", 0)
            summary["sodium"] += nutrition.get("sodium", 0)
            summary["sugar"] += nutrition.get("sugar", 0)
            summary["fiber"] += nutrition.get("fiber", 0)
        
        return summary
    
    def get_weekly_nutrition_summary(self, user_id: str, end_date: date) -> Dict:
        """Calculate weekly nutrition summary"""
        from datetime import timedelta
        
        start_date = end_date - timedelta(days=6)
        meals = self.get_meals_in_range(user_id, start_date, end_date)
        
        weekly_summary = {}
        for meal in meals:
            meal_date = meal.get("logged_at").split("T")[0]
            
            if meal_date not in weekly_summary:
                weekly_summary[meal_date] = {
                    "calories": 0,
                    "protein": 0,
                    "carbs": 0,
                    "fat": 0,
                    "sodium": 0,
                    "sugar": 0,
                    "fiber": 0,
                    "meal_count": 0,
                }
            
            nutrition = meal.get("nutrition", {})
            weekly_summary[meal_date]["calories"] += nutrition.get("calories", 0)
            weekly_summary[meal_date]["protein"] += nutrition.get("protein", 0)
            weekly_summary[meal_date]["carbs"] += nutrition.get("carbs", 0)
            weekly_summary[meal_date]["fat"] += nutrition.get("fat", 0)
            weekly_summary[meal_date]["sodium"] += nutrition.get("sodium", 0)
            weekly_summary[meal_date]["sugar"] += nutrition.get("sugar", 0)
            weekly_summary[meal_date]["fiber"] += nutrition.get("fiber", 0)
            weekly_summary[meal_date]["meal_count"] += 1
        
        return weekly_summary
    
    # ==================== BADGES & GAMIFICATION ====================
    
    def update_badges(self, user_id: str, badges: List[str]) -> bool:
        """Update user badges"""
        try:
            self.supabase.table("health_profiles").update({"badges_earned": badges}).eq("user_id", user_id).execute()
            return True
        except Exception as e:
            st.error(f"Error updating badges: {str(e)}")
            return False
    
    def add_badge(self, user_id: str, badge_id: str) -> bool:
        """Add a badge to user"""
        profile = self.get_health_profile(user_id)
        if profile:
            badges = profile.get("badges_earned", [])
            if badge_id not in badges:
                badges.append(badge_id)
                return self.update_badges(user_id, badges)
        return False
    
    # ==================== PREFERENCES & HISTORY ====================
    
    def save_food_history(self, user_id: str, food_item: Dict) -> bool:
        """Save food item to user history for quick access"""
        try:
            food_item["user_id"] = user_id
            self.supabase.table("food_history").insert(food_item).execute()
            return True
        except Exception as e:
            st.error(f"Error saving food history: {str(e)}")
            return False
    
    def get_food_history(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get user's food history"""
        try:
            response = self.supabase.table("food_history").select("*").eq("user_id", user_id).order("last_used", desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            st.error(f"Error fetching food history: {str(e)}")
            return []
    
    # ==================== WATER TRACKING ====================
    
    def log_water(self, user_id: str, glasses: int = 1, logged_date: Optional[date] = None) -> bool:
        """Log water intake - updates existing entry for the day or creates new one"""
        try:
            if logged_date is None:
                logged_date = date.today()
            
            date_str = logged_date.isoformat()
            
            # Check if entry exists for this date
            response = self.supabase.table("water_intake").select("id, glasses").eq("user_id", user_id).eq("logged_date", date_str).execute()
            
            if response.data:
                # Update existing entry
                existing_glasses = response.data[0].get("glasses", 0)
                new_total = existing_glasses + glasses
                self.supabase.table("water_intake").update({"glasses": new_total}).eq("user_id", user_id).eq("logged_date", date_str).execute()
            else:
                # Insert new entry
                water_entry = {
                    "user_id": user_id,
                    "glasses": max(0, glasses),  # Ensure non-negative
                    "logged_date": date_str,
                }
                self.supabase.table("water_intake").insert(water_entry).execute()
            return True
        except Exception as e:
            st.error(f"Error logging water: {str(e)}")
            return False
    
    def get_daily_water_intake(self, user_id: str, water_date: date) -> int:
        """Get total water intake for a specific date"""
        try:
            date_str = water_date.isoformat()
            response = self.supabase.table("water_intake").select("glasses").eq("user_id", user_id).eq("logged_date", date_str).execute()
            
            total_glasses = 0
            if response.data:
                for entry in response.data:
                    total_glasses += entry.get("glasses", 0)
            return total_glasses
        except Exception as e:
            print(f"Error fetching water intake: {str(e)}")
            return 0
    
    # ==================== GAMIFICATION: XP & POINTS ====================
    
    def add_xp(self, user_id: str, xp_amount: int) -> bool:
        """Add XP to user"""
        try:
            profile = self.get_health_profile(user_id)
            if profile:
                current_xp = profile.get("total_xp", 0)
                new_xp = current_xp + xp_amount
                self.supabase.table("health_profiles").update({"total_xp": new_xp}).eq("user_id", user_id).execute()
                return True
        except Exception as e:
            print(f"Error adding XP: {str(e)}")
            return False
    
    def get_user_level(self, user_id: str) -> int:
        """Calculate user level based on XP (1 level per 100 XP)"""
        profile = self.get_health_profile(user_id)
        if profile:
            total_xp = profile.get("total_xp", 0)
            return max(1, total_xp // 100)
        return 1
    
    def get_user_xp_progress(self, user_id: str) -> Dict[str, int]:
        """Get XP progress towards next level"""
        profile = self.get_health_profile(user_id)
        if profile:
            total_xp = profile.get("total_xp", 0)
            current_level = max(1, total_xp // 100)
            xp_for_next_level = (current_level * 100) + 100
            current_xp_in_level = total_xp % 100
            
            return {
                "current_level": current_level,
                "current_xp": current_xp_in_level,
                "xp_needed": 100,
                "total_xp": total_xp,
            }
        return {"current_level": 1, "current_xp": 0, "xp_needed": 100, "total_xp": 0}
    
    # ==================== GAMIFICATION: DAILY CHALLENGES ====================
    
    def get_daily_challenges(self, user_id: str, challenge_date: date) -> List[Dict]:
        """Get daily challenges for a user"""
        try:
            date_str = challenge_date.isoformat()
            response = self.supabase.table("daily_challenges").select("*").eq("user_id", user_id).eq("challenge_date", date_str).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error fetching daily challenges: {str(e)}")
            return []
    
    def create_daily_challenges(self, user_id: str, challenge_date: date, challenges: List[Dict]) -> bool:
        """Create daily challenges for a user"""
        try:
            date_str = challenge_date.isoformat()
            
            # Delete existing challenges for this date
            self.supabase.table("daily_challenges").delete().eq("user_id", user_id).eq("challenge_date", date_str).execute()
            
            # Insert new challenges
            for challenge in challenges:
                challenge_data = {
                    "user_id": user_id,
                    "challenge_date": date_str,
                    "challenge_type": challenge.get("type"),
                    "challenge_name": challenge.get("name"),
                    "description": challenge.get("description"),
                    "target": challenge.get("target"),
                    "current_progress": 0,
                    "completed": False,
                    "xp_reward": challenge.get("xp_reward", 50),
                }
                self.supabase.table("daily_challenges").insert(challenge_data).execute()
            
            return True
        except Exception as e:
            print(f"Error creating daily challenges: {str(e)}")
            return False
    
    def update_challenge_progress(self, user_id: str, challenge_date: date, challenge_name: str, progress: int) -> bool:
        """Update progress on a daily challenge"""
        try:
            date_str = challenge_date.isoformat()
            self.supabase.table("daily_challenges").update({"current_progress": progress}).eq("user_id", user_id).eq("challenge_date", date_str).eq("challenge_name", challenge_name).execute()
            return True
        except Exception as e:
            print(f"Error updating challenge progress: {str(e)}")
            return False
    
    def complete_challenge(self, user_id: str, challenge_date: date, challenge_name: str) -> bool:
        """Mark challenge as completed"""
        try:
            date_str = challenge_date.isoformat()
            self.supabase.table("daily_challenges").update({"completed": True}).eq("user_id", user_id).eq("challenge_date", date_str).eq("challenge_name", challenge_name).execute()
            
            # Award XP
            challenge_data = self.supabase.table("daily_challenges").select("xp_reward").eq("user_id", user_id).eq("challenge_date", date_str).eq("challenge_name", challenge_name).execute()
            if challenge_data.data:
                xp_reward = challenge_data.data[0].get("xp_reward", 50)
                self.add_xp(user_id, xp_reward)
            
            return True
        except Exception as e:
            print(f"Error completing challenge: {str(e)}")
            return False
    
    # ==================== GAMIFICATION: WEEKLY GOALS ====================
    
    def get_weekly_goals(self, user_id: str, week_start_date: date) -> Optional[Dict]:
        """Get weekly goals for a user"""
        try:
            date_str = week_start_date.isoformat()
            response = self.supabase.table("weekly_goals").select("*").eq("user_id", user_id).eq("week_start_date", date_str).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching weekly goals: {str(e)}")
            return None
    
    def create_weekly_goals(self, user_id: str, week_start_date: date) -> bool:
        """Create weekly goals for a user"""
        try:
            date_str = week_start_date.isoformat()
            
            # Check if already exists
            existing = self.get_weekly_goals(user_id, week_start_date)
            if existing:
                return True  # Already created
            
            weekly_goal = {
                "user_id": user_id,
                "week_start_date": date_str,
                "target_days_with_nutrition_goals": 5,  # 5 out of 7 days
                "days_completed": 0,
                "completed": False,
                "xp_reward": 200,
            }
            self.supabase.table("weekly_goals").insert(weekly_goal).execute()
            return True
        except Exception as e:
            print(f"Error creating weekly goals: {str(e)}")
            return False
    
    def increment_weekly_days_completed(self, user_id: str, week_start_date: date) -> bool:
        """Increment days completed towards weekly goal"""
        try:
            date_str = week_start_date.isoformat()
            goal = self.get_weekly_goals(user_id, week_start_date)
            
            if goal:
                new_days = goal.get("days_completed", 0) + 1
                target = goal.get("target_days_with_nutrition_goals", 5)
                completed = new_days >= target
                
                self.supabase.table("weekly_goals").update({
                    "days_completed": new_days,
                    "completed": completed
                }).eq("user_id", user_id).eq("week_start_date", date_str).execute()
                
                # Award XP if completed
                if completed:
                    self.add_xp(user_id, goal.get("xp_reward", 200))
                
                return True
        except Exception as e:
            print(f"Error updating weekly goal: {str(e)}")
            return False
