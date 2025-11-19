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
            self.supabase.table("health_profiles").insert(profile_data).execute()
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
            self.supabase.table("health_profiles").update(profile_data).eq("user_id", user_id).execute()
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
        """Log water intake"""
        try:
            if logged_date is None:
                logged_date = date.today()
            
            water_entry = {
                "user_id": user_id,
                "glasses": glasses,
                "logged_date": logged_date.isoformat(),
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
