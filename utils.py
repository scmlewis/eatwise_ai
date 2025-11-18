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


def get_date_range(days: int) -> tuple:
    """Get date range for analytics"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def serialize_datetime(obj):
    """JSON serializer for datetime objects"""
    if isinstance(obj, (datetime, )):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


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


def clear_session():
    """Clear session state"""
    st.session_state.user_id = None
    st.session_state.user_email = None
    st.session_state.user_profile = None
    st.session_state.current_page = "Dashboard"


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
