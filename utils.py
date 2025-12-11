"""Utility functions for EatWise"""
import json
import html
import time
import logging
from functools import wraps
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import streamlit as st
import pytz

logger = logging.getLogger(__name__)


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


def show_skeleton_loader(num_items: int = 3, item_type: str = "card"):
    """
    Display animated skeleton loaders while content is loading.
    
    Args:
        num_items: Number of skeleton items to show (default: 3)
        item_type: Type of skeleton - "card", "text", "bar", "list" (default: "card")
    """
    import streamlit as st
    
    if item_type == "card":
        for _ in range(num_items):
            st.markdown("""
            <div class="skeleton-card">
                <div class="skeleton skeleton-heading"></div>
                <div class="skeleton skeleton-line"></div>
                <div class="skeleton skeleton-line"></div>
                <div class="skeleton skeleton-line" style="width: 80%;"></div>
            </div>
            """, unsafe_allow_html=True)
    
    elif item_type == "text":
        for _ in range(num_items):
            st.markdown("""
            <div style="margin-bottom: 12px;">
                <div class="skeleton skeleton-heading"></div>
                <div class="skeleton skeleton-line"></div>
                <div class="skeleton skeleton-line"></div>
            </div>
            """, unsafe_allow_html=True)
    
    elif item_type == "bar":
        for _ in range(num_items):
            st.markdown("""
            <div style="margin-bottom: 16px;">
                <div class="skeleton skeleton-line" style="width: 40%; margin-bottom: 8px;"></div>
                <div class="skeleton skeleton-bar"></div>
            </div>
            """, unsafe_allow_html=True)
    
    elif item_type == "list":
        for _ in range(num_items):
            st.markdown("""
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <div class="skeleton" style="width: 32px; height: 32px; border-radius: 50%; margin-right: 12px;"></div>
                <div style="flex: 1;">
                    <div class="skeleton skeleton-line" style="margin-bottom: 8px;"></div>
                    <div class="skeleton skeleton-line" style="width: 70%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_icon(icon_name: str, icon_size: str = "md", color_class: str = "icon-primary") -> str:
    """
    Render an icon using Tabler Icons.
    
    Args:
        icon_name: Tabler icon name (e.g., "apple", "flame", "heart", "activity")
        icon_size: Icon size - "sm", "md", "lg", "xl" (default: "md")
        color_class: Color class - "icon-primary", "icon-success", "icon-warning", etc.
    
    Returns:
        HTML string for the icon
    """
    return f'<i class="icon icon-{icon_size} {color_class} ti ti-{icon_name}"></i>'


def get_nutrition_icon(nutrition_type: str) -> str:
    """
    Get appropriate icon for nutrition metrics.
    
    Args:
        nutrition_type: Type of nutrition - "calories", "protein", "carbs", "fat", etc.
    
    Returns:
        Tabler icon name
    """
    icon_map = {
        "calories": "flame",
        "protein": "beef",
        "carbs": "grain",
        "fat": "droplet",
        "fiber": "leaf",
        "sugar": "candy",
        "sodium": "salt",
        "water": "droplets",
        "meal": "apple",
        "breakfast": "sun",
        "lunch": "sun",
        "dinner": "moon",
        "snack": "cookie",
        "health": "heart",
        "goal": "target",
        "activity": "activity",
        "trending": "trending-up"
    }
    return icon_map.get(nutrition_type, "circle")


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0, exceptions: tuple = (ConnectionError, TimeoutError)):
    """
    Decorator to retry failed operations with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exception types to catch and retry
        
    Returns:
        Decorated function that retries on failure
        
    Example:
        @retry_on_failure(max_retries=3)
        def fetch_data():
            # ... code that might fail
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"Max retries ({max_retries}) reached for {func.__name__}: {e}")
                        raise
                    
                    logger.warning(
                        f"Retry {retries}/{max_retries} for {func.__name__} "
                        f"after {current_delay:.1f}s due to: {type(e).__name__}"
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
                except Exception as e:
                    # Don't retry on other exception types
                    logger.error(f"Non-retryable error in {func.__name__}: {type(e).__name__}: {e}")
                    raise
                    
            return None
        return wrapper
    return decorator


def sanitize_user_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input for AI prompts and database storage.
    
    Args:
        text: User input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text safe for processing
        
    Example:
        meal_desc = sanitize_user_input(user_input, max_length=500)
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove excessive whitespace
    text = " ".join(text.split())
    
    # Truncate to max length
    if len(text) > max_length:
        logger.warning(f"Input truncated from {len(text)} to {max_length} characters")
        text = text[:max_length]
    
    # Escape HTML to prevent injection
    text = html.escape(text)
    
    return text


def get_user_friendly_error(error: Exception) -> str:
    """
    Convert technical errors to user-friendly messages.
    
    Args:
        error: Exception object
        
    Returns:
        User-friendly error message
    """
    ERROR_MESSAGES = {
        "user_id": "Your session has expired. Please log in again.",
        "row level security": "You don't have permission to access this data.",
        "permission denied": "You don't have permission to perform this action.",
        "network": "Connection error. Please check your internet connection.",
        "timeout": "Request timed out. Please try again.",
        "rate limit": "Too many requests. Please wait a moment and try again.",
        "authentication": "Authentication error. Please log in again.",
        "not found": "The requested resource was not found.",
    }
    
    error_str = str(error).lower()
    
    for key, message in ERROR_MESSAGES.items():
        if key in error_str:
            return message
    
    # Default message for unknown errors
    return "An unexpected error occurred. Please try again or contact support if the issue persists."


