"""Utility functions for EatWise"""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import streamlit as st
import pytz


def get_greeting(timezone_str: str = "UTC") -> str:
    """
    Get time-based greeting based on user's timezone.
    
    Remarks on UTC vs GMT:
    - UTC (Coordinated Universal Time): The primary time standard used internationally.
      It's a continuous time scale maintained by atomic clocks and leap seconds.
      UTC does NOT observe daylight saving time.
    - GMT (Greenwich Mean Time): The solar time at the Prime Meridian (0° longitude).
      GMT is effectively equivalent to UTC but is a solar-based time, not atomic-based.
      GMT is also known as Zulu time in military contexts (UTC±0).
    
    For practical purposes: UTC and GMT are equivalent (UTC±0 / GMT±0).
    Pytz uses IANA timezone names (e.g., 'UTC', 'America/New_York', 'Europe/London').
    Users can select any IANA timezone, and the greeting will reflect their local time.
    """
    try:
        tz = pytz.timezone(timezone_str)
        user_time = datetime.now(tz)
        hour = user_time.hour
    except (pytz.exceptions.UnknownTimeZoneError, AttributeError):
        # Fallback to UTC if timezone is invalid
        # UTC (UTC±0) is used as the default when user's timezone cannot be resolved
        hour = datetime.now(pytz.UTC).hour
    
    if hour < 12:
        return "🌅 Good Morning"
    elif hour < 18:
        return "👋 Good Afternoon"
    else:
        return "🌙 Good Evening"


def calculate_nutrition_percentage(current: float, target: float) -> float:
    """Calculate percentage of nutrition target achieved"""
    if target == 0:
        return 0
    return min((current / target) * 100, 200)  # Cap at 200%


def get_nutrition_status(current: float, target: float, tolerance: float = 0.1) -> str:
    """Get status badge for nutrition metric"""
    percentage = calculate_nutrition_percentage(current, target)
    
    if percentage >= 90 and percentage <= 110:
        return "✅ On Target"
    elif percentage < 90:
        return f"⬆️ Under ({percentage:.0f}%)"
    else:
        return f"⬇️ Over ({percentage:.0f}%)"


def format_nutrition_dict(nutrition: Dict[str, float]) -> Dict[str, str]:
    """Format nutrition values with units"""
    return {
        "Calories": f"{nutrition.get('calories', 0):.0f} kcal",
        "Protein": f"{nutrition.get('protein', 0):.1f}g",
        "Carbs": f"{nutrition.get('carbs', 0):.1f}g",
        "Fat": f"{nutrition.get('fat', 0):.1f}g",
        "Sodium": f"{nutrition.get('sodium', 0):.0f}mg",
        "Sugar": f"{nutrition.get('sugar', 0):.1f}g",
        "Fiber": f"{nutrition.get('fiber', 0):.1f}g",
    }





def init_session_state():
    """Initialize session state variables"""
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"
    if "meal_cache" not in st.session_state:
        st.session_state.meal_cache = {}





def get_streak_info(meal_dates: List[datetime]) -> Dict[str, int]:
    """Calculate current streak and longest streak"""
    if not meal_dates:
        return {"current_streak": 0, "longest_streak": 0}
    
    sorted_dates = sorted(set([d.date() if isinstance(d, datetime) else d for d in meal_dates]))
    current_streak = 0
    longest_streak = 0
    temp_streak = 1
    
    for i in range(len(sorted_dates) - 1, -1, -1):
        if i == len(sorted_dates) - 1:
            # Check if today or yesterday has a meal
            if sorted_dates[i] >= datetime.now().date() - timedelta(days=1):
                current_streak = 1
            temp_streak = 1
        else:
            if (sorted_dates[i] - sorted_dates[i + 1]).days == -1:
                temp_streak += 1
                if i == len(sorted_dates) - 1 or (sorted_dates[i + 1] >= datetime.now().date() - timedelta(days=1)):
                    current_streak = temp_streak
                longest_streak = max(longest_streak, temp_streak)
            else:
                longest_streak = max(longest_streak, temp_streak)
                temp_streak = 1
    
    return {"current_streak": current_streak, "longest_streak": longest_streak}


def get_earned_badges(badges_earned: List[str]) -> Dict[str, Any]:
    """Get details of earned badges"""
    from constants import BADGES
    return {badge_id: BADGES.get(badge_id, {}) for badge_id in badges_earned if badge_id in BADGES}


def build_nutrition_by_date(meals: List[Dict]) -> Dict[str, Dict[str, float]]:
    """
    Build a nutrition summary organized by date from a list of meals.
    
    Consolidates nutritional data across multiple meals for each date.
    Used by analytics and dashboard pages to prepare data for visualization.
    
    Args:
        meals: List of meal dictionaries with nutrition data
        
    Returns:
        Dictionary with dates as keys and nutrition summaries as values
        {
            "2025-11-20": {
                "calories": 2150,
                "protein": 85.5,
                "carbs": 250,
                "fat": 75
            }
        }
    """
    nutrition_by_date = {}
    for meal in meals:
        meal_date = meal.get("logged_at", "").split("T")[0]
        nutrition = meal.get("nutrition", {})
        
        if meal_date not in nutrition_by_date:
            nutrition_by_date[meal_date] = {
                "calories": 0,
                "protein": 0,
                "carbs": 0,
                "fat": 0,
            }
        
        nutrition_by_date[meal_date]["calories"] += nutrition.get("calories", 0)
        nutrition_by_date[meal_date]["protein"] += nutrition.get("protein", 0)
        nutrition_by_date[meal_date]["carbs"] += nutrition.get("carbs", 0)
        nutrition_by_date[meal_date]["fat"] += nutrition.get("fat", 0)
    
    return nutrition_by_date


def paginate_items(items: List, page_size: int = 10) -> tuple[int, List]:
    """
    Paginate a list of items with session state management.
    
    Handles pagination state and returns the current page and paginated items.
    Uses session state to persist page selection across reruns.
    
    Args:
        items: List of items to paginate
        page_size: Number of items per page (default: 10)
        
    Returns:
        Tuple of (total_pages, paginated_items)
    """
    import streamlit as st
    
    # Initialize pagination state
    if "pagination_page" not in st.session_state:
        st.session_state.pagination_page = 0
    
    total_items = len(items)
    total_pages = (total_items + page_size - 1) // page_size  # Ceiling division
    
    # Ensure current page is valid
    if st.session_state.pagination_page >= total_pages:
        st.session_state.pagination_page = max(0, total_pages - 1)
    
    # Calculate slice indices
    start_idx = st.session_state.pagination_page * page_size
    end_idx = start_idx + page_size
    
    paginated_items = items[start_idx:end_idx]
    
    return total_pages, paginated_items
