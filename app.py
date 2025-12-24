"""
EatWise - AI-Powered Nutrition Hub
Main Streamlit Application
"""

# Cache buster - increment this to force page reload
APP_VERSION = "2.5.1"

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta, time
from typing import Optional, Dict, List
import json
import base64
from streamlit_option_menu import option_menu

# Import modules
from config import (
    APP_NAME, APP_DESCRIPTION, SUPABASE_URL, SUPABASE_KEY,
    DAILY_CALORIE_TARGET, DAILY_PROTEIN_TARGET, DAILY_CARBS_TARGET,
    DAILY_FAT_TARGET, DAILY_SODIUM_TARGET, DAILY_SUGAR_TARGET, 
    DAILY_FIBER_TARGET, AGE_GROUP_TARGETS, HEALTH_CONDITION_TARGETS, HEALTH_GOAL_TARGETS, GENDER_ADJUSTMENTS,
    AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT
)
from constants import MEAL_TYPES, HEALTH_CONDITIONS, DIETARY_PREFERENCES, BADGES, COLORS
from auth import AuthManager, init_auth_session, is_authenticated
from database import DatabaseManager
from nutrition_analyzer import NutritionAnalyzer
from recommender import RecommendationEngine
from coaching_assistant import CoachingAssistant
from restaurant_analyzer import RestaurantMenuAnalyzer
from nutrition_components import display_nutrition_targets_progress
from gamification import GamificationManager
from utils import (
    init_session_state, get_greeting, calculate_nutrition_percentage,
    get_nutrition_status, get_streak_info,
    get_earned_badges, build_nutrition_by_date, paginate_items
)
from portion_estimation_disclaimer import (
    assess_input_confidence, show_estimation_disclaimer, show_estimation_tips
)


def normalize_profile(profile: dict) -> dict:
    """Ensure profile fields are present and properly typed.

    - Parses JSON strings for list fields coming from DB.
    - Ensures defaults for missing keys so UI doesn't show N/A unexpectedly.
    """
    if not profile:
        return profile

    p = dict(profile)  # shallow copy

    # health_conditions may be stored as JSON string in DB
    hc = p.get('health_conditions')
    if isinstance(hc, str):
        try:
            p['health_conditions'] = json.loads(hc)
        except Exception:
            p['health_conditions'] = [hc] if hc else []
    elif hc is None:
        p['health_conditions'] = []
    elif not isinstance(hc, list):
        p['health_conditions'] = [hc]

    # dietary_preferences may be stored as JSON string
    dp = p.get('dietary_preferences')
    if isinstance(dp, str):
        try:
            p['dietary_preferences'] = json.loads(dp)
        except Exception:
            p['dietary_preferences'] = [dp] if dp else []
    elif dp is None:
        p['dietary_preferences'] = []
    elif not isinstance(dp, list):
        p['dietary_preferences'] = [dp]

    # Ensure water goal is numeric
    try:
        p['water_goal_glasses'] = int(p.get('water_goal_glasses', 8) or 8)
    except Exception:
        p['water_goal_glasses'] = 8

    # Defaults for compact display
    if not p.get('age_group'):
        p['age_group'] = 'N/A'
    if not p.get('health_goal'):
        p['health_goal'] = 'N/A'

    return p


def get_or_load_user_profile() -> dict:
    """
    Get user profile from session state, or load from database if missing.
    Centralizes profile loading logic to prevent duplicate DB calls.
    
    Returns:
        Normalized user profile dict
    """
    # Try to get from session state first
    user_profile = st.session_state.get('user_profile')
    
    if user_profile:
        return user_profile
    
    # Load from database if not in session
    user_profile = db_manager.get_health_profile(st.session_state.user_id)
    
    # Normalize the profile
    user_profile = normalize_profile(user_profile) if user_profile else None
    
    # If still missing, use sensible defaults
    if not user_profile:
        user_profile = {
            "user_id": st.session_state.user_id,
            "age_group": "26-35",
            "health_goal": "general_health",
            "timezone": "UTC",
            "health_conditions": [],
            "dietary_preferences": [],
            "water_goal_glasses": 8
        }
    
    # Cache in session state for subsequent calls
    st.session_state.user_profile = user_profile
    
    return user_profile


def calculate_personal_targets(user_profile: Optional[dict]) -> dict:
    """
    Build nutrition targets for a user profile with all adjustments applied.
    Centralizes the age/goal/condition logic so we don't duplicate it across pages.
    """
    profile = user_profile or {}
    age_group = profile.get("age_group", "26-35")
    targets = AGE_GROUP_TARGETS.get(age_group, AGE_GROUP_TARGETS["26-35"]).copy()

    # Apply health condition adjustments (these replace values for medical reasons)
    for condition in profile.get("health_conditions", []) or []:
        if condition in HEALTH_CONDITION_TARGETS:
            targets.update(HEALTH_CONDITION_TARGETS[condition])

    # Apply health goal adjustments (these ADD to base values)
    health_goal = profile.get("health_goal", "general_health")
    if health_goal in HEALTH_GOAL_TARGETS:
        for key, value in HEALTH_GOAL_TARGETS[health_goal].items():
            if key in targets:
                targets[key] += value

    # Apply gender adjustments (these ADD to current values)
    gender = profile.get("gender", "Female")
    if gender in GENDER_ADJUSTMENTS and GENDER_ADJUSTMENTS[gender]:
        for key, value in GENDER_ADJUSTMENTS[gender].items():
            if key in targets:
                targets[key] += value

    return targets


def load_daily_snapshot(user_profile: Optional[dict], days_back: int = 30) -> dict:
    """
    Fetch commonly used daily data once so sidebar and dashboard can share it.
    Reduces duplicate DB hits within a single app run.
    """
    user_id = st.session_state.user_id
    today = date.today()
    default_nutrition = {
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0,
        "sodium": 0,
        "sugar": 0,
        "fiber": 0,
    }

    meals_today = db_manager.get_meals_by_date(user_id, today)
    daily_nutrition_raw = db_manager.get_daily_nutrition_summary(user_id, today) or {}
    daily_nutrition = {**default_nutrition, **daily_nutrition_raw}
    water_intake = db_manager.get_daily_water_intake(user_id, today)

    start_date = today - timedelta(days=days_back)
    recent_meals = db_manager.get_meals_in_range(user_id, start_date, today)

    recent_meal_dates = []
    for meal in recent_meals:
        try:
            recent_meal_dates.append(datetime.fromisoformat(meal.get("logged_at", "")))
        except Exception:
            continue

    return {
        "today": today,
        "meals_today": meals_today,
        "daily_nutrition": daily_nutrition,
        "water_intake": water_intake,
        "recent_meals": recent_meals,
        "recent_meal_dates": recent_meal_dates,
        "streak_info": get_streak_info(recent_meal_dates),
        "targets": calculate_personal_targets(user_profile),
    }


def render_stat_card(emoji: str, title: str, value: str, subtitle: str, 
                     progress_value: float, status: str, color: str, 
                     shadow_color: str, gradient_start: str, gradient_end: str):
    """
    Render a reusable nutrition stat card with consistent styling.
    
    Args:
        emoji: Card emoji (e.g., "🔥", "🍽️")
        title: Card title in uppercase (e.g., "Avg Calories")
        value: Main value to display (e.g., "2500")
        subtitle: Subtitle text (e.g., "of 2000")
        progress_value: Float 0-100 for progress bar width
        status: Status indicator (emoji + optional text)
        color: Primary color for text/borders (e.g., "#FFB84D")
        shadow_color: RGBA color for box-shadow
        gradient_start: Gradient start color with alpha (e.g., "#FF6B1620")
        gradient_end: Gradient end color with alpha (e.g., "#FF6B1640")
    """
    st.markdown(f"""
    <div class="stat-card" style="
        background: linear-gradient(135deg, {gradient_start} 0%, {gradient_end} 100%);
        border: 1px solid {color};
        border-left: 5px solid {color};
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 15px {shadow_color};
        transition: transform 0.2s ease;
    ">
        <div style="font-size: 28px; margin-bottom: 6px;">{emoji}</div>
        <div style="font-size: 11px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; font-weight: 700;">{title}</div>
        <div style="font-size: 28px; font-weight: 900; color: {color}; margin-bottom: 8px;">{value}</div>
        <div style="font-size: 9px; color: {color}; font-weight: 700; margin-bottom: 6px;">{subtitle}</div>
        <div style="background: #0a0e27; border-radius: 4px; height: 4px; margin-bottom: 8px;"><div style="background: linear-gradient(90deg, {color} 0%, {color}80 100%); height: 100%; width: {min(progress_value, 100)}%; border-radius: 4px;"></div></div>
        <div style="font-size: 9px; color: {color}; font-weight: 600;">{status}</div>
    </div>
    """, unsafe_allow_html=True)


def show_notification(message: str, notification_type: str = "success", use_toast: bool = True):
    """
    Unified notification helper for consistent UX across the app.
    
    Args:
        message: Notification message (emoji already included if needed)
        notification_type: 'success', 'error', 'warning', or 'info'
        use_toast: If True, use st.toast() (auto-dismiss); if False, use persistent boxes
    """
    if use_toast:
        # Auto-dismiss toasts for quick feedback (water, quick add, delete, etc.)
        icon_map = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        st.toast(message, icon=icon_map.get(notification_type, "ℹ️"))
    else:
        # Persistent boxes for important context (profile changes, batch operations)
        api_map = {
            "success": st.success,
            "error": st.error,
            "warning": st.warning,
            "info": st.info
        }
        api_func = api_map.get(notification_type, st.info)
        api_func(message)


def render_animated_stat_card(emoji: str, title: str, value: float, subtitle: str, 
                               progress_value: float, status: str, color: str, 
                               shadow_color: str, gradient_start: str, gradient_end: str):
    """
    Render a nutrition stat card with animated number counter.
    
    Args:
        emoji: Card emoji (e.g., "🔥", "🍽️")
        title: Card title in uppercase (e.g., "Avg Calories")
        value: Main value to display (will animate from 0 to this number)
        subtitle: Subtitle text (e.g., "of 2000")
        progress_value: Float 0-100 for progress bar width
        status: Status indicator (emoji + optional text)
        color: Primary color for text/borders (e.g., "#FFB84D")
        shadow_color: RGBA color for box-shadow
        gradient_start: Gradient start color with alpha
        gradient_end: Gradient end color with alpha
    """
    int_value = int(value)
    st.markdown(f"""
    <div class="stat-card" style="
        background: linear-gradient(135deg, {gradient_start} 0%, {gradient_end} 100%);
        border: 1px solid {color};
        border-left: 5px solid {color};
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 15px {shadow_color};
        transition: transform 0.2s ease;
    ">
        <div style="font-size: 28px; margin-bottom: 6px;">{emoji}</div>
        <div style="font-size: 11px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; font-weight: 700;">{title}</div>
        <div class="counter-number" style="font-size: 28px; font-weight: 900; color: {color}; margin-bottom: 8px; display: block;">
            <span data-target="{int_value}">0</span>
        </div>
        <div style="font-size: 9px; color: {color}; font-weight: 700; margin-bottom: 6px;">{subtitle}</div>
        <div style="background: #0a0e27; border-radius: 4px; height: 4px; margin-bottom: 8px;">
            <div class="progress-bar-animated" style="background: linear-gradient(90deg, {color} 0%, {color}80 100%); height: 100%; --progress-width: {min(progress_value, 100)}%; border-radius: 4px;"></div>
        </div>
        <div style="font-size: 9px; color: {color}; font-weight: 600;">{status}</div>
    </div>
    
    <script>
        function animateCounter(element, target, duration = 800) {{
            const startValue = 0;
            const startTime = performance.now();
            
            function update(currentTime) {{
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const easeOut = 1 - Math.pow(1 - progress, 3);
                const currentValue = Math.floor(startValue + (target - startValue) * easeOut);
                
                element.textContent = currentValue.toLocaleString();
                
                if (progress < 1) {{
                    requestAnimationFrame(update);
                }}
            }}
            
            requestAnimationFrame(update);
        }}
        
        document.querySelectorAll('[data-target]').forEach(el => {{
            const target = parseInt(el.getAttribute('data-target'));
            animateCounter(el, target);
        }});
    </script>
    """, unsafe_allow_html=True)


def show_badge_unlock_animation(badge_name: str, badge_icon: str, badge_description: str = ""):
    """
    Display badge unlock with pop-in animation.
    
    Args:
        badge_name: Name of the badge earned
        badge_icon: Emoji icon for the badge
        badge_description: Optional description of the badge
    """
    st.markdown(f"""
    <style>
        .badge-unlock-container {{
            text-align: center;
            padding: 30px 20px;
            background: linear-gradient(135deg, rgba(82, 196, 184, 0.15) 0%, rgba(255, 212, 59, 0.15) 100%);
            border: 2px solid rgba(82, 196, 184, 0.3);
            border-radius: 16px;
            margin: 20px 0;
        }}
    </style>
    <div class="badge-unlock-container">
        <div class="badge-unlock" style="font-size: 64px; margin-bottom: 12px; display: inline-block;">
            {badge_icon}
        </div>
        <div class="badge-unlock-text" style="font-size: 22px; color: #FFD43B; font-weight: 900; margin-bottom: 8px;">
            🎉 Badge Unlocked!
        </div>
        <div style="font-size: 16px; color: #52C4B8; font-weight: 700; margin-bottom: 6px;">
            {badge_name}
        </div>
        {f'<div style="font-size: 12px; color: #a0a0a0;">{badge_description}</div>' if badge_description else ''}
    </div>
    """, unsafe_allow_html=True)


def show_empty_state(emoji: str, title: str, description: str, action_text: str = None):
    """
    Display beautiful empty state with CTA for better UX when no data is available.
    
    Args:
        emoji: Large emoji to display
        title: Empty state title
        description: Description of why this state is shown
        action_text: Optional call-to-action text
    """
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 60px 20px;
        background: linear-gradient(135deg, rgba(82, 196, 184, 0.1) 0%, rgba(82, 196, 184, 0.05) 100%);
        border: 2px dashed rgba(82, 196, 184, 0.3);
        border-radius: 16px;
        margin: 20px 0;
    ">
        <div style="font-size: 48px; margin-bottom: 16px;">{emoji}</div>
        <h3 style="color: #52C4B8; margin: 0 0 8px 0; font-weight: 700;">{title}</h3>
        <p style="color: #b8dbd9; margin: 0 0 16px 0; font-size: 14px;">{description}</p>
        {f'<p style="color: #10A19D; font-weight: 600; margin: 0; font-size: 13px;">→ {action_text}</p>' if action_text else ''}
    </div>
    """, unsafe_allow_html=True)


# ==================== COMPONENT HELPERS ====================
# Production-grade card and component styling functions


def validate_meal_data(meal_name: str, nutrition: dict, meal_date: datetime.date = None) -> tuple[bool, str]:
    """
    Validate meal data before saving to database.
    
    Args:
        meal_name: Name of the meal
        nutrition: Dictionary with nutrition values (calories, protein, carbs, fat, sodium, sugar, fiber)
        meal_date: Date of the meal (optional, defaults to today)
    
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    # Validate meal name
    if not meal_name or not meal_name.strip():
        return False, "Meal name cannot be empty"
    
    # Validate date is not in the future
    if meal_date:
        if meal_date > datetime.now().date():
            return False, "Meal date cannot be in the future"
    
    # Validate nutrition values are in reasonable ranges
    if not nutrition:
        return False, "Nutrition information is required"
    
    calories = nutrition.get('calories', 0)
    protein = nutrition.get('protein', 0)
    carbs = nutrition.get('carbs', 0)
    fat = nutrition.get('fat', 0)
    
    # Sanity check: calories should be 0-10000 for a single meal
    if calories < 0 or calories > 10000:
        return False, f"Calories must be between 0-10000 (got {calories})"
    
    # Sanity check: macros should be reasonable (0-2000g per macro)
    for macro_name, macro_value in [("Protein", protein), ("Carbs", carbs), ("Fat", fat)]:
        if macro_value < 0 or macro_value > 2000:
            return False, f"{macro_name} must be between 0-2000g (got {macro_value}g)"
    
    return True, ""


def show_nutrition_facts(nutrition: dict, show_label: bool = False):
    """
    Display nutrition facts in a consistent card format across the app.
    
    Args:
        nutrition: Dictionary with nutrition values (calories, protein, carbs, fat, etc.)
        show_label: Whether to show "Nutrition Facts" label (for main meal detail displays)
    """
    if show_label:
        st.markdown("### 📊 Nutrition Facts")
    
    st.markdown(nutrition_analyzer.get_nutrition_facts_html(nutrition), unsafe_allow_html=True)








# ==================== PAGE CONFIG ====================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="assets/eatwise-logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# ==================== STYLING ====================

st.markdown("""
<style>
    /* ===== FONTS & BASE IMPORTS ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');
    @import url('https://cdn.jsdelivr.net/npm/tabler-icons@latest/tabler-icons.min.css');
    
    :root {
        /* Primary palette - refined teal with depth */
        --primary-50: #E6FAF9;
        --primary-100: #B3F0ED;
        --primary-200: #80E6E1;
        --primary-300: #4DD9D3;
        --primary-400: #26CFC8;
        --primary-500: #10A19D;
        --primary-600: #0D847F;
        --primary-700: #0A6662;
        --primary-800: #074845;
        --primary-900: #042A28;
        
        /* Accent colors */
        --accent-purple: #8B5CF6;
        --accent-purple-light: #A78BFA;
        --accent-blue: #3B82F6;
        --accent-blue-light: #60A5FA;
        --accent-pink: #EC4899;
        --accent-orange: #F59E0B;
        
        /* Semantic colors */
        --success-400: #4ADE80;
        --success-500: #22C55E;
        --success-600: #16A34A;
        --warning-400: #FBBF24;
        --warning-500: #F59E0B;
        --warning-600: #D97706;
        --danger-400: #F87171;
        --danger-500: #EF4444;
        --danger-600: #DC2626;
        
        /* Neutrals - refined dark theme */
        --neutral-50: #F8FAFC;
        --neutral-100: #F1F5F9;
        --neutral-200: #E2E8F0;
        --neutral-300: #CBD5E1;
        --neutral-400: #94A3B8;
        --neutral-500: #64748B;
        --neutral-600: #475569;
        --neutral-700: #334155;
        --neutral-800: #1E293B;
        --neutral-900: #0F172A;
        --neutral-950: #020617;
        
        /* Surface colors for layered UI - GREENER */
        --surface-0: #1a3430;
        --surface-1: #1e3a35;
        --surface-2: #24443f;
        --surface-3: #2a4e4a;
        --surface-4: #305854;
        
        /* Glass morphism */
        --glass-bg: rgba(255, 255, 255, 0.03);
        --glass-border: rgba(255, 255, 255, 0.08);
        --glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        
        /* Typography */
        --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
        
        /* Spacing scale */
        --space-1: 4px;
        --space-2: 8px;
        --space-3: 12px;
        --space-4: 16px;
        --space-5: 20px;
        --space-6: 24px;
        --space-8: 32px;
        --space-10: 40px;
        --space-12: 48px;
        
        /* Border radius */
        --radius-sm: 6px;
        --radius-md: 10px;
        --radius-lg: 14px;
        --radius-xl: 20px;
        --radius-2xl: 28px;
        --radius-full: 9999px;
        
        /* Shadows - layered for depth */
        --shadow-xs: 0 1px 2px rgba(0, 0, 0, 0.3);
        --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.3), 0 1px 2px rgba(0, 0, 0, 0.2);
        --shadow-md: 0 4px 8px rgba(0, 0, 0, 0.3), 0 2px 4px rgba(0, 0, 0, 0.2);
        --shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.3), 0 4px 8px rgba(0, 0, 0, 0.2);
        --shadow-xl: 0 16px 32px rgba(0, 0, 0, 0.4), 0 8px 16px rgba(0, 0, 0, 0.2);
        --shadow-glow-primary: 0 0 20px rgba(16, 161, 157, 0.3), 0 0 40px rgba(16, 161, 157, 0.15);
        --shadow-glow-success: 0 0 20px rgba(34, 197, 94, 0.3), 0 0 40px rgba(34, 197, 94, 0.15);
        --shadow-glow-warning: 0 0 20px rgba(245, 158, 11, 0.3), 0 0 40px rgba(245, 158, 11, 0.15);
        --shadow-glow-danger: 0 0 20px rgba(239, 68, 68, 0.3), 0 0 40px rgba(239, 68, 68, 0.15);
        
        /* Transitions */
        --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-slow: 350ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-bounce: 500ms cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    
    /* ===== GLOBAL STYLES ===== */
    html, body, [class*="css"] {
        font-family: var(--font-sans) !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        letter-spacing: -0.01em;
    }
    
    /* Background with subtle noise texture - GREENER THEME */
    .main {
        padding-top: 1.5rem;
        background: 
            radial-gradient(ellipse 80% 50% at 50% -20%, rgba(16, 161, 157, 0.4), transparent),
            radial-gradient(ellipse 60% 40% at 100% 100%, rgba(34, 197, 94, 0.25), transparent),
            radial-gradient(circle at 0% 0%, rgba(16, 161, 157, 0.15), transparent 50%),
            radial-gradient(circle at 100% 100%, rgba(34, 197, 94, 0.15), transparent 50%),
            linear-gradient(180deg, #1a3430 0%, #1e3a35 50%, #244440 100%);
        background-attachment: fixed;
        min-height: 100vh;
    }
    
    /* Subtle animated gradient overlay - GREENER */
    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 20% 80%, rgba(16, 161, 157, 0.2) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(34, 197, 94, 0.18) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(16, 161, 157, 0.1) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
        animation: gradientShift 20s ease-in-out infinite alternate;
    }
    
    @keyframes gradientShift {
        0% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Typography hierarchy */
    h1 {
        font-size: 2rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.03em !important;
        background: linear-gradient(135deg, var(--neutral-50) 0%, var(--neutral-300) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-top: 0.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    h2 {
        font-size: 1.375rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        color: var(--neutral-100) !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    h3 {
        font-size: 1.125rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em !important;
        color: var(--neutral-200) !important;
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    p, span, div {
        color: var(--neutral-300);
    }
    
    /* ===== MODERN GRADIENT CARDS ===== */
    .gradient-primary {
        background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-400) 100%);
    }
    
    .gradient-purple {
        background: linear-gradient(135deg, var(--accent-purple) 0%, var(--accent-purple-light) 100%);
    }
    
    .gradient-blue {
        background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-blue-light) 100%);
    }
    
    .gradient-success {
        background: linear-gradient(135deg, var(--success-500) 0%, var(--success-400) 100%);
    }
    
    .gradient-warning {
        background: linear-gradient(135deg, var(--warning-500) 0%, var(--warning-400) 100%);
    }
    
    .gradient-danger {
        background: linear-gradient(135deg, var(--danger-500) 0%, var(--danger-400) 100%);
    }
    
    /* ===== METRIC CARDS - PRODUCTION GRADE ===== */
    .metric-card {
        background: linear-gradient(135deg, rgba(16, 161, 157, 0.08) 0%, rgba(16, 161, 157, 0.03) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(16, 161, 157, 0.15);
        padding: var(--space-5);
        border-radius: var(--radius-xl);
        color: white;
        margin: var(--space-2) 0;
        box-shadow: 
            var(--shadow-lg),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        transition: all var(--transition-base);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    }
    
    .metric-card:hover {
        transform: translateY(-4px) scale(1.01);
        background: linear-gradient(135deg, rgba(16, 161, 157, 0.12) 0%, rgba(16, 161, 157, 0.06) 100%);
        border-color: rgba(16, 161, 157, 0.3);
        box-shadow: 
            var(--shadow-xl),
            var(--shadow-glow-primary),
            inset 0 1px 0 rgba(255, 255, 255, 0.08);
    }
    
    /* Glass morphism cards */
    .card-glass {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-xl);
        padding: var(--space-5);
        box-shadow: var(--glass-shadow);
        position: relative;
    }
    
    .card-glass::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.06), transparent);
    }
    
    /* ===== NUTRITION PROGRESS BARS ===== */
    .nutrition-bar {
        height: 6px;
        background: rgba(255, 255, 255, 0.06);
        border-radius: var(--radius-full);
        overflow: hidden;
        margin: 6px 0;
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3);
    }
    
    .nutrition-bar > div {
        height: 100%;
        border-radius: var(--radius-full);
        transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .nutrition-bar > div::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        animation: shimmerBar 2s infinite;
    }
    
    @keyframes shimmerBar {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    /* Semantic status classes */
    .success { color: var(--success-400) !important; font-weight: 600; }
    .warning { color: var(--warning-400) !important; font-weight: 600; }
    .danger { color: var(--danger-400) !important; font-weight: 600; }
    .info { color: var(--accent-blue-light) !important; font-weight: 600; }
    
    /* ===== BUTTONS - REFINED ===== */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
        color: white;
        border: none;
        border-radius: var(--radius-lg);
        padding: 12px 24px;
        font-weight: 600;
        font-size: 14px;
        letter-spacing: -0.01em;
        transition: all var(--transition-base);
        box-shadow: 
            var(--shadow-md),
            0 0 0 1px rgba(16, 161, 157, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 50%;
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.1) 0%, transparent 100%);
        pointer-events: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 
            var(--shadow-lg),
            var(--shadow-glow-primary),
            0 0 0 1px rgba(16, 161, 157, 0.5);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: var(--shadow-sm);
    }
    
    /* Secondary button variant */
    .stButton > button[kind="secondary"] {
        background: transparent;
        border: 1px solid rgba(16, 161, 157, 0.4);
        color: var(--primary-400);
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: rgba(16, 161, 157, 0.1);
        border-color: var(--primary-400);
    }
    
    /* ===== TABS - PILL STYLE ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--surface-2);
        padding: 6px;
        border-radius: var(--radius-xl);
        border: 1px solid var(--glass-border);
        margin-bottom: 1.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: var(--radius-lg);
        padding: 10px 20px;
        border: none;
        color: var(--neutral-400);
        font-weight: 500;
        font-size: 14px;
        transition: all var(--transition-fast);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.05);
        color: var(--neutral-200);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
        color: white;
        font-weight: 600;
        box-shadow: var(--shadow-md);
    }
    
    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }
    
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }
    
    /* ===== SIDEBAR - GREENER ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a3430 0%, #1e3a35 100%);
        border-right: 1px solid rgba(16, 161, 157, 0.15);
    }
    
    section[data-testid="stSidebar"] > div {
        width: 280px !important;
        padding-top: var(--space-4);
    }
    
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: var(--neutral-300);
    }
    
    /* ===== FORM INPUTS ===== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        background: var(--surface-2) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: var(--radius-md) !important;
        color: var(--neutral-100) !important;
        font-size: 14px;
        transition: all var(--transition-fast);
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-500) !important;
        box-shadow: 0 0 0 3px rgba(16, 161, 157, 0.15) !important;
        outline: none !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: var(--neutral-500) !important;
    }
    
    /* Input labels */
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label {
        color: var(--neutral-300) !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        margin-bottom: 6px !important;
    }
    
    /* ===== ACCESSIBILITY ===== */
    input:focus, textarea:focus, select:focus {
        outline: 2px solid var(--primary-500) !important;
        outline-offset: 2px !important;
    }
    
    input:focus-visible, textarea:focus-visible, select:focus-visible {
        outline: 2px solid var(--primary-500) !important;
        outline-offset: 2px !important;
    }
    
    button:focus-visible {
        outline: 2px solid var(--primary-500) !important;
        outline-offset: 2px !important;
    }
    
    button:disabled, input:disabled, select:disabled, textarea:disabled {
        opacity: 0.5 !important;
        cursor: not-allowed !important;
    }
    
    button, input, select, textarea {
        min-height: 44px;
        font-size: 14px;
        line-height: 1.5;
    }
    
    /* Links */
    a {
        color: var(--primary-400);
        text-decoration: none;
        transition: all var(--transition-fast);
        font-weight: 500;
    }
    
    a:hover {
        color: var(--primary-300);
        text-decoration: underline;
    }
    
    a:focus {
        outline: 2px solid var(--primary-500);
        outline-offset: 2px;
    }
    
    /* Skip link */
    .skip-to-main {
        position: absolute;
        left: -9999px;
        z-index: 999;
    }
    
    .skip-to-main:focus {
        position: fixed;
        top: 10px;
        left: 10px;
        padding: 12px 24px;
        background: var(--primary-500);
        color: white;
        text-decoration: none;
        border-radius: var(--radius-md);
        z-index: 1000;
        box-shadow: var(--shadow-lg);
    }
    
    /* Ensure sufficient color contrast for semantic colors */
    .success {
        color: var(--success-400);
        font-weight: 600;
    }
    
    .warning {
        color: var(--warning-400);
        font-weight: 600;
    }
    
    .danger {
        color: var(--danger-400);
        font-weight: 600;
    }
    
    .info {
        color: var(--accent-blue-light);
        font-weight: 600;
    }
    
    /* ===== CARD SYSTEM - PRODUCTION GRADE ===== */
    
    /* Base card component */
    .card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-xl);
        padding: var(--space-5);
        position: relative;
        overflow: hidden;
        transition: all var(--transition-base);
    }
    
    .card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.08), transparent);
    }
    
    .card:hover {
        border-color: rgba(16, 161, 157, 0.3);
        box-shadow: var(--shadow-lg), var(--shadow-glow-primary);
    }
    
    /* ===== MEAL CARD - ENHANCED ===== */
    .meal-card {
        background: linear-gradient(135deg, rgba(16, 161, 157, 0.06) 0%, rgba(139, 92, 246, 0.03) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(16, 161, 157, 0.15);
        border-radius: var(--radius-xl);
        padding: var(--space-5);
        position: relative;
        overflow: hidden;
        transition: all var(--transition-base);
        cursor: pointer;
    }
    
    .meal-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(16, 161, 157, 0.3), transparent);
    }
    
    .meal-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(16, 161, 157, 0.1) 0%, transparent 50%);
        opacity: 0;
        transition: opacity var(--transition-base);
        pointer-events: none;
    }
    
    .meal-card:hover {
        transform: translateY(-4px) scale(1.01);
        border-color: rgba(16, 161, 157, 0.4);
        box-shadow: 
            var(--shadow-xl),
            var(--shadow-glow-primary);
    }
    
    .meal-card:hover::after {
        opacity: 1;
    }
    
    /* ===== NUTRITION INFO CARD - ENHANCED ===== */
    .nutrition-info {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.04) 0%, rgba(255, 255, 255, 0.01) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: var(--radius-xl);
        position: relative;
        overflow: hidden;
        transition: all var(--transition-base);
    }
    
    .nutrition-info::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        border-radius: var(--radius-xl) 0 0 var(--radius-xl);
    }
    
    .nutrition-info:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-xl);
    }
    
    /* ===== BADGE/ACHIEVEMENT CARD - ENHANCED ===== */
    .badge-achievement {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(16, 161, 157, 0.05) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: var(--radius-xl);
        padding: var(--space-4);
        position: relative;
        overflow: hidden;
        transition: all var(--transition-bounce);
        cursor: pointer;
    }
    
    .badge-achievement::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 60%);
        opacity: 0;
        transition: opacity var(--transition-base);
        pointer-events: none;
    }
    
    .badge-achievement:hover {
        transform: translateY(-6px) scale(1.02);
        border-color: rgba(139, 92, 246, 0.5);
        box-shadow: 
            var(--shadow-xl),
            0 0 30px rgba(139, 92, 246, 0.3),
            0 0 60px rgba(139, 92, 246, 0.15);
    }
    
    .badge-achievement:hover::before {
        opacity: 1;
    }
    
    /* ===== INSIGHT CARD - ENHANCED ===== */
    .insight-box {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.06) 0%, rgba(16, 161, 157, 0.03) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-left: 3px solid var(--accent-blue);
        border-radius: var(--radius-lg);
        padding: var(--space-4);
        position: relative;
        transition: all var(--transition-base);
    }
    
    .insight-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, var(--accent-blue), transparent 80%);
    }
    
    .insight-box:hover {
        border-color: rgba(59, 130, 246, 0.4);
        transform: translateX(4px);
        box-shadow: var(--shadow-lg), 0 0 20px rgba(59, 130, 246, 0.15);
    }
    
    /* ===== STAT CARD - ENHANCED ===== */
    .stat-card {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.04) 0%, rgba(255, 255, 255, 0.01) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-xl);
        padding: var(--space-5);
        position: relative;
        overflow: hidden;
        transition: all var(--transition-base);
        cursor: pointer;
    }
    
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.08), transparent);
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
        border-color: rgba(16, 161, 157, 0.3);
        box-shadow: var(--shadow-xl), var(--shadow-glow-primary);
    }
    
    /* ===== CHART CONTAINER - ENHANCED ===== */
    .chart-container {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-xl);
        padding: var(--space-5);
        position: relative;
        overflow: hidden;
        transition: all var(--transition-base);
    }
    
    .chart-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.06), transparent);
    }
    
    .chart-container:hover {
        border-color: rgba(16, 161, 157, 0.3);
        box-shadow: var(--shadow-lg);
    }
    
    /* ===== SUMMARY/PROGRESS CARD - ENHANCED ===== */
    .summary-card {
        background: linear-gradient(145deg, rgba(16, 161, 157, 0.08) 0%, rgba(16, 161, 157, 0.03) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(16, 161, 157, 0.15);
        border-radius: var(--radius-xl);
        padding: var(--space-5);
        position: relative;
        overflow: hidden;
        transition: all var(--transition-base);
        cursor: pointer;
    }
    
    .summary-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(16, 161, 157, 0.2), transparent);
    }
    
    .summary-card:hover {
        transform: translateY(-4px) scale(1.01);
        border-color: rgba(16, 161, 157, 0.4);
        box-shadow: var(--shadow-xl), var(--shadow-glow-primary);
    }
    
    /* ===== MACRO BREAKDOWN BOX - ENHANCED ===== */
    .macro-box {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.04) 0%, rgba(255, 255, 255, 0.01) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-lg);
        padding: var(--space-4);
        position: relative;
        overflow: hidden;
        transition: all var(--transition-base);
    }
    
    .macro-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.06), transparent);
    }
    
    .macro-box:hover {
        border-color: rgba(16, 161, 157, 0.4);
        box-shadow: var(--shadow-lg), var(--shadow-glow-primary);
    }
    
    /* ===== DASHBOARD INFO BOXES - ENHANCED ===== */
    @keyframes dashboardFadeIn {
        from { 
            opacity: 0; 
            transform: translateY(16px);
        }
        to { 
            opacity: 1; 
            transform: translateY(0);
        }
    }
    
    .dashboard-info-box {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.04) 0%, rgba(255, 255, 255, 0.01) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-xl);
        padding: var(--space-5);
        position: relative;
        overflow: hidden;
        animation: dashboardFadeIn 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        transition: all var(--transition-base);
    }
    
    .dashboard-info-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.08), transparent);
    }
    
    .dashboard-info-box:hover {
        border-color: rgba(16, 161, 157, 0.4);
        box-shadow: var(--shadow-xl), var(--shadow-glow-primary);
    }
    
    /* ===== PATTERN/TIMING CARD - ENHANCED ===== */
    .pattern-card {
        background: linear-gradient(145deg, rgba(139, 92, 246, 0.06) 0%, rgba(16, 161, 157, 0.03) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(139, 92, 246, 0.15);
        border-radius: var(--radius-lg);
        padding: var(--space-4);
        position: relative;
        overflow: hidden;
        transition: all var(--transition-base);
        cursor: pointer;
    }
    
    .pattern-card:hover {
        background: linear-gradient(145deg, rgba(139, 92, 246, 0.12) 0%, rgba(16, 161, 157, 0.06) 100%);
        border-color: rgba(139, 92, 246, 0.4);
        box-shadow: var(--shadow-lg), 0 0 20px rgba(139, 92, 246, 0.15);
    }
    
    /* ===== HEALTH METRIC BOX - ENHANCED ===== */
    .health-metric {
        background: linear-gradient(145deg, rgba(34, 197, 94, 0.06) 0%, rgba(16, 161, 157, 0.03) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(34, 197, 94, 0.15);
        border-radius: var(--radius-xl);
        padding: var(--space-5);
        position: relative;
        overflow: hidden;
        transition: all var(--transition-base);
        cursor: pointer;
    }
    
    .health-metric:hover {
        transform: translateY(-4px);
        border-color: rgba(34, 197, 94, 0.4);
        box-shadow: var(--shadow-xl), var(--shadow-glow-success);
    }
    
    /* ===== STREAK BOX - ENHANCED ===== */
    .streak-box {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(239, 68, 68, 0.05) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 2px solid rgba(245, 158, 11, 0.3);
        border-radius: var(--radius-2xl);
        padding: var(--space-6);
        position: relative;
        overflow: hidden;
        transition: all var(--transition-bounce);
        cursor: pointer;
    }
    
    .streak-box::before {
        content: '';
        position: absolute;
        top: -100%;
        left: -100%;
        width: 300%;
        height: 300%;
        background: radial-gradient(circle, rgba(245, 158, 11, 0.1) 0%, transparent 50%);
        animation: pulseGlow 3s ease-in-out infinite;
        pointer-events: none;
    }
    
    @keyframes pulseGlow {
        0%, 100% { transform: translate(0, 0); opacity: 0.5; }
        50% { transform: translate(10%, 10%); opacity: 1; }
    }
    
    .streak-box:hover {
        transform: translateY(-6px) scale(1.02);
        border-color: rgba(245, 158, 11, 0.6);
        box-shadow: var(--shadow-xl), var(--shadow-glow-warning);
    }
    
    /* ===== PROFILE SECTION - ENHANCED ===== */
    .profile-section {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.04) 0%, rgba(255, 255, 255, 0.01) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-xl);
        padding: var(--space-6);
        position: relative;
        overflow: hidden;
        transition: all var(--transition-base);
    }
    
    .profile-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.08), transparent);
    }
    
    .profile-section:hover {
        border-color: rgba(16, 161, 157, 0.4);
        box-shadow: var(--shadow-lg);
    }
    
    /* ===== SUGGESTION/RECOMMENDATION CARD - ENHANCED ===== */
    .suggestion-card {
        background: linear-gradient(145deg, rgba(59, 130, 246, 0.06) 0%, rgba(139, 92, 246, 0.03) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(59, 130, 246, 0.15);
        border-left: 3px solid var(--accent-blue);
        border-radius: var(--radius-lg);
        padding: var(--space-4);
        position: relative;
        overflow: hidden;
        transition: all var(--transition-base);
        cursor: pointer;
    }
    
    .suggestion-card:hover {
        transform: translateX(6px);
        border-color: rgba(59, 130, 246, 0.4);
        box-shadow: var(--shadow-lg), 0 0 20px rgba(59, 130, 246, 0.15);
    }
    
    /* ===== HIGH PRIORITY ANIMATIONS ===== */
    
    /* NUMBER COUNTER ANIMATION FOR STAT CARDS */
    @keyframes slideUpNumber {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .counter-number {
        animation: slideUpNumber 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
        display: inline-block;
    }
    
    /* PAGE TRANSITION ANIMATIONS */
    @keyframes slideInFromRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInFromLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .page-transition {
        animation: slideInFromRight 0.4s ease-out;
    }
    
    /* BADGE UNLOCK ANIMATION - POP-IN WITH BOUNCE */
    @keyframes badgePopIn {
        0% {
            opacity: 0;
            transform: scale(0) rotateZ(-15deg);
        }
        50% {
            transform: scale(1.15) rotateZ(5deg);
        }
        100% {
            opacity: 1;
            transform: scale(1) rotateZ(0deg);
        }
    }
    
    @keyframes badgeBounce {
        0%, 100% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-8px);
        }
    }
    
    .badge-unlock {
        animation: badgePopIn 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    }
    
    .badge-unlock-text {
        animation: badgeBounce 2s ease-in-out infinite;
    }
    
    /* PROGRESS BAR FILL ANIMATION */
    @keyframes fillProgress {
        from {
            width: 0;
        }
        to {
            width: var(--progress-width, 100%);
        }
    }
    
    .progress-bar-animated {
        animation: fillProgress 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
    }
    
    /* ===== UI OPTIMIZATION: SPACING & HIERARCHY ===== */
    
    /* Consistent section spacing for breathing room */
    .section-spacing {
        margin: 32px 0 !important;
    }
    
    /* Consistent card spacing */
    .card-spacing {
        margin-bottom: 16px !important;
    }
    
    /* Better heading hierarchy */
    h2 {
        margin-top: 28px !important;
        margin-bottom: 16px !important;
    }
    
    h3 {
        margin-top: 20px !important;
        margin-bottom: 12px !important;
    }
    
    /* Primary stat cards (larger, more prominent) */
    .primary-stat {
        min-height: 140px;
        font-size: 1.1em;
    }
    
    /* Secondary stat cards (medium) */
    .secondary-stat {
        min-height: 120px;
        font-size: 0.95em;
    }
    
    /* Tertiary stat cards (compact) */
    .tertiary-stat {
        min-height: 100px;
        font-size: 0.85em;
    }
    
    /* Better text contrast for accessibility */
    .card-text {
        color: var(--neutral-100) !important;
        font-weight: 500;
    }
    
    .card-label {
        color: var(--neutral-300) !important;
        font-weight: 600;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Clickable card hover effects */
    .clickable-card {
        cursor: pointer;
        transition: all var(--transition-base);
    }
    
    .clickable-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-lg), var(--shadow-glow-primary);
    }
    
    /* ===== EMPTY STATE - ENHANCED ===== */
    .empty-state {
        text-align: center;
        padding: 60px 32px;
        background: linear-gradient(145deg, rgba(16, 161, 157, 0.06) 0%, rgba(139, 92, 246, 0.03) 100%);
        border: 2px dashed rgba(16, 161, 157, 0.25);
        border-radius: var(--radius-2xl);
        margin: 24px 0;
        position: relative;
        overflow: hidden;
    }
    
    .empty-state::before {
        content: '';
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(16, 161, 157, 0.1) 0%, transparent 70%);
        pointer-events: none;
    }
    
    .empty-state-icon {
        font-size: 56px;
        margin-bottom: 20px;
        display: block;
    }
    
    .empty-state-title {
        color: var(--primary-300);
        margin: 0 0 12px 0;
        font-weight: 700;
        font-size: 18px;
    }
    
    .empty-state-description {
        color: var(--neutral-400);
        margin: 0 0 20px 0;
        font-size: 14px;
        line-height: 1.6;
    }
    
    .empty-state-action {
        color: var(--primary-400);
        font-weight: 600;
        margin: 0;
        font-size: 14px;
    }
    
    /* ===== MOBILE RESPONSIVENESS - ENHANCED ===== */
    @media (max-width: 768px) {
        :root {
            --space-4: 12px;
            --space-5: 16px;
            --space-6: 20px;
        }
        
        /* Stack columns vertically on mobile */
        [data-testid="column"] {
            min-width: 100% !important;
            margin-bottom: var(--space-4) !important;
        }
        
        /* Hide less important sidebar expanded text */
        .sidebar-expanded-text {
            display: none;
        }
        
        /* Larger touch targets for mobile */
        button {
            min-height: 48px !important;
            padding: 12px 16px !important;
        }
        
        .stButton > button {
            min-height: 48px !important;
            padding: 12px 20px !important;
            font-size: 14px !important;
        }
        
        /* Reduce horizontal padding on mobile */
        .main {
            padding: 0 var(--space-3) !important;
            padding-top: 1.5rem !important;
        }
        
        /* Compact stat cards on mobile */
        .stat-card, .metric-card, .dashboard-info-box {
            padding: var(--space-4) !important;
            border-radius: var(--radius-lg) !important;
        }
        
        /* Typography adjustments */
        h1 {
            font-size: 1.5rem !important;
        }
        
        h2 {
            font-size: 1.125rem !important;
            margin-top: var(--space-4) !important;
        }
        
        h3 {
            font-size: 1rem !important;
            margin-top: var(--space-3) !important;
        }
        
        /* Better spacing for mobile */
        .section-spacing {
            margin: var(--space-4) 0 !important;
        }
        
        .card-spacing {
            margin-bottom: var(--space-3) !important;
        }
        
        /* Tabs on mobile */
        .stTabs [data-baseweb="tab-list"] {
            flex-wrap: wrap;
            gap: 6px;
            padding: 4px;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 8px 14px;
            font-size: 13px;
            flex: 1 1 auto;
            text-align: center;
        }
        
        /* Hide less critical info on mobile */
        .mobile-hidden {
            display: none !important;
        }
    }
    
    @media (max-width: 480px) {
        /* Extra compact on very small screens */
        .main {
            padding: 0 var(--space-2) !important;
        }
        
        h1 {
            font-size: 1.25rem !important;
        }
        
        h2 {
            font-size: 1rem !important;
        }
        
        .stat-card, .metric-card {
            padding: var(--space-3) !important;
        }
        
        /* Single column grid on very small screens */
        [data-testid="column"] {
            max-width: 100% !important;
        }
        
        /* Compact nutrition cards */
        .nutrition-info {
            min-height: auto !important;
            padding: var(--space-3) !important;
        }
    }
    
    /* Reduce motion for users who prefer it */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    
    /* High contrast mode support */
    @media (prefers-contrast: more) {
        :root {
            --glass-border: rgba(255, 255, 255, 0.3);
        }
        
        input:focus, textarea:focus, select:focus, button:focus {
            outline: 3px solid var(--primary-400) !important;
            outline-offset: 3px !important;
        }
        
        button:disabled {
            opacity: 0.3 !important;
            border: 2px solid var(--neutral-500) !important;
        }
        
        .card, .metric-card, .stat-card {
            border-width: 2px !important;
        }
    }
    
    /* ===== ENTRANCE ANIMATIONS - REFINED ===== */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes slideUpFade {
        from {
            opacity: 0;
            transform: translateY(16px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideDownFade {
        from {
            opacity: 0;
            transform: translateY(-16px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes scaleIn {
        from {
            opacity: 0;
            transform: scale(0.96);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(24px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Staggered animation delays */
    .stagger-1 { animation-delay: 0.05s; }
    .stagger-2 { animation-delay: 0.1s; }
    .stagger-3 { animation-delay: 0.15s; }
    .stagger-4 { animation-delay: 0.2s; }
    .stagger-5 { animation-delay: 0.25s; }
    
    /* Apply entrance animations to main containers */
    .main {
        animation: fadeIn 0.4s ease-out;
    }
    
    [data-testid="stMetricDelta"] {
        animation: slideUpFade 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    [data-testid="stMetric"] {
        animation: slideUpFade 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stTabs [role="tablist"] {
        animation: slideDownFade 0.4s ease-out;
    }
    
    /* Card entrance animations */
    .meal-card {
        animation: scaleIn 0.35s cubic-bezier(0.4, 0, 0.2, 1) both;
    }
    
    .metric-card {
        animation: slideUpFade 0.4s cubic-bezier(0.4, 0, 0.2, 1) both;
    }
    
    .stat-card {
        animation: scaleIn 0.35s cubic-bezier(0.4, 0, 0.2, 1) both;
    }
    
    .nutrition-info {
        animation: slideUpFade 0.4s cubic-bezier(0.4, 0, 0.2, 1) both;
    }
    
    .dashboard-info-box {
        animation: slideUpFade 0.45s cubic-bezier(0.4, 0, 0.2, 1) both;
    }
    
    /* ===== LOADING SKELETONS - ENHANCED ===== */
    .skeleton {
        background: linear-gradient(
            90deg,
            rgba(255, 255, 255, 0.03) 0%,
            rgba(16, 161, 157, 0.08) 50%,
            rgba(255, 255, 255, 0.03) 100%
        );
        background-size: 200% 100%;
        animation: shimmer 1.8s ease-in-out infinite;
        border-radius: var(--radius-md);
    }
    
    @keyframes shimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    
    .skeleton-text {
        height: 14px;
        margin-bottom: 10px;
        border-radius: var(--radius-sm);
        display: block;
    }
    
    .skeleton-text:last-child {
        width: 70%;
    }
    
    .skeleton-heading {
        height: 28px;
        margin-bottom: 20px;
        border-radius: var(--radius-sm);
        display: block;
        width: 50%;
    }
    
    .skeleton-card {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.02) 0%, rgba(255, 255, 255, 0.01) 100%);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-xl);
        padding: var(--space-5);
        margin-bottom: var(--space-4);
    }
    
    .skeleton-card .skeleton-heading {
        margin-top: 0;
    }
    
    .skeleton-line {
        height: 12px;
        margin-bottom: 14px;
        border-radius: var(--radius-sm);
    }
    
    .skeleton-line:nth-child(odd) {
        width: 85%;
    }
    
    .skeleton-line:last-child {
        margin-bottom: 0;
        width: 60%;
    }
    
    .skeleton-bar {
        height: 44px;
        margin-bottom: 14px;
        border-radius: var(--radius-md);
    }
    
    .skeleton-avatar {
        width: 48px;
        height: 48px;
        border-radius: var(--radius-full);
    }
    
    .skeleton-circle {
        border-radius: var(--radius-full);
    }
    
    /* ===== ICON SYSTEM - PRODUCTION GRADE ===== */
    .icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        vertical-align: middle;
        flex-shrink: 0;
    }
    
    .icon-xs {
        width: 14px;
        height: 14px;
        font-size: 12px;
    }
    
    .icon-sm {
        width: 18px;
        height: 18px;
        font-size: 16px;
    }
    
    .icon-md {
        width: 24px;
        height: 24px;
        font-size: 20px;
    }
    
    .icon-lg {
        width: 32px;
        height: 32px;
        font-size: 28px;
    }
    
    .icon-xl {
        width: 48px;
        height: 48px;
        font-size: 40px;
    }
    
    .icon-2xl {
        width: 64px;
        height: 64px;
        font-size: 56px;
    }
    
    /* Icon colors using CSS variables */
    .icon-primary { color: var(--primary-400); }
    .icon-success { color: var(--success-400); }
    .icon-warning { color: var(--warning-400); }
    .icon-danger { color: var(--danger-400); }
    .icon-info { color: var(--accent-blue-light); }
    .icon-secondary { color: var(--accent-purple-light); }
    .icon-muted { color: var(--neutral-500); }
    
    /* Icon with background */
    .icon-bg {
        padding: 8px;
        border-radius: var(--radius-md);
    }
    
    .icon-bg-primary {
        background: rgba(16, 161, 157, 0.15);
        color: var(--primary-400);
    }
    
    .icon-bg-success {
        background: rgba(34, 197, 94, 0.15);
        color: var(--success-400);
    }
    
    .icon-bg-warning {
        background: rgba(245, 158, 11, 0.15);
        color: var(--warning-400);
    }
    
    .icon-bg-danger {
        background: rgba(239, 68, 68, 0.15);
        color: var(--danger-400);
    }
    
    /* ===== UTILITY CLASSES ===== */
    .text-center { text-align: center; }
    .text-left { text-align: left; }
    .text-right { text-align: right; }
    
    .font-mono { font-family: var(--font-mono); }
    .font-bold { font-weight: 700; }
    .font-semibold { font-weight: 600; }
    .font-medium { font-weight: 500; }
    
    .text-primary { color: var(--primary-400) !important; }
    .text-success { color: var(--success-400) !important; }
    .text-warning { color: var(--warning-400) !important; }
    .text-danger { color: var(--danger-400) !important; }
    .text-muted { color: var(--neutral-500) !important; }
    
    .bg-primary { background-color: var(--primary-500); }
    .bg-surface-1 { background-color: var(--surface-1); }
    .bg-surface-2 { background-color: var(--surface-2); }
    
    .rounded-sm { border-radius: var(--radius-sm); }
    .rounded-md { border-radius: var(--radius-md); }
    .rounded-lg { border-radius: var(--radius-lg); }
    .rounded-xl { border-radius: var(--radius-xl); }
    .rounded-full { border-radius: var(--radius-full); }
    
    .shadow-sm { box-shadow: var(--shadow-sm); }
    .shadow-md { box-shadow: var(--shadow-md); }
    .shadow-lg { box-shadow: var(--shadow-lg); }
    .shadow-xl { box-shadow: var(--shadow-xl); }
    .shadow-glow { box-shadow: var(--shadow-glow-primary); }
    
    /* Divider */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--glass-border), transparent);
        margin: var(--space-6) 0;
    }
    
    /* Badge component */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        font-size: 12px;
        font-weight: 600;
        border-radius: var(--radius-full);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-primary {
        background: rgba(16, 161, 157, 0.15);
        color: var(--primary-400);
        border: 1px solid rgba(16, 161, 157, 0.3);
    }
    
    .badge-success {
        background: rgba(34, 197, 94, 0.15);
        color: var(--success-400);
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    
    .badge-warning {
        background: rgba(245, 158, 11, 0.15);
        color: var(--warning-400);
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .badge-danger {
        background: rgba(239, 68, 68, 0.15);
        color: var(--danger-400);
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    /* Tooltip styling */
    .tooltip {
        position: relative;
    }
    
    .tooltip::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%) translateY(-8px);
        background: var(--surface-3);
        color: var(--neutral-100);
        padding: 8px 12px;
        border-radius: var(--radius-md);
        font-size: 12px;
        white-space: nowrap;
        opacity: 0;
        visibility: hidden;
        transition: all var(--transition-fast);
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--glass-border);
        z-index: 100;
    }
    
    .tooltip:hover::after {
        opacity: 1;
        visibility: visible;
        transform: translateX(-50%) translateY(-4px);
    }
    
    /* ===== SCROLLBAR STYLING ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--surface-1);
        border-radius: var(--radius-full);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--surface-4);
        border-radius: var(--radius-full);
        border: 2px solid var(--surface-1);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--neutral-500);
    }
    
    /* Firefox scrollbar */
    * {
        scrollbar-width: thin;
        scrollbar-color: var(--surface-4) var(--surface-1);
    }
    
    /* ===== SELECTION STYLING ===== */
    ::selection {
        background: rgba(16, 161, 157, 0.3);
        color: white;
    }
    
    ::-moz-selection {
        background: rgba(16, 161, 157, 0.3);
        color: white;
    }
    
</style>
""", unsafe_allow_html=True)

# ==================== INITIALIZATION ====================

init_session_state()
init_auth_session()

auth_manager = st.session_state.auth_manager
db_manager = DatabaseManager()
nutrition_analyzer = NutritionAnalyzer()
recommender = RecommendationEngine()


# ==================== AUTHENTICATION PAGES ====================

def login_page():
    """Login and signup page"""
    auth_manager = st.session_state.auth_manager
    # Add custom CSS for login page with full-page background
    st.markdown("""
    <style>
        /* Apply gradient to entire page when on login - GREENER */
        [data-testid="stAppViewContainer"] {
            background: 
                radial-gradient(ellipse 100% 80% at 50% 120%, rgba(16, 161, 157, 0.3), transparent),
                radial-gradient(ellipse 80% 50% at 0% 50%, rgba(34, 197, 94, 0.12), transparent),
                linear-gradient(180deg, #1a3430 0%, #1e3a35 50%, #244440 100%) !important;
            background-attachment: fixed !important;
        }
        
        [data-testid="stAppViewContainer"]::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: 
                radial-gradient(circle at 20% 30%, rgba(16, 161, 157, 0.1) 0%, transparent 40%),
                radial-gradient(circle at 80% 70%, rgba(34, 197, 94, 0.08) 0%, transparent 40%);
            pointer-events: none;
            z-index: 1;
        }
        
        .main {
            background: transparent !important;
        }
        
        .login-container {
            display: flex;
            gap: 24px;
            align-items: stretch;
        }
        
        .login-hero {
            flex: 1;
            background: linear-gradient(145deg, rgba(16, 161, 157, 0.95) 0%, rgba(13, 132, 127, 0.95) 100%);
            backdrop-filter: blur(20px);
            padding: 28px 32px;
            border-radius: 24px;
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 
                0 4px 6px rgba(0, 0, 0, 0.1),
                0 10px 20px rgba(0, 0, 0, 0.15),
                0 20px 40px rgba(16, 161, 157, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            position: relative;
            overflow: hidden;
        }
        
        .login-hero::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        }
        
        .login-hero::after {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 60%);
            pointer-events: none;
        }
        
        .login-hero h1 {
            font-size: 2.5em;
            margin: 0 0 8px 0;
            font-weight: 800;
            letter-spacing: -0.03em;
            position: relative;
            z-index: 1;
        }
        
        .login-hero h2 {
            font-size: 1.1em;
            margin: 0 0 20px 0;
            font-weight: 400;
            opacity: 0.9;
            letter-spacing: -0.01em;
            position: relative;
            z-index: 1;
        }
        
        .login-hero ul {
            font-size: 0.95em;
            line-height: 1.6;
            position: relative;
            z-index: 1;
        }
        
        .login-hero li {
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 12px;
            opacity: 0.95;
        }
        
        .login-form-container {
            flex: 1;
            background: linear-gradient(145deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 36px;
            border-radius: 24px;
            border: 1px solid rgba(16, 161, 157, 0.2);
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            box-shadow: 
                0 4px 6px rgba(0, 0, 0, 0.1),
                0 10px 20px rgba(0, 0, 0, 0.15),
                inset 0 1px 0 rgba(255, 255, 255, 0.05);
            position: relative;
        }
        
        .login-form-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(16, 161, 157, 0.3), transparent);
        }
        
        .login-header {
            margin-bottom: 4px;
            text-align: center;
            padding: 8px 0;
        }
        
        .login-header h3 {
            color: #4DD9D3;
            font-size: 1.4em;
            margin: 0;
            margin-bottom: 4px;
            font-weight: 700;
            letter-spacing: -0.02em;
        }
        
        .login-header p {
            margin: 0 !important;
            padding: 0 !important;
            color: #94A3B8;
        }
        
        .login-tabs {
            margin-top: 20px;
            margin-bottom: 15px;
        }
        
        .form-input-group {
            margin-bottom: 16px;
        }
        
        .form-input-group label {
            display: block;
            margin-bottom: 8px;
            color: #CBD5E1;
            font-weight: 500;
            font-size: 0.9em;
        }
        
        .stTextInput {
            margin-bottom: 16px !important;
        }
        
        .stTextInput input {
            background: rgba(15, 23, 42, 0.8) !important;
            color: #F1F5F9 !important;
            border: 1px solid rgba(16, 161, 157, 0.25) !important;
            border-radius: 12px !important;
            padding: 14px 16px !important;
            font-size: 0.95em !important;
            transition: all 0.2s ease !important;
        }
        
        .stTextInput input::placeholder {
            color: #64748B !important;
        }
        
        .stTextInput input:focus {
            border-color: #10A19D !important;
            box-shadow: 0 0 0 3px rgba(16, 161, 157, 0.15), 0 0 20px rgba(16, 161, 157, 0.1) !important;
            background: rgba(15, 23, 42, 0.95) !important;
        }
        
        .stCaption {
            color: #94A3B8 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    

    
    col1, col2 = st.columns([1.1, 1], gap="medium")
    
    with col1:
        st.markdown("""
        <div class="login-hero">
            <h1 style="font-size: 3.3em; margin: 0 0 8px 0; font-weight: 800; letter-spacing: -0.02em; background: linear-gradient(135deg, #fff 0%, rgba(255,255,255,0.9) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.1;">
                EatWise
            </h1>
            <h2 style="font-size: 1.3em; margin: 0 0 14px 0; font-weight: 600; color: rgba(255, 255, 255, 0.95); letter-spacing: -0.01em;">
                Your AI-Powered Nutrition Hub
            </h2>
            <p style="font-size: 0.98em; opacity: 0.85; margin-bottom: 14px; line-height: 1.5; color: rgba(255, 255, 255, 0.9);">
                Transform your eating habits with intelligent meal tracking and personalized nutrition insights.
            </p>
            <div style="border-top: 1px solid rgba(255, 255, 255, 0.15); padding-top: 12px;">
                <ul style="list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px;">
                    <li style="display: flex; align-items: center; gap: 10px; font-size: 0.93em; opacity: 0.9;">
                        <span style="font-size: 1.35em;">📸</span>
                        <span style="font-weight: 500;">Smart meal logging (text or photo)</span>
                    </li>
                    <li style="display: flex; align-items: center; gap: 10px; font-size: 0.93em; opacity: 0.9;">
                        <span style="font-size: 1.35em;">📊</span>
                        <span style="font-weight: 500;">Instant nutritional analysis</span>
                    </li>
                    <li style="display: flex; align-items: center; gap: 10px; font-size: 0.93em; opacity: 0.9;">
                        <span style="font-size: 1.35em;">📈</span>
                        <span style="font-weight: 500;">Habit tracking and progress monitoring</span>
                    </li>
                    <li style="display: flex; align-items: center; gap: 10px; font-size: 0.93em; opacity: 0.9;">
                        <span style="font-size: 1.35em;">💡</span>
                        <span style="font-weight: 500;">AI-powered personalized suggestions</span>
                    </li>
                    <li style="display: flex; align-items: center; gap: 10px; font-size: 0.93em; opacity: 0.9;">
                        <span style="font-size: 1.35em;">🎮</span>
                        <span style="font-weight: 500;">Gamification with badges and streaks</span>
                    </li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.markdown("#### Login to your account")
            
            email = st.text_input("Email", key="login_email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", key="login_password", placeholder="••••••••")
            
            if st.button("Login", key="login_btn", use_container_width=True):
                if email and password:
                    success, message, user_data = auth_manager.login(email, password)
                    if success:
                        st.session_state.user_id = user_data["user_id"]
                        st.session_state.user_email = user_data["email"]
                        # Normalize the profile data immediately
                        normalized_profile = normalize_profile(user_data)
                        st.session_state.user_profile = normalized_profile
                        show_notification("Login successful! Redirecting...", "success", use_toast=False)
                        st.rerun()
                    else:
                        show_notification(message, "error", use_toast=False)
                else:
                    show_notification("Please enter email and password", "warning", use_toast=False)
            
            # Forgot password button - same width as login button
            st.markdown("""
            <p style="text-align: center; color: #c0d5d3; margin-top: 12px; font-size: 0.8em;">
                Don't have an account? Create one in the Sign Up tab ↗️
            </p>
            """, unsafe_allow_html=True)
        
        with tab2:
            st.markdown("#### Create new account")
            
            new_email = st.text_input("Email", key="signup_email", placeholder="your@email.com")
            full_name = st.text_input("Full Name", key="signup_name", placeholder="John Doe")
            new_password = st.text_input("Password", type="password", key="signup_password", placeholder="••••••••")
            
            st.caption("Password must be at least 6 characters")
            
            if st.button("Sign Up", key="signup_btn", use_container_width=True):
                if new_email and new_password and full_name:
                    if len(new_password) < 6:
                        show_notification("Password must be at least 6 characters", "error", use_toast=False)
                    else:
                        success, message = auth_manager.sign_up(new_email, new_password, full_name)
                        if success:
                            show_notification("Account created! Please login with your credentials.", "success", use_toast=False)
                        else:
                            show_notification(message, "error", use_toast=False)
                else:
                    show_notification("Please fill all fields", "warning", use_toast=False)
            
            st.markdown("""
            <p style="text-align: center; color: #c0d5d3; margin-top: 12px; font-size: 0.8em;">
                Already have an account? Login in the Login tab ↖️
            </p>
            """, unsafe_allow_html=True)


def dashboard_page(prefetched_data: Optional[dict] = None):
    """Dashboard/Home page"""
    # Get user profile (handles loading and caching automatically)
    user_profile = get_or_load_user_profile()
    user_timezone = user_profile.get("timezone", "UTC")
    st.markdown(f"# {get_greeting(user_timezone)} 👋")

    # Pull prefetched data when available to avoid redundant DB calls
    today = prefetched_data.get("today") if prefetched_data else date.today()

    meals = prefetched_data.get("meals_today") if prefetched_data else None
    if meals is None:
        meals = db_manager.get_meals_by_date(st.session_state.user_id, today)

    daily_nutrition = prefetched_data.get("daily_nutrition") if prefetched_data else None
    if daily_nutrition is None:
        daily_nutrition = db_manager.get_daily_nutrition_summary(st.session_state.user_id, today) or {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "sodium": 0,
            "sugar": 0,
            "fiber": 0,
        }

    targets = prefetched_data.get("targets") if prefetched_data else None
    if targets is None:
        targets = calculate_personal_targets(user_profile)

    water_intake = prefetched_data.get("water_intake") if prefetched_data else None
    if water_intake is None:
        water_intake = db_manager.get_daily_water_intake(st.session_state.user_id, today)

    recent_meals = None
    recent_meal_dates = None
    if prefetched_data:
        recent_meals = prefetched_data.get("recent_meals_7d") or prefetched_data.get("recent_meals")
        recent_meal_dates = prefetched_data.get("recent_meal_dates_7d") or prefetched_data.get("recent_meal_dates")

    if recent_meals is None:
        start_date = today - timedelta(days=7)
        recent_meals = db_manager.get_meals_in_range(st.session_state.user_id, start_date, today)

    if recent_meal_dates is None:
        recent_meal_dates = []
        for meal in recent_meals:
            try:
                recent_meal_dates.append(datetime.fromisoformat(meal.get("logged_at", "")))
            except Exception:
                continue

    streak_info = prefetched_data.get("streak_info") if prefetched_data else None
    if streak_info is None:
        streak_info = get_streak_info(recent_meal_dates)

    current_streak = streak_info.get('current_streak', 0)
    longest_streak = streak_info.get('longest_streak', 0)
    
    # Motivational notifications (as persistent boxes below greeting)
    if current_streak >= 7 and current_streak % 7 == 0:
        st.success(f"🎉 **Amazing!** You've achieved a {current_streak}-day streak! Keep up the great work!")
    elif current_streak >= 3:
        st.info(f"🔥 **Nice!** You're on a {current_streak}-day streak! Log a meal today to keep it going!")
    elif current_streak == 1:
        st.info(f"🌟 **Great start!** You're 1 day in. Tomorrow's the test!")
    elif current_streak == 0 and len(meals) == 0:
        st.warning(f"📝 Don't forget to log a meal today to start building your streak!")
    
    # Milestone notifications
    if longest_streak == 30:
        st.success("🏆 **Congratulations!** You've hit a 30-day streak! You're a nutrition champion!")
    elif longest_streak == 14:
        st.info("🎯 **Epic!** 14-day record! You're committed to your health!")
    
    # Add spacing divider
    st.markdown("")
    
    # ===== Statistics & Achievements (Top Section) =====
    # Prepare data for statistics using utility function
    nutrition_by_date = build_nutrition_by_date(recent_meals)
    
    # Convert to DataFrame for statistics
    df = pd.DataFrame(list(nutrition_by_date.items()), columns=["Date", "Nutrition"])
    df["calories"] = df["Nutrition"].apply(lambda x: x["calories"])
    df["protein"] = df["Nutrition"].apply(lambda x: x["protein"])
    df["carbs"] = df["Nutrition"].apply(lambda x: x["carbs"])
    df["fat"] = df["Nutrition"].apply(lambda x: x["fat"])
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    
    # Display Statistics with Modern Card Layout
    # Add responsive CSS for mobile view - 2 cards per row on mobile
    st.markdown(
        """
        <style>
            @media (max-width: 640px) {
                /* Force 2 columns on mobile for stat cards */
                [data-testid="column"] {
                    flex: 0 1 calc(50% - 8px) !important;
                }
                
                /* Reduce padding in cards on mobile */
                [style*="padding: 16px"] {
                    padding: 12px !important;
                }
                
                /* Reduce font sizes on mobile */
                [style*="font-size: 24px"] {
                    font-size: 18px !important;
                }
                
                [style*="font-size: 32px"] {
                    font-size: 24px !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("## 🏆 Achievements & Quick Stats")
    
    achieve_cols = st.columns(2, gap="small")
    
    # Current Streak Card
    with achieve_cols[0]:
        streak_emoji = "🔥" if current_streak > 0 else "⭕"
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, rgba(255, 103, 21, 0.15), rgba(255, 140, 70, 0.08)); border: 1px solid rgba(255, 103, 21, 0.5); border-radius: 20px; padding: 28px 20px; text-align: center; min-height: 180px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
            <div style="font-size: 48px; margin-bottom: 12px;">{streak_emoji}</div>
            <div style="font-size: 10px; color: #94A3B8; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 10px; font-weight: 700;">Current Streak</div>
            <div style="font-size: 44px; font-weight: 900; color: #FFB84D; margin-bottom: 8px;">{current_streak}</div>
            <div style="font-size: 12px; color: #FF8C46; font-weight: 600;">days in a row</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Longest Streak Card
    with achieve_cols[1]:
        longest_streak = streak_info['longest_streak']
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, rgba(255, 212, 59, 0.12), rgba(255, 201, 77, 0.06)); border: 1px solid rgba(255, 212, 59, 0.4); border-radius: 20px; padding: 28px 20px; text-align: center; min-height: 180px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
            <div style="font-size: 48px; margin-bottom: 12px;">🏅</div>
            <div style="font-size: 10px; color: #94A3B8; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 10px; font-weight: 700;">Longest Streak</div>
            <div style="font-size: 44px; font-weight: 900; color: #FFD43B; margin-bottom: 8px;">{longest_streak}</div>
            <div style="font-size: 12px; color: #FFC94D; font-weight: 600;">personal record</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display XP Level
    st.markdown("### 🎮 Experience & Level")
    user_level = db_manager.get_user_level(st.session_state.user_id)
    xp_progress = db_manager.get_user_xp_progress(st.session_state.user_id)
    GamificationManager.render_xp_progress(
        user_level,
        xp_progress.get("current_xp", 0),
        xp_progress.get("xp_needed", 100)
    )
    
    # Display Daily Challenges
    daily_challenges = GamificationManager.calculate_daily_challenges(db_manager, st.session_state.user_id, user_profile)
    
    # Update challenge progress
    completed_challenges = GamificationManager.update_challenge_progress(
        db_manager, st.session_state.user_id, daily_nutrition, targets, water_intake
    )
    
    GamificationManager.render_daily_challenges(daily_challenges, completed_challenges)
    
    # Display Weekly Goals
    week_start = GamificationManager.get_week_start_date(today)
    db_manager.create_weekly_goals(st.session_state.user_id, week_start)
    weekly_goal = db_manager.get_weekly_goals(st.session_state.user_id, week_start)
    GamificationManager.render_weekly_goals(weekly_goal)
    
    # Display earned badges
    if user_profile.get("badges_earned"):
        st.markdown("### 🎖️ Earned Badges")
        badges_earned = get_earned_badges(user_profile.get("badges_earned", []))
        badge_cols = st.columns(min(len(badges_earned), 4), gap="medium")
        
        for idx, (badge_id, badge_info) in enumerate(badges_earned.items()):
            if idx < len(badge_cols):
                with badge_cols[idx]:
                    st.markdown(f"""
                    <div class="badge-achievement" style="
                        background: linear-gradient(135deg, #10A19D20 0%, #52C4B840 100%);
                        border: 1px solid #10A19D;
                        border-left: 4px solid #10A19D;
                        border-radius: 10px;
                        padding: 12px;
                        text-align: center;
                        box-shadow: 0 4px 12px rgba(16, 161, 157, 0.2);
                    ">
                        <div style="font-size: 28px; margin-bottom: 6px;">{badge_info.get('icon', '🏆')}</div>
                        <div style="font-size: 11px; font-weight: bold; color: #e0f2f1; margin-bottom: 4px;">{badge_info.get('name', 'Badge')}</div>
                        <div style="font-size: 9px; color: #a0a0a0;">{badge_info.get('description', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # ===== WATER INTAKE TRACKER + QUICK STATS (2-COLUMN) =====
    st.markdown("## 💧 Hydration & Energy Status")
    
    quick_stats_col1, quick_stats_col2 = st.columns(2, gap="medium")
    
    # Water Intake Card (Left)
    with quick_stats_col1:
        # Get water intake data
        water_goal = user_profile.get("water_goal_glasses", 8)
        current_water = water_intake
        water_percentage = min((current_water / water_goal) * 100, 100) if water_goal > 0 else 0
        
        # Determine water status
        if current_water >= water_goal:
            water_status = "🎉 Daily goal achieved!"
            water_status_color = "#4ADE80"
            water_bg = "linear-gradient(145deg, rgba(74, 222, 128, 0.12) 0%, rgba(34, 197, 94, 0.06) 100%)"
            water_border = "rgba(74, 222, 128, 0.5)"
            water_glow = "0 0 30px rgba(74, 222, 128, 0.25)"
        elif current_water >= water_goal * 0.75:
            water_status = "💪 Almost there! Keep going!"
            water_status_color = "#60A5FA"
            water_bg = "linear-gradient(145deg, rgba(96, 165, 250, 0.12) 0%, rgba(59, 130, 246, 0.06) 100%)"
            water_border = "rgba(96, 165, 250, 0.5)"
            water_glow = "0 0 30px rgba(96, 165, 250, 0.25)"
        else:
            water_status = "💧 Stay hydrated!"
            water_status_color = "#60A5FA"
            water_bg = "linear-gradient(145deg, rgba(96, 165, 250, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%)"
            water_border = "rgba(96, 165, 250, 0.4)"
            water_glow = "0 0 20px rgba(96, 165, 250, 0.2)"
        
        # Water glasses visualization
        glasses_display = ""
        for i in range(water_goal):
            if i < current_water:
                glasses_display += '<span style="font-size: 18px; margin: 0 2px; filter: drop-shadow(0 2px 4px rgba(96, 165, 250, 0.5));">💧</span>'
            else:
                glasses_display += '<span style="font-size: 18px; margin: 0 2px; opacity: 0.3;">💧</span>'
        
        # Water intake card
        st.markdown(f"""
        <div class="dashboard-info-box" style="background: {water_bg}; border: 1px solid {water_border}; border-radius: 20px; padding: 24px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2), {water_glow}, inset 0 1px 0 rgba(255, 255, 255, 0.08); margin-bottom: 12px; position: relative; overflow: hidden; backdrop-filter: blur(10px);">
            <div style="position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, {water_status_color}60, transparent);"></div>
            <div style="position: absolute; top: -30%; right: -20%; width: 50%; height: 80%; background: radial-gradient(circle, {water_status_color}08 0%, transparent 70%); pointer-events: none;"></div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 28px; filter: drop-shadow(0 2px 6px rgba(96, 165, 250, 0.4));">💧</span>
                    <span style="color: #F1F5F9; font-weight: 700; font-size: 16px;">Water Intake</span>
                </div>
                <span style="color: {water_status_color}; font-weight: 800; font-size: 18px; font-family: JetBrains Mono, monospace; text-shadow: 0 2px 8px {water_status_color}40;">{current_water}/{water_goal}</span>
            </div>
            <div style="margin-bottom: 16px; text-align: center; line-height: 1.8;">{glasses_display}</div>
            <div style="background: rgba(15, 23, 42, 0.5); border-radius: 12px; height: 12px; overflow: hidden; margin-bottom: 16px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.4);">
                <div style="background: linear-gradient(90deg, #3B82F6, #60A5FA, #93C5FD); height: 100%; width: {water_percentage}%; border-radius: 12px; transition: width 0.5s; box-shadow: 0 0 15px rgba(96, 165, 250, 0.5);"></div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: {water_status_color}; font-weight: 600; font-size: 13px;">{water_status}</span>
                <span style="color: #94A3B8; font-size: 12px; font-weight: 600; background: rgba(0,0,0,0.3); padding: 4px 10px; border-radius: 20px;">{water_percentage:.0f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Water action buttons
        water_btn_col1, water_btn_col2, water_btn_col3 = st.columns(3, gap="small")
        
        with water_btn_col1:
            if st.button("➕ Add", key="add_water_btn", use_container_width=True):
                if db_manager.log_water(st.session_state.user_id, 1, today):
                    st.toast("✅ Glass added!", icon="💧")
                    st.rerun()
                else:
                    st.toast("❌ Failed to log water", icon="⚠️")
        
        with water_btn_col2:
            if st.button("➖ Remove", key="remove_water_btn", use_container_width=True):
                if current_water > 0:
                    if db_manager.log_water(st.session_state.user_id, -1, today):
                        st.toast("✅ Removed 1 glass", icon="💧")
                        st.rerun()
                    else:
                        st.toast("❌ Failed to remove water", icon="⚠️")
                else:
                    st.toast("⚠️ No water logged yet", icon="💧")
        
        with water_btn_col3:
            if st.button("🏁 Complete", key="fill_water_btn", disabled=(current_water >= water_goal), use_container_width=True):
                remaining = max(0, water_goal - current_water)
                if remaining > 0 and db_manager.log_water(st.session_state.user_id, remaining, today):
                    st.toast(f"✅ Added {remaining} glasses!", icon="🎉")
                    st.rerun()
                else:
                    st.toast("❌ Failed to complete water goal", icon="⚠️")
    
    # Quick Calories Card (Right)
    with quick_stats_col2:
        cal_value = int(daily_nutrition['calories'])
        cal_target = targets.get("calories", 2000)
        cal_percentage = calculate_nutrition_percentage(cal_value, cal_target)
        
        # Determine calorie status
        if cal_percentage > 100:
            cal_status = "⚡ Above target"
            cal_color = "#4ADE80"
            cal_glow = "0 0 20px rgba(74, 222, 128, 0.2)"
        elif cal_percentage >= 80:
            cal_color = "#4ADE80"
            cal_status = "✅ On track"
            cal_glow = "0 0 20px rgba(74, 222, 128, 0.2)"
        elif cal_percentage >= 50:
            cal_color = "#FBBF24"
            cal_status = "⚠️ Below target"
            cal_glow = "0 0 20px rgba(251, 191, 36, 0.2)"
        else:
            cal_color = "#F87171"
            cal_status = "📉 Well below"
            cal_glow = "0 0 20px rgba(248, 113, 113, 0.2)"
            cal_gradient = "linear-gradient(90deg, #F87171, #EF4444)"
        
        cal_dash = min(cal_percentage, 100) * 2.64
        st.markdown(f"""
        <div class="dashboard-info-box" style="background: linear-gradient(145deg, {cal_color}12 0%, {cal_color}06 100%); border: 1px solid {cal_color}50; border-radius: 20px; padding: 24px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2), {cal_glow}, inset 0 1px 0 rgba(255, 255, 255, 0.08); margin-bottom: 12px; position: relative; overflow: hidden; backdrop-filter: blur(10px);">
            <div style="position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, {cal_color}60, transparent);"></div>
            <div style="position: absolute; top: -30%; left: -20%; width: 50%; height: 80%; background: radial-gradient(circle, {cal_color}08 0%, transparent 70%); pointer-events: none;"></div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 28px; filter: drop-shadow(0 2px 6px {cal_color}60);">🔥</span>
                    <span style="color: #F1F5F9; font-weight: 700; font-size: 16px;">Daily Calories</span>
                </div>
                <span style="color: {cal_color}; font-weight: 800; font-size: 18px; font-family: JetBrains Mono, monospace; text-shadow: 0 2px 8px {cal_color}40;">{cal_value}/{cal_target}</span>
            </div>
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="display: inline-block; position: relative; width: 100px; height: 100px;">
                    <svg viewBox="0 0 100 100" style="transform: rotate(-90deg); width: 100px; height: 100px;"><circle cx="50" cy="50" r="42" fill="none" stroke="rgba(15, 23, 42, 0.6)" stroke-width="8"/><circle cx="50" cy="50" r="42" fill="none" stroke="{cal_color}" stroke-width="8" stroke-dasharray="{cal_dash} 264" stroke-linecap="round" style="filter: drop-shadow(0 0 6px {cal_color}80);"/></svg>
                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;"><div style="font-size: 20px; font-weight: 800; color: {cal_color}; font-family: JetBrains Mono, monospace;">{cal_percentage:.0f}%</div></div>
                </div>
            </div>
            <div style="display: flex; justify-content: center; align-items: center;"><span style="color: {cal_color}; font-weight: 600; font-size: 14px; background: {cal_color}15; padding: 6px 14px; border-radius: 20px; border: 1px solid {cal_color}30;">{cal_status}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # ===== Quick Stats =====
    st.markdown("## 📊 Today's Nutrition Summary")
    
    # Unified nutrition cards with all key info + progress bars
    # Note: Calories is now shown in "Hydration & Energy Status" section above, so removed from here
    nutrition_cards = [
        {
            "icon": "💪",
            "label": "Protein",
            "value": f"{daily_nutrition['protein']:.1f}",
            "target": targets["protein"],
            "percentage": calculate_nutrition_percentage(daily_nutrition["protein"], targets["protein"]),
            "unit": "g",
            "base_color": "#8B5CF6",
            "gradient": "linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%)"
        },
        {
            "icon": "🥗",
            "label": "Carbs",
            "value": f"{daily_nutrition['carbs']:.1f}",
            "target": targets["carbs"],
            "percentage": calculate_nutrition_percentage(daily_nutrition["carbs"], targets["carbs"]),
            "unit": "g",
            "base_color": "#F59E0B",
            "gradient": "linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%)"
        },
        {
            "icon": "🧈",
            "label": "Fat",
            "value": f"{daily_nutrition['fat']:.1f}",
            "target": targets["fat"],
            "percentage": calculate_nutrition_percentage(daily_nutrition["fat"], targets["fat"]),
            "unit": "g",
            "base_color": "#10B981",
            "gradient": "linear-gradient(135deg, #10B981 0%, #34D399 100%)"
        },
        {
            "icon": "🧂",
            "label": "Sodium",
            "value": f"{daily_nutrition['sodium']:.0f}",
            "target": targets["sodium"],
            "percentage": calculate_nutrition_percentage(daily_nutrition["sodium"], targets["sodium"]),
            "unit": "mg",
            "base_color": "#EC4899",
            "gradient": "linear-gradient(135deg, #EC4899 0%, #F472B6 100%)"
        },
        {
            "icon": "🍬",
            "label": "Sugar",
            "value": f"{daily_nutrition['sugar']:.1f}",
            "target": targets["sugar"],
            "percentage": calculate_nutrition_percentage(daily_nutrition["sugar"], targets["sugar"]),
            "unit": "g",
            "base_color": "#EF4444",
            "gradient": "linear-gradient(135deg, #EF4444 0%, #F87171 100%)"
        }
    ]
    
    # Create 3-column grid for compact display
    cols = st.columns(3, gap="small")  # Compact spacing between cards
    
    for idx, card in enumerate(nutrition_cards):
        with cols[idx % 3]:
            percentage = card["percentage"]
            
            # Determine color and status using refined palette
            if card["label"] in ["Sodium", "Sugar"]:
                # Harmful nutrients - red for exceeding
                if percentage > 100:
                    color = "#F87171"
                    gradient_color = "#EF4444"
                    status_icon = "⚠️"
                    status_text = f"Over by {percentage-100:.0f}%"
                    glow = "0 0 20px rgba(248, 113, 113, 0.2)"
                elif percentage >= 80:
                    color = "#FBBF24"
                    gradient_color = "#F59E0B"
                    status_icon = "⚠️"
                    status_text = f"{percentage:.0f}%"
                    glow = "0 0 20px rgba(251, 191, 36, 0.2)"
                else:
                    color = "#4ADE80"
                    gradient_color = "#22C55E"
                    status_icon = "✅"
                    status_text = f"{percentage:.0f}%"
                    glow = "0 0 20px rgba(74, 222, 128, 0.2)"
            else:
                # Good nutrients - green for on target
                if percentage > 100:
                    color = "#4ADE80"
                    gradient_color = "#22C55E"
                    status_icon = "⚡"
                    status_text = f"+{percentage-100:.0f}%"
                    glow = "0 0 20px rgba(74, 222, 128, 0.2)"
                elif percentage >= 80:
                    color = "#4ADE80"
                    gradient_color = "#22C55E"
                    status_icon = "✅"
                    status_text = f"{percentage:.0f}%"
                    glow = "0 0 20px rgba(74, 222, 128, 0.2)"
                else:
                    color = "#FBBF24"
                    gradient_color = "#F59E0B"
                    status_icon = "⚠️"
                    status_text = f"{percentage:.0f}%"
                    glow = "0 0 20px rgba(251, 191, 36, 0.2)"
            
            # Use macro-specific base color for background tint
            base_color = card.get("base_color", color)
            progress_gradient = card.get("gradient", f"linear-gradient(90deg, {color}, {gradient_color})")
            progress_width = min(percentage, 100)
            
            st.markdown(f"""
            <div class="nutrition-info" style="background: linear-gradient(145deg, {base_color}15 0%, {base_color}08 100%); border: 1px solid {base_color}30; border-radius: 20px; padding: 24px 16px; text-align: center; min-height: 210px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15), 0 0 20px {base_color}15, inset 0 1px 0 rgba(255, 255, 255, 0.05); position: relative; overflow: hidden; backdrop-filter: blur(10px);">
                <div style="position: absolute; top: 0; left: 0; right: 0; height: 1px; background: linear-gradient(90deg, transparent, {base_color}50, transparent);"></div>
                <div style="position: absolute; top: -40%; right: -40%; width: 80%; height: 80%; background: radial-gradient(circle, {base_color}10 0%, transparent 70%); pointer-events: none;"></div>
                <div><div style="font-size: 40px; margin-bottom: 8px; filter: drop-shadow(0 4px 8px {base_color}40);">{card['icon']}</div><div style="font-size: 10px; color: #94A3B8; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 6px; font-weight: 700;">{card['label']}</div></div>
                <div><div style="font-size: 34px; font-weight: 800; color: #F1F5F9; margin-bottom: 6px; letter-spacing: -0.02em; font-family: JetBrains Mono, monospace; text-shadow: 0 2px 8px rgba(0,0,0,0.3);">{card['value']}<span style="font-size: 13px; font-weight: 500; color: #94A3B8;">{card['unit']}</span></div><div style="background: rgba(15, 23, 42, 0.5); border-radius: 10px; height: 8px; margin: 12px 0; box-shadow: inset 0 2px 4px rgba(0,0,0,0.4);"><div style="background: {progress_gradient}; height: 100%; width: {progress_width}%; border-radius: 10px; box-shadow: 0 0 12px {base_color}60;"></div></div><div style="font-size: 11px; color: #64748B; margin-bottom: 8px;">of {card['target']}{card['unit']}</div></div>
                <div style="font-size: 12px; color: {color}; font-weight: 700; background: {color}15; padding: 4px 12px; border-radius: 20px; display: inline-block;">{status_icon} {status_text}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # ===== MACRO BREAKDOWN & INSIGHTS =====
    st.markdown("")
    st.markdown("## 📊 Nutrition Breakdown")

    # Use a single full-width container for the breakdown section
    breakdown_col1 = st.container()

    # MACRO BALANCE - full width
    with breakdown_col1:
        st.markdown("""
        <div class="macro-box dashboard-info-box" style="
            background: linear-gradient(135deg, rgba(16, 161, 157, 0.1) 0%, rgba(255, 107, 22, 0.05) 100%);
            border: 1px solid rgba(16, 161, 157, 0.3);
            border-radius: 12px;
            padding: 24px;
        ">
            <h3 style="color: #e0f2f1; margin-top: 0; font-size: 18px;">🔥 Today's Macro Balance</h3>
        """, unsafe_allow_html=True)
        
        if daily_nutrition['protein'] > 0 or daily_nutrition['carbs'] > 0 or daily_nutrition['fat'] > 0:
            macro_data = {
                "Nutrient": ["Protein", "Carbs", "Fat"],
                "Grams": [
                    daily_nutrition['protein'],
                    daily_nutrition['carbs'],
                    daily_nutrition['fat']
                ]
            }
            
            fig_macro = px.pie(
                macro_data,
                values="Grams",
                names="Nutrient",
                color_discrete_map={"Protein": "#51CF66", "Carbs": "#FFD43B", "Fat": "#FF6B6B"}
            )
            fig_macro.update_traces(textinfo="percent+label", textposition="inside")
            fig_macro.update_layout(
                showlegend=True,
                height=280,
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#e0f2f1'
            )
            st.plotly_chart(fig_macro, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("📊 Log some meals to see your macro balance!")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Right column removed — this section is now full-width.
    
    # Remove duplicate EATING TIME PATTERNS section that was below
    
    # ===== Today's Meals =====
    st.markdown("## 🍽️ Today's Meals")
    
    if meals:
        for meal in meals:
            st.markdown(f"""
            <div class="meal-card" style="
                background: linear-gradient(135deg, #10A19D15 0%, #52C4B825 100%);
                border: 2px solid #10A19D;
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 12px;
                box-shadow: 0 4px 12px rgba(16, 161, 157, 0.15);
            ">
                <div style="display: flex; justify-content: space-between; align-items: start; gap: 12px;">
                    <div style="flex: 1;">
                        <div style="font-size: 14px; font-weight: bold; color: #e0f2f1; margin-bottom: 4px;">
                            🍴 {meal.get('meal_name', 'Unknown Meal')} <span style="font-size: 12px; color: #a0a0a0;">• {meal.get('meal_type', 'meal')}</span>
                        </div>
                        <div style="font-size: 11px; color: #7a8a89;">Logged at: {meal.get('logged_at', 'N/A')}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show meal details in expander
            with st.expander(f"📋 View Details - {meal.get('meal_name', 'Meal')}", expanded=False):
                st.write(f"**Description:** {meal.get('description', 'N/A')}")
                nutrition = meal.get("nutrition", {})
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    show_nutrition_facts(nutrition)
                with col2:
                    healthiness = meal.get('healthiness_score', 'N/A')
                    st.metric("Score", healthiness)
    else:
        st.info("No meals logged yet. Start by logging a meal!")
    
    # Daily Insight is now displayed in sidebar


def meal_logging_page():
    """Meal logging page"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0D847F 0%, #10A19D 50%, #52C4B8 100%);
        padding: 24px 32px;
        border-radius: 16px;
        margin: -1rem -1rem 24px -1rem;
        box-shadow: 
            0 8px 32px rgba(16, 161, 157, 0.3),
            inset 0 1px 1px rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.15);
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 100% 0%, rgba(255, 255, 255, 0.15) 0%, transparent 50%);
            pointer-events: none;
        "></div>
        <h1 style="
            color: white; 
            margin: 0; 
            font-size: 1.75em; 
            font-weight: 700;
            line-height: 1.2;
            position: relative;
            z-index: 1;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <span style="font-size: 1.3em;">📸</span>
            <span>Log Your Meal</span>
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== TIME-BASED SUGGESTIONS =====
    from datetime import datetime as dt
    import pytz
    
    # Get user profile (handles loading and caching automatically)
    user_profile = get_or_load_user_profile()
    user_timezone = user_profile.get("timezone", "UTC")
    
    try:
        tz = pytz.timezone(user_timezone)
        current_time = dt.now(tz)
        current_hour = current_time.hour
    except (pytz.exceptions.UnknownTimeZoneError, AttributeError):
        current_hour = dt.now(pytz.UTC).hour
    
    if 6 <= current_hour < 10:
        suggestion = "🌅 Good morning! It's breakfast time. Fuel your day with a healthy breakfast!"
        suggested_type = "breakfast"
    elif 10 <= current_hour < 15:
        suggestion = "🍴 It's lunch time! Time to refuel with a balanced meal!"
        suggested_type = "lunch"
    elif 15 <= current_hour < 21:
        suggestion = "🌙 Dinner time approaches! What's for dinner?"
        suggested_type = "dinner"
    else:
        suggestion = "🍿 Looking for a snack? Log what you're having!"
        suggested_type = "snack"
    
    st.info(suggestion)
    
    # ===== QUICK ADD FROM HISTORY =====
    st.markdown("### 🚀 Quick Add From History")
    
    # Get recent meals for quick add
    recent_meals = db_manager.get_recent_meals(st.session_state.user_id, limit=10)
    
    if recent_meals:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            meal_options = {f"{m.get('meal_name')} ({m.get('meal_type')})" : m for m in recent_meals}
            selected_quick_meal = st.selectbox(
                "Select a meal you've had before",
                options=list(meal_options.keys()),
                format_func=lambda x: x,
                label_visibility="collapsed",
                key="quick_add_selector"
            )
        
        with col2:
            if st.button("➕ Quick Add", key="quick_add_btn", use_container_width=True):
                st.session_state.show_quick_add_form = True
        
        # Show quick add form with time selection
        if st.session_state.get("show_quick_add_form", False):
            st.markdown("---")
            st.subheader("Add Quick Meal")
            
            meal = meal_options[selected_quick_meal]
            
            # Date and time selection for quick add
            col1, col2 = st.columns(2)
            with col1:
                quick_date = st.date_input(
                    "Select date",
                    value=date.today(),
                    max_value=date.today(),
                    key="quick_add_date"
                )
            with col2:
                quick_time = st.time_input(
                    "Select time",
                    value=datetime.now().time(),
                    key="quick_add_time"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirm", key="quick_add_confirm", use_container_width=True):
                    meal_data = {
                        "user_id": st.session_state.user_id,
                        "meal_name": meal.get('meal_name', 'Unknown'),
                        "description": meal.get('description', ''),
                        "meal_type": meal.get('meal_type'),
                        "nutrition": meal.get('nutrition', {}),
                        "healthiness_score": meal.get('healthiness_score', 0),
                        "health_notes": meal.get('health_notes', ''),
                        "logged_at": datetime.combine(quick_date, quick_time).isoformat(),
                    }
                    
                    if db_manager.log_meal(meal_data):
                        db_manager.add_xp(st.session_state.user_id, GamificationManager.XP_REWARDS['meal_logged'])
                        st.session_state.show_quick_add_form = False
                        st.toast("Meal added! +25 XP", icon="✅")
                        st.rerun()
                    else:
                        st.toast("Failed to add meal", icon="❌")
            with col2:
                if st.button("❌ Cancel", key="quick_add_cancel", use_container_width=True):
                    st.session_state.show_quick_add_form = False
        
        st.divider()
    
    st.markdown("""
    ### Choose how you'd like to log your meal:
    1. **Text Description** - Describe your meal in words
    2. **Photo** - Take a photo of your meal
    3. **Batch Log** - Log multiple meals for past days
    """)
    
    # Quick reference help section
    with st.expander("📖 Portion Estimation Guide - How We Estimate Meals", expanded=False):
        st.markdown("""
        ### Accuracy Levels
        
        **HIGH (±15%)** - You provide exact measurements
        - "150g chicken, 200g rice, 1 tbsp oil"
        
        **MEDIUM (±20-25%)** - You describe portions generally  
        - "A bowl of rice with some chicken"
        
        **MEDIUM-LOW (±30-35%)** - Vague descriptions
        - "Some chicken and rice"
        
        **LOW (±40-50%)** - Photos without portion details
        - Photo only, no text description
        
        ### How to Improve Accuracy
        - **Use specific measurements:** grams, cups, tablespoons, not "some"
        - **Specify cooking method:** "grilled" vs "fried" (huge calorie difference!)
        - **Include condiments:** "2 tbsp olive oil dressing" not "with dressing"
        - **For photos:** Include a reference object (coin, hand, utensil) for scale
        - **List ingredients separately:** Not "stir fry" but "chicken + rice + vegetables"
        
        👉 See the full guide in Settings → Help → Portion Estimation Guide
        """)
    
    tab1, tab2, tab3 = st.tabs(["📝 Text", "📸 Photo", "📅 Batch Log"])
    
    with tab1:
        st.markdown("## 📝 Describe Your Meal")
        
        # CRITICAL: Warning box first to set expectations
        st.warning("""
        ⚠️ **Accuracy depends on detail level:**
        - **SPECIFIC** (±15%): "150g grilled chicken, 200g brown rice, 100g broccoli"
        - **GENERAL** (±25%): "chicken with rice and vegetables"  
        - **VAGUE** (±40-50%): "some chicken and rice"
        """)
        
        # Quick reference section - minimal and actionable
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""**Include:**
- Main ingredients
- Portion size/weight
- Cooking method""")
        with col2:
            st.markdown("""**Pro Tips:**
- Use grams/cups if possible
- Be specific, not vague
- Don't skip drinks/extras""")
        
        st.markdown("---")
        
        meal_description = st.text_area(
            "What did you eat?",
            placeholder="E.g., 150g grilled chicken breast, 200g brown rice, 100g broccoli, 1 tbsp olive oil",
            height=100
        )
        
        meal_type = st.selectbox(
            "Meal Type",
            options=list(MEAL_TYPES.keys()),
            format_func=lambda x: MEAL_TYPES.get(x, x)
        )
        
        if st.button("Analyze Meal", use_container_width=True):
            if meal_description:
                # Store description for confidence assessment
                st.session_state.meal_description = meal_description
                with st.spinner("🤖 Analyzing your meal..."):
                    analysis = nutrition_analyzer.analyze_text_meal(meal_description, meal_type)
                    
                    if analysis:
                        # Store analysis in session state so it persists
                        st.session_state.meal_analysis = analysis
                        st.session_state.meal_type = meal_type
                        st.toast("Meal analyzed!", icon="✅")
                    else:
                        st.toast("Could not analyze meal. Please try again.", icon="❌")
            else:
                st.toast("Please describe your meal", icon="⚠️")
        
        # Display analysis if it exists in session state
        if "meal_analysis" in st.session_state:
            analysis = st.session_state.meal_analysis
            meal_type = st.session_state.meal_type
            
            st.markdown(f"### {analysis.get('meal_name', 'Meal')}")
            st.write(analysis.get('description', ''))
            
            # Show confidence level and disclaimer for text input
            if "meal_description" in st.session_state:
                confidence_level = assess_input_confidence(st.session_state.get("meal_description", ""), has_photo=False)
                st.session_state.text_confidence_level = confidence_level
                show_estimation_disclaimer(st, confidence_level, input_type="text")
            elif "text_confidence_level" in st.session_state:
                show_estimation_disclaimer(st, st.session_state.text_confidence_level, input_type="text")
            
            # Portion estimation reference (grouped with confidence section)
            with st.expander("📚 Common Portion Sizes", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("""**Proteins:**
- Chicken breast: 100-200g
- Fish: 100-150g
- Egg: 50g
- Cheese: 30-50g""")
                with col2:
                    st.markdown("""**Grains & Carbs:**
- Rice (cooked): 150-200g
- Bread: 1 slice = 30g
- Pasta: 150-200g
- Potato: 150g""")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                show_nutrition_facts(analysis['nutrition'])
            
            with col2:
                healthiness = analysis.get('healthiness_score', 0)
                st.metric("Healthiness Score", f"{healthiness}/100")
            
            st.info(f"**Health Notes:** {analysis.get('health_notes', 'N/A')}")
            
            # Date and time selector
            st.markdown("### 📅 When did you eat this?")
            col1, col2 = st.columns(2)
            with col1:
                meal_date = st.date_input(
                    "Select date",
                    value=date.today(),
                    max_value=date.today(),
                    help="You can log meals from past dates",
                    key="text_meal_date"
                )
            with col2:
                meal_time = st.time_input(
                    "Select time",
                    value=datetime.now().time(),
                    help="What time did you eat this meal?",
                    key="text_meal_time"
                )
            
            # Save meal
            if st.button("Save This Meal", key="text_save_btn", use_container_width=True):
                meal_data = {
                    "user_id": st.session_state.user_id,
                    "meal_name": analysis.get('meal_name', 'Unknown'),
                    "description": analysis.get('description', ''),
                    "meal_type": meal_type,
                    "nutrition": analysis['nutrition'],
                    "healthiness_score": analysis.get('healthiness_score', 0),
                    "health_notes": analysis.get('health_notes', ''),
                    "logged_at": datetime.combine(meal_date, meal_time).isoformat(),
                }
                
                # Validate meal data before saving
                is_valid, error_msg = validate_meal_data(
                    meal_data["meal_name"],
                    meal_data["nutrition"],
                    meal_date
                )
                
                if not is_valid:
                    st.error(f"⚠️ Validation Error: {error_msg}")
                elif db_manager.log_meal(meal_data):
                    # Award XP for logging meal
                    db_manager.add_xp(st.session_state.user_id, GamificationManager.XP_REWARDS['meal_logged'])
                    # Clear the analysis from session state
                    del st.session_state.meal_analysis
                    del st.session_state.meal_type
                    st.toast("Meal saved! +25 XP", icon="✅")
                    st.rerun()
                else:
                    show_notification("Failed to save meal. Please check your internet connection and try again.", "error", use_toast=False)
    
    with tab2:
        st.markdown("## 📸 Upload Food Photo")
        
        st.info("""
        📸 **Photo tips for best results:**
        - Include a reference object for scale (coin, utensil, hand)
        - Photograph from above at ~45° angle
        - Use natural lighting for clarity
        - Include all food items in the frame
        - Add text description of portions if possible for better accuracy
        
        📁 **Supported formats:** JPG, JPEG, PNG | **Max file size:** 50 MB
        """)
        
        uploaded_file = st.file_uploader(
            "Choose a food photo",
            type=["jpg", "jpeg", "png"],
            help="Upload a clear photo of your meal (JPG/PNG, max 50 MB)"
        )
        
        meal_type = st.selectbox(
            "Meal Type",
            options=list(MEAL_TYPES.keys()),
            format_func=lambda x: MEAL_TYPES.get(x, x),
            key="photo_meal_type"
        )
        
        # Add text description for portions to improve accuracy
        portion_description = st.text_input(
            "Add text description of portions (optional)",
            placeholder="e.g., '150g chicken, 1 cup rice, medium apple'",
            help="Providing portion sizes or weights significantly improves accuracy"
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Your meal", use_column_width=True)
            
            if st.button("Analyze Photo", use_container_width=True):
                with st.spinner("🤖 Analyzing your photo..."):
                    image_data = uploaded_file.getvalue()
                    analysis = nutrition_analyzer.analyze_food_image(image_data)
                    
                    if analysis:
                        # Store analysis and portion description in session state
                        st.session_state.photo_analysis = analysis
                        st.session_state.photo_portion_description = portion_description
                        show_notification("Photo analyzed! Ready to save.", "success", use_toast=False)
                    else:
                        show_notification("Couldn't analyze photo. Try a clearer image with better lighting.", "error", use_toast=False)
        
        # Display analysis if it exists in session state
        if "photo_analysis" in st.session_state:
            analysis = st.session_state.photo_analysis
            # meal_type is already managed by the selectbox widget via key="photo_meal_type"
            
            # Display detected foods
            st.markdown("### Detected Foods")
            for food in analysis.get('detected_foods', []):
                st.write(f"- {food['name']} ({food['quantity']})")
            
            # Show confidence level and disclaimer for photo input
            # Include portion description if provided
            photo_text_description = st.session_state.get("photo_portion_description", "")
            confidence_level = assess_input_confidence(text_description=photo_text_description, has_photo=True)
            show_estimation_disclaimer(st, confidence_level, input_type="photo")
            
            # Display nutrition
            show_nutrition_facts(analysis['total_nutrition'], show_label=True)
            
            st.info(f"**AI Confidence:** {analysis.get('confidence', 0)}%")
            st.info(f"**Notes:** {analysis.get('notes', 'N/A')}")
            
            # Date and time selector
            st.markdown("### 📅 When did you eat this?")
            col1, col2 = st.columns(2)
            with col1:
                meal_date = st.date_input(
                    "Select date",
                    value=date.today(),
                    max_value=date.today(),
                    help="You can log meals from past dates",
                    key="photo_meal_date"
                )
            with col2:
                meal_time = st.time_input(
                    "Select time",
                    value=datetime.now().time(),
                    help="What time did you eat this meal?",
                    key="photo_meal_time"
                )
            
            # Save meal
            if st.button("Save This Meal", key="save_photo_meal", use_container_width=True):
                meal_data = {
                    "user_id": st.session_state.user_id,
                    "meal_name": f"Meal from photo",
                    "description": ", ".join([f"{f['name']} ({f['quantity']})" for f in analysis.get('detected_foods', [])]),
                    "meal_type": st.session_state.photo_meal_type,  # Use session state variable managed by selectbox
                    "nutrition": analysis['total_nutrition'],
                    "healthiness_score": 75,  # Default score
                    "health_notes": analysis.get('notes', ''),
                    "logged_at": datetime.combine(meal_date, meal_time).isoformat(),
                }
                
                # Validate meal data before saving
                is_valid, error_msg = validate_meal_data(
                    meal_data["meal_name"],
                    meal_data["nutrition"],
                    meal_date
                )
                
                if not is_valid:
                    st.error(f"⚠️ Validation Error: {error_msg}")
                elif db_manager.log_meal(meal_data):
                    # Award XP for logging meal
                    db_manager.add_xp(st.session_state.user_id, GamificationManager.XP_REWARDS['meal_logged'])
                    # Clear the analysis from session state
                    del st.session_state.photo_analysis
                    # Set flag to show success message on next render
                    st.session_state._photo_meal_saved = True
                    st.toast("Meal saved! +25 XP", icon="✅")
                    st.rerun()
                else:
                    show_notification("Failed to save meal. Please check your internet connection and try again.", "error", use_toast=False)
    
    with tab3:
        st.markdown("## 📅 Batch Log Meals")
        st.markdown("Log multiple meals for past days at once. Great for catching up!")
        
        # Date range selector
        col1, col2 = st.columns(2)
        
        with col1:
            batch_start_date = st.date_input(
                "Start Date",
                value=date.today() - timedelta(days=3),
                max_value=date.today(),
                key="batch_start_date"
            )
        
        with col2:
            batch_end_date = st.date_input(
                "End Date",
                value=date.today(),
                max_value=date.today(),
                key="batch_end_date"
            )
        
        st.markdown("---")
        
        # Generate calendar-like interface
        current_date = batch_start_date
        day_meals = {}
        
        while current_date <= batch_end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            st.markdown(f"### 📅 {current_date.strftime('%A, %B %d, %Y')}")
            
            meal_data_for_day = {}
            
            # Breakfast
            col1, col2 = st.columns([3, 1])
            with col1:
                breakfast_desc = st.text_input(
                    f"Breakfast",
                    placeholder="e.g., Oatmeal with berries",
                    key=f"batch_breakfast_desc_{date_str}"
                )
            with col2:
                breakfast_time = st.time_input(
                    "Time",
                    value=time(8, 0),
                    key=f"batch_breakfast_time_{date_str}"
                )
            meal_data_for_day["breakfast"] = {"desc": breakfast_desc, "time": breakfast_time}
            
            # Lunch
            col1, col2 = st.columns([3, 1])
            with col1:
                lunch_desc = st.text_input(
                    f"Lunch",
                    placeholder="e.g., Grilled chicken with vegetables",
                    key=f"batch_lunch_desc_{date_str}"
                )
            with col2:
                lunch_time = st.time_input(
                    "Time",
                    value=time(12, 0),
                    key=f"batch_lunch_time_{date_str}"
                )
            meal_data_for_day["lunch"] = {"desc": lunch_desc, "time": lunch_time}
            
            # Dinner
            col1, col2 = st.columns([3, 1])
            with col1:
                dinner_desc = st.text_input(
                    f"Dinner",
                    placeholder="e.g., Salmon with rice",
                    key=f"batch_dinner_desc_{date_str}"
                )
            with col2:
                dinner_time = st.time_input(
                    "Time",
                    value=time(19, 0),
                    key=f"batch_dinner_time_{date_str}"
                )
            meal_data_for_day["dinner"] = {"desc": dinner_desc, "time": dinner_time}
            
            day_meals[date_str] = meal_data_for_day
            st.markdown("---")
            
            current_date += timedelta(days=1)
        
        st.divider()
        
        st.divider()
        if st.button("📥 Analyze & Save All Meals", key="batch_save_btn", use_container_width=True):
            total_saved = 0
            total_failed = 0
            
            with st.spinner("🤖 Analyzing and saving meals..."):
                for date_str, meals_dict in day_meals.items():
                    for meal_type, meal_data_dict in meals_dict.items():
                        description = meal_data_dict.get("desc", "")
                        meal_time = meal_data_dict.get("time", time(12, 0))
                        
                        if description and description.strip():
                            # Analyze the meal
                            analysis = nutrition_analyzer.analyze_text_meal(description, meal_type)
                            
                            if analysis:
                                meal_data = {
                                    "user_id": st.session_state.user_id,
                                    "meal_name": analysis.get('meal_name', description[:50]),
                                    "description": analysis.get('description', description),
                                    "meal_type": meal_type,
                                    "nutrition": analysis['nutrition'],
                                    "healthiness_score": analysis.get('healthiness_score', 0),
                                    "health_notes": analysis.get('health_notes', ''),
                                    "logged_at": datetime.combine(
                                        datetime.fromisoformat(date_str).date(),
                                        meal_time
                                    ).isoformat(),
                                }
                                
                                if db_manager.log_meal(meal_data):
                                    # Award XP for logging meal
                                    db_manager.add_xp(st.session_state.user_id, GamificationManager.XP_REWARDS['meal_logged'])
                                    total_saved += 1
                                else:
                                    total_failed += 1
            
            show_notification(f"Saved {total_saved} meals successfully!", "success", use_toast=False)
            if total_failed > 0:
                show_notification(f"Failed to save {total_failed} meals", "warning", use_toast=False)
            st.rerun()


def analytics_page():
    """Analytics and insights page"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #6E48C7 0%, #845EF7 50%, #BE80FF 100%);
        padding: 24px 32px;
        border-radius: 16px;
        margin: -1rem -1rem 24px -1rem;
        box-shadow: 
            0 8px 32px rgba(132, 94, 247, 0.3),
            inset 0 1px 1px rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.15);
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 100% 0%, rgba(255, 255, 255, 0.15) 0%, transparent 50%);
            pointer-events: none;
        "></div>
        <h1 style="
            color: white; 
            margin: 0; 
            font-size: 1.75em; 
            font-weight: 700;
            line-height: 1.2;
            position: relative;
            z-index: 1;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <span style="font-size: 1.3em;">📈</span>
            <span>Analytics & Insights</span>
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Get user profile (handles loading and caching automatically)
    user_profile = get_or_load_user_profile()

    # Initialize days from session state or use default
    if "analytics_days" not in st.session_state:
        st.session_state.analytics_days = 7
    
    # Time period button options
    st.markdown("### Select time period")
    col1, col2, col3 = st.columns(3, gap="small")
    
    with col1:
        if st.button("Last Week", use_container_width=True, key="btn_7days"):
            st.session_state.analytics_days = 7
    
    with col2:
        if st.button("Last 2 weeks", use_container_width=True, key="btn_14days"):
            st.session_state.analytics_days = 14
    
    with col3:
        if st.button("Last 30 days", use_container_width=True, key="btn_30days"):
            st.session_state.analytics_days = 30
    
    # Get the selected number of days from session state
    days = st.session_state.analytics_days
    
    # Get data
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    meals = db_manager.get_meals_in_range(st.session_state.user_id, start_date, end_date)
    
    if not meals:
        st.info("No meals logged in this period")
        return
    
    # Get nutrition targets
    targets = calculate_personal_targets(user_profile)
    
    # ===== STATISTICS CARDS =====
    st.markdown("## 📊 Statistics")
    
    # Prepare data for stats
    df_list = []
    for meal in meals:
        meal_date = meal.get("logged_at", "").split("T")[0]
        nutrition = meal.get("nutrition", {})  # Fixed: was "Nutrition" with capital N
        df_list.append({
            "Date": meal_date,
            "calories": nutrition.get("calories", 0),
            "protein": nutrition.get("protein", 0),
            "carbs": nutrition.get("carbs", 0),
            "fat": nutrition.get("fat", 0)
        })
    df = pd.DataFrame(df_list)
    
    stats_cols = st.columns(4, gap="medium")
    
    # Avg Daily Calories Card
    with stats_cols[0]:
        avg_cal = df["calories"].mean() if len(df) > 0 else 0
        target_cal = targets['calories']
        cal_pct = (avg_cal / target_cal * 100) if target_cal > 0 else 0
        cal_status = "✅" if 80 <= cal_pct <= 120 else ("⚠️" if cal_pct < 80 else "⚡")
        render_stat_card(
            emoji="🔥",
            title="Avg Calories",
            value=f"{avg_cal:.0f}",
            subtitle=f"of {target_cal}",
            progress_value=cal_pct,
            status=f"{cal_status} {cal_pct:.0f}%",
            color="#FFB84D",
            shadow_color="rgba(255, 107, 22, 0.2)",
            gradient_start="#FF6B1620",
            gradient_end="#FF6B1640"
        )
    
    # Total Meals Card
    with stats_cols[1]:
        total_meals = len(meals)
        meals_status = "🔥" if total_meals >= 14 else ("✅" if total_meals >= 7 else "⚠️")
        meals_progress = min((total_meals / 21) * 100, 100)
        render_stat_card(
            emoji="🍽️",
            title="Total Meals",
            value=f"{total_meals}",
            subtitle=f"{days} days",
            progress_value=meals_progress,
            status=f"{meals_status} {(total_meals/days):.1f}/day",
            color="#5DDCD6",
            shadow_color="rgba(16, 161, 157, 0.2)",
            gradient_start="#10A19D20",
            gradient_end="#52C4B840"
        )
    
    # Avg Meals Per Day Card
    with stats_cols[2]:
        avg_meals_per_day = total_meals / days if days > 0 else 0
        meal_freq_status = "✅" if 2 <= avg_meals_per_day <= 4 else ("⚠️" if avg_meals_per_day < 2 else "⚡")
        render_stat_card(
            emoji="📈",
            title="Meals/Day",
            value=f"{avg_meals_per_day:.1f}",
            subtitle="avg",
            progress_value=min((avg_meals_per_day / 5) * 100, 100),
            status=meal_freq_status,
            color="#B89FFF",
            shadow_color="rgba(132, 94, 247, 0.2)",
            gradient_start="#845EF720",
            gradient_end="#BE80FF40"
        )
    
    # Avg Protein Card
    with stats_cols[3]:
        avg_protein = df["protein"].mean() if len(df) > 0 else 0
        target_protein = targets['protein']
        protein_pct = (avg_protein / target_protein * 100) if target_protein > 0 else 0
        protein_status = "✅" if 80 <= protein_pct <= 120 else ("⚠️" if protein_pct < 80 else "⚡")
        render_stat_card(
            emoji="💪",
            title="Avg Protein",
            value=f"{avg_protein:.1f}g",
            subtitle=f"of {target_protein}g",
            progress_value=protein_pct,
            status=f"{protein_status} {protein_pct:.0f}%",
            color="#7FDB8F",
            shadow_color="rgba(81, 207, 102, 0.2)",
            gradient_start="#51CF6620",
            gradient_end="#80C34240"
        )
    
    # ===== Nutrition Trends =====
    st.markdown("## 📊 Nutrition Trends")
    
    # Prepare data for charts using utility function
    nutrition_by_date = build_nutrition_by_date(meals)
    
    # Convert to DataFrame with proper date handling
    df = pd.DataFrame(list(nutrition_by_date.items()), columns=["Date", "Nutrition"])
    df["calories"] = df["Nutrition"].apply(lambda x: x["calories"])
    df["protein"] = df["Nutrition"].apply(lambda x: x["protein"])
    df["carbs"] = df["Nutrition"].apply(lambda x: x["carbs"])
    df["fat"] = df["Nutrition"].apply(lambda x: x["fat"])
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    
    # Calories chart
    fig_cal = px.line(
        df,
        x="Date",
        y="calories",
        title="Daily Calorie Intake",
        labels={"calories": "Calories", "Date": "Date"},
        markers=True
    )
    fig_cal.add_hline(y=targets["calories"], line_dash="dash", line_color="red", annotation_text="Target")
    st.plotly_chart(fig_cal, use_container_width=True)
    
    # Macronutrients chart
    fig_macro = px.bar(
        df,
        x="Date",
        y=["protein", "carbs", "fat"],
        title="Macronutrient Distribution",
        labels={"value": "Grams", "variable": "Nutrient"},
        barmode="group"
    )
    st.plotly_chart(fig_macro, use_container_width=True)


def show_meal_quality(meals):
    """Display best and worst meals quality section"""
    st.markdown("## 🏆 Your Meal Quality")
    
    # Sort meals by healthiness score
    sorted_meals = sorted(meals, key=lambda x: x.get('healthiness_score', 0), reverse=True)
    
    if sorted_meals:
        best_worst_col1, best_worst_col2 = st.columns(2)

        # Left: Healthiest Meals (styled container)
        with best_worst_col1:
            healthiest = sorted_meals[:3]
            items_html = ""
            for idx, meal in enumerate(highest := healthiest, 1):
                name = meal.get('meal_name', 'Unknown')
                score = meal.get('healthiness_score', 0)
                desc = meal.get('description', 'N/A')
                items_html += f"<li style='margin-bottom:12px;'>\n"
                items_html += f"<div style='font-weight:700; font-size:16px; color:#e0f2f1;'>{name} - <span style='font-weight:900;'>{score}/100</span></div>\n"
                items_html += f"<div style='color:#97a7a3; font-size:13px; margin-top:6px;'>{desc}</div>\n"
                items_html += "</li>\n"

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(16,161,157,0.03) 0%, rgba(81,207,102,0.015) 100%); border:1px solid rgba(16,161,157,0.08); border-radius:12px; padding:18px;">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
                    <div style="font-size:20px;">✅</div>
                    <div style="font-size:18px; font-weight:800; color:#e0f2f1;">Healthiest Meals</div>
                </div>
                <ol style="padding-left:18px; margin:0;">{items_html}</ol>
            </div>
            """, unsafe_allow_html=True)

        # Right: Meals to Improve (styled container)
        with best_worst_col2:
            to_improve = list(reversed(sorted_meals[-3:]))
            items_html = ""
            for idx, meal in enumerate(to_improve, 1):
                name = meal.get('meal_name', 'Unknown')
                score = meal.get('healthiness_score', 0)
                desc = meal.get('description', 'N/A')
                items_html += f"<li style='margin-bottom:12px;'>\n"
                items_html += f"<div style='font-weight:700; font-size:16px; color:#e0f2f1;'>{name} - <span style='font-weight:900;'>{score}/100</span></div>\n"
                items_html += f"<div style='color:#97a7a3; font-size:13px; margin-top:6px;'>{desc}</div>\n"
                items_html += "</li>\n"

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(255,193,7,0.03) 0%, rgba(255,87,34,0.015) 100%); border:1px solid rgba(255,193,7,0.08); border-radius:12px; padding:18px;">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
                    <div style="font-size:20px;">⚠️</div>
                    <div style="font-size:18px; font-weight:800; color:#e0f2f1;">Meals to Improve</div>
                </div>
                <ol style="padding-left:18px; margin:0;">{items_html}</ol>
            </div>
            """, unsafe_allow_html=True)


def show_meal_recommendations(user_profile, meals, today_nutrition, targets):
    """Display personalized meal recommendations section"""
    st.markdown("## 🎯 Today's Meal Recommendations")
    st.caption("💡 Click the button below to generate personalized meal recommendations (this uses API calls)")
    
    if st.button("🤖 Generate Meal Recommendations", use_container_width=True):
        with st.spinner("🤖 Generating personalized recommendations..."):
            recommendations = recommender.get_personalized_recommendations(
                user_profile,
                meals,
                today_nutrition,
                targets
            )
            
            if recommendations:
                for idx, rec in enumerate(recommendations[:3], 1):
                    with st.expander(f"{idx}. {rec.get('meal_name', 'Meal')} - {rec.get('meal_type', '')}"):
                        st.write(f"**Description:** {rec.get('description', '')}")
                        st.write(f"⏱️ **Prep Time:** {rec.get('preparation_time', 'N/A')}")
                        
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            show_nutrition_facts(rec.get('estimated_nutrition', {}))
                        
                        with col2:
                            st.info(f"**Why:** {rec.get('why_recommended', '')}")
                        
                        if rec.get('health_benefits'):
                            st.success(f"**Benefits:** {', '.join(rec.get('health_benefits', []))}")


def show_health_insights(meals, user_profile, st_session_state):
    """Display health insights and analysis section"""
    st.markdown("## 📊 Health Insights")
    st.caption("💡 Click the button below to analyze your eating patterns (this uses API calls)")
    
    if st.button("🤖 Analyze Health Insights", use_container_width=True):
        with st.spinner("🤖 Analyzing your eating patterns..."):
            nutrition_history = db_manager.get_weekly_nutrition_summary(st_session_state.user_id, date.today())
            
            insights = recommender.get_health_insights(
                meals,
                user_profile,
                nutrition_history
            )
            
            if insights:
                # Create copyable insights text
                insights_text = "🍎 HEALTH INSIGHTS REPORT\n"
                insights_text += "=" * 40 + "\n\n"
                
                # Strengths
                insights_text += "✅ YOUR STRENGTHS:\n"
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("✅ Your Strengths")
                    for strength in insights.get('strengths', []):
                        st.write(f"• {strength}")
                        insights_text += f"• {strength}\n"
                
                with col2:
                    st.subheader("⚠️ Areas to Improve")
                    for area in insights.get('areas_for_improvement', []):
                        st.write(f"• {area}")
                
                insights_text += "\n⚠️ AREAS TO IMPROVE:\n"
                for area in insights.get('areas_for_improvement', []):
                    insights_text += f"• {area}\n"
                
                # Recommendations
                st.subheader("💡 Recommendations")
                insights_text += "\n💡 RECOMMENDATIONS:\n"
                for rec in insights.get('specific_recommendations', []):
                    st.write(f"• {rec}")
                    insights_text += f"• {rec}\n"
                
                # Red flags
                if insights.get('red_flags'):
                    insights_text += "\n🚨 WATCH OUT:\n"
                    st.error(f"🚨 **Watch Out:** {', '.join(insights.get('red_flags', []))}")
                    insights_text += f"• {', '.join(insights.get('red_flags', []))}\n"
                
                # Motivational message
                st.success(f"🌟 {insights.get('motivational_message', '')}")
                insights_text += f"\n🌟 {insights.get('motivational_message', '')}\n"
                
                # Add copy/share buttons
                st.divider()
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📋 Copy to Clipboard", use_container_width=True):
                        st.info("📝 Select all text below and copy (Ctrl+C):")
                        st.text_area("Insights:", value=insights_text, height=250, disabled=True, key="copy_insights")
                
                with col2:
                    if st.button("🔗 Share as Text", use_container_width=True):
                        with st.expander("📧 Shareable Format", expanded=True):
                            st.text_area("Copy and share this:", value=insights_text, height=250, disabled=True, key="share_insights")


def insights_page():
    """Health insights and recommendations page"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #41B952 0%, #51CF66 50%, #80C342 100%);
        padding: 24px 32px;
        border-radius: 16px;
        margin: -1rem -1rem 24px -1rem;
        box-shadow: 
            0 8px 32px rgba(81, 207, 102, 0.3),
            inset 0 1px 1px rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.15);
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 100% 0%, rgba(255, 255, 255, 0.15) 0%, transparent 50%);
            pointer-events: none;
        "></div>
        <h1 style="
            color: white; 
            margin: 0; 
            font-size: 1.75em; 
            font-weight: 700;
            line-height: 1.2;
            position: relative;
            z-index: 1;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <span style="font-size: 1.3em;">💡</span>
            <span>Health Insights & Recommendations</span>
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Get user profile (handles loading and caching automatically)
    user_profile = get_or_load_user_profile()
    
    # Get recent meals
    meals = db_manager.get_recent_meals(st.session_state.user_id, limit=20)
    
    if not meals:
        st.info("Log some meals to get personalized insights!")
        return
    
    # Get nutrition targets
    targets = calculate_personal_targets(user_profile)
    
    # Today's summary
    today_nutrition = db_manager.get_daily_nutrition_summary(st.session_state.user_id, date.today())
    
    # ===== BEST & WORST MEALS =====
    st.divider()
    show_meal_quality(meals)
    
    # ===== Personalized Recommendations =====
    st.divider()
    show_meal_recommendations(user_profile, meals, today_nutrition, targets)
    
    # ===== Health Insights =====
    st.divider()
    show_health_insights(meals, user_profile, st.session_state)
    
    # ===== NUTRITION TARGETS SUMMARY =====
    st.divider()
    st.markdown("## 🎯 Your Nutrition Targets")
    
    if user_profile:
        # Set end_date for nutrition summary
        end_date = date.today()
        
        # ===== PERSONALIZATION CONTEXT =====
        # Only render the context boxes when meaningful profile values exist.
        age_group = user_profile.get('age_group', 'N/A')
        gender = user_profile.get('gender', 'N/A')
        health_goal_val = user_profile.get('health_goal', 'N/A')
        health_conditions_list = user_profile.get('health_conditions', []) or []

        # Show personalization if profile has been customized from defaults
        # or if any meaningful data exists
        has_personalization = (
            user_profile and
            (
                (age_group and age_group != 'N/A') or
                (gender and gender != 'N/A') or
                (health_goal_val and health_goal_val != 'N/A') or
                (isinstance(health_conditions_list, list) and len(health_conditions_list) > 0)
            )
        )

        if has_personalization and age_group != 'N/A':
            st.markdown("**Your targets are personalized based on:**")
            context_cols = st.columns(4, gap="small")

            with context_cols[0]:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #3B82F620 0%, #60A5FA40 100%);
                    border: 1px solid #3B82F6;
                    border-radius: 10px;
                    padding: 12px 16px;
                    text-align: center;
                ">
                    <div style="font-size: 12px; color: #a0a0a0; text-transform: uppercase; margin-bottom: 4px; font-weight: 700;">Age Group</div>
                    <div style="font-size: 16px; font-weight: 900; color: #60A5FA;">{age_group}</div>
                </div>
                """, unsafe_allow_html=True)

            with context_cols[1]:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #EC489920 0%, #F472B640 100%);
                    border: 1px solid #EC4899;
                    border-radius: 10px;
                    padding: 12px 16px;
                    text-align: center;
                ">
                    <div style="font-size: 12px; color: #a0a0a0; text-transform: uppercase; margin-bottom: 4px; font-weight: 700;">Gender</div>
                    <div style="font-size: 16px; font-weight: 900; color: #F472B6;">{gender}</div>
                </div>
                """, unsafe_allow_html=True)

            with context_cols[2]:
                health_goal = str(health_goal_val).replace('_', ' ').title()
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #10B98120 0%, #34D39940 100%);
                    border: 1px solid #10B981;
                    border-radius: 10px;
                    padding: 12px 16px;
                    text-align: center;
                ">
                    <div style="font-size: 12px; color: #a0a0a0; text-transform: uppercase; margin-bottom: 4px; font-weight: 700;">Health Goal</div>
                    <div style="font-size: 16px; font-weight: 900; color: #34D399;">{health_goal}</div>
                </div>
                """, unsafe_allow_html=True)

            with context_cols[3]:
                health_conditions = ', '.join(health_conditions_list) or 'None'
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #8B5CF620 0%, #A78BFA40 100%);
                    border: 1px solid #8B5CF6;
                    border-radius: 10px;
                    padding: 12px 16px;
                    text-align: center;
                ">
                    <div style="font-size: 12px; color: #a0a0a0; text-transform: uppercase; margin-bottom: 4px; font-weight: 700;">Health Conditions</div>
                    <div style="font-size: 14px; font-weight: 700; color: #C4B5FD;">{health_conditions}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("")  # Spacing
        else:
            # If no personalization data available, just show the targets with defaults
            # Don't prompt to complete profile since we have defaults now
            pass
        
        # ===== NUTRITION TARGETS WITH PROGRESS =====
        st.markdown("**Daily Nutrition Targets:**")
        
        # Get today's nutrition for comparison (using end_date which is closest to today)
        today_nutrition = db_manager.get_daily_nutrition_summary(st.session_state.user_id, end_date)
        
        # Macronutrients - 2x2 grid
        macro_cols = st.columns(2, gap="medium")
        
        # Calories
        with macro_cols[0]:
            cal_target = targets['calories']
            cal_current = today_nutrition.get('calories', 0)
            cal_percent = min(100, (cal_current / cal_target * 100)) if cal_target > 0 else 0
            cal_emoji = "✅" if 0.9 <= cal_percent <= 1.1 else ("⚠️" if cal_percent < 0.9 else "⚡")
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #FF671520 0%, #FF671540 100%);
                border: 1px solid #FF6715;
                border-radius: 12px;
                padding: 18px;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div style="font-size: 20px; font-weight: 900; color: #FF6715;">🔥 Calories</div>
                    <div style="font-size: 18px;">{cal_emoji}</div>
                </div>
                <div style="margin-bottom: 10px;">
                    <div style="font-size: 24px; font-weight: 900; color: #FFB84D;">{cal_current:.0f}</div>
                    <div style="font-size: 12px; color: #a0a0a0;">of {cal_target} kcal/day</div>
                </div>
                <div style="background: #ffffff20; border-radius: 8px; height: 8px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #FF6715 0%, #FFB84D 100%); height: 100%; width: {cal_percent}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Protein
        with macro_cols[1]:
            protein_target = targets['protein']
            protein_current = today_nutrition.get('protein', 0)
            protein_percent = min(100, (protein_current / protein_target * 100)) if protein_target > 0 else 0
            protein_emoji = "✅" if 0.9 <= protein_percent <= 1.1 else ("⚠️" if protein_percent < 0.9 else "⚡")
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #EC4D6320 0%, #F43F5E40 100%);
                border: 1px solid #EC4D63;
                border-radius: 12px;
                padding: 18px;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div style="font-size: 20px; font-weight: 900; color: #EC4D63;">💪 Protein</div>
                    <div style="font-size: 18px;">{protein_emoji}</div>
                </div>
                <div style="margin-bottom: 10px;">
                    <div style="font-size: 24px; font-weight: 900; color: #FF8BA8;">{protein_current:.0f}g</div>
                    <div style="font-size: 12px; color: #a0a0a0;">of {protein_target}g/day</div>
                </div>
                <div style="background: #ffffff20; border-radius: 8px; height: 8px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #EC4D63 0%, #FF8BA8 100%); height: 100%; width: {protein_percent}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Carbs
        with macro_cols[0]:
            carbs_target = targets['carbs']
            carbs_current = today_nutrition.get('carbs', 0)
            carbs_percent = min(100, (carbs_current / carbs_target * 100)) if carbs_target > 0 else 0
            carbs_emoji = "✅" if 0.9 <= carbs_percent <= 1.1 else ("⚠️" if carbs_percent < 0.9 else "⚡")
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #F59E0B20 0%, #FBBF2440 100%);
                border: 1px solid #F59E0B;
                border-radius: 12px;
                padding: 18px;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div style="font-size: 20px; font-weight: 900; color: #F59E0B;">🌾 Carbs</div>
                    <div style="font-size: 18px;">{carbs_emoji}</div>
                </div>
                <div style="margin-bottom: 10px;">
                    <div style="font-size: 24px; font-weight: 900; color: #FCD34D;">{carbs_current:.0f}g</div>
                    <div style="font-size: 12px; color: #a0a0a0;">of {carbs_target}g/day</div>
                </div>
                <div style="background: #ffffff20; border-radius: 8px; height: 8px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #F59E0B 0%, #FCD34D 100%); height: 100%; width: {carbs_percent}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Fat
        with macro_cols[1]:
            fat_target = targets['fat']
            fat_current = today_nutrition.get('fat', 0)
            fat_percent = min(100, (fat_current / fat_target * 100)) if fat_target > 0 else 0
            fat_emoji = "✅" if 0.9 <= fat_percent <= 1.1 else ("⚠️" if fat_percent < 0.9 else "⚡")
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #06B6D420 0%, #14B8A640 100%);
                border: 1px solid #06B6D4;
                border-radius: 12px;
                padding: 18px;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div style="font-size: 20px; font-weight: 900; color: #06B6D4;">🌿 Fat</div>
                    <div style="font-size: 18px;">{fat_emoji}</div>
                </div>
                <div style="margin-bottom: 10px;">
                    <div style="font-size: 24px; font-weight: 900; color: #22D3EE;">{fat_current:.0f}g</div>
                    <div style="font-size: 12px; color: #a0a0a0;">of {fat_target}g/day</div>
                </div>
                <div style="background: #ffffff20; border-radius: 8px; height: 8px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #06B6D4 0%, #22D3EE 100%); height: 100%; width: {fat_percent}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("")  # Spacing
        
        # ===== MICRONUTRIENTS =====
        st.markdown("**Micronutrients:**")
        micro_cols = st.columns(3, gap="small")
        
        with micro_cols[0]:
            sodium_target = targets['sodium']
            sodium_current = today_nutrition.get('sodium', 0)
            st.metric("Sodium", f"{sodium_current:.0f}mg", f"Target: {sodium_target}mg")
        
        with micro_cols[1]:
            fiber_target = targets.get('fiber', 25)
            fiber_current = today_nutrition.get('fiber', 0)
            st.metric("Fiber", f"{fiber_current:.0f}g", f"Target: {fiber_target}g")
        
        with micro_cols[2]:
            sugar_target = 50  # Recommended daily max
            sugar_current = today_nutrition.get('sugar', 0)
            st.metric("Sugar", f"{sugar_current:.0f}g", f"Limit: {sugar_target}g")
    


def meal_history_page():
    """View and manage all logged meals"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #2563EB 0%, #3B82F6 50%, #60A5FA 100%);
        padding: 24px 32px;
        border-radius: 16px;
        margin: -1rem -1rem 24px -1rem;
        box-shadow: 
            0 8px 32px rgba(59, 130, 246, 0.3),
            inset 0 1px 1px rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.15);
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 100% 0%, rgba(255, 255, 255, 0.15) 0%, transparent 50%);
            pointer-events: none;
        "></div>
        <h1 style="
            color: white; 
            margin: 0; 
            font-size: 1.75em; 
            font-weight: 700;
            line-height: 1.2;
            position: relative;
            z-index: 1;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <span style="font-size: 1.3em;">📋</span>
            <span>Meal History</span>
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    user_id = st.session_state.user_id
    
    # Date range filters with proper alignment
    st.markdown("### 📅 Filter by Date Range")
    
    col1, col2, col3 = st.columns([1.5, 1.5, 0.8], gap="medium")
    
    with col1:
        start_date = st.date_input(
            "Start Date", 
            value=date.today() - timedelta(days=30),
            key="start_date_input"
        )
    
    with col2:
        end_date = st.date_input(
            "End Date", 
            value=date.today(),
            key="end_date_input"
        )
    
    with col3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🔍 Search", key="search_meals_btn", use_container_width=True):
            st.session_state.search_triggered = True
    
    # Get meals in range
    if st.session_state.get("search_triggered", False) or date.today() == end_date:
        meals = db_manager.get_meals_in_range(user_id, start_date, end_date)
        
        if not meals:
            st.info(f"No meals found between {start_date} and {end_date}")
            return
        
        # Sort by date descending
        meals = sorted(meals, key=lambda x: x.get("logged_at", ""), reverse=True)
        
        # Pagination
        page_size = 10
        total_pages, paginated_meals = paginate_items(meals, page_size=page_size)
        
        st.markdown(f"### Found {len(meals)} meals")
        st.divider()
        
        # Display meals with edit/delete options
        for meal in paginated_meals:
            col1, col2, col3, col4 = st.columns([2, 0.4, 0.4, 0.4])
            
            with col1:
                st.write(f"🍴 **{meal.get('meal_name', 'Unknown')}** - {meal.get('meal_type', 'meal')}")
                # Format timestamp nicely
                logged_at = meal.get('logged_at', 'N/A')
                if logged_at and logged_at != 'N/A':
                    try:
                        meal_dt = datetime.fromisoformat(logged_at)
                        formatted_time = meal_dt.strftime("%a, %b %d • %I:%M %p")
                        st.caption(f"📅 {formatted_time}")
                    except:
                        st.caption(f"📅 {logged_at}")
                else:
                    st.caption(f"📅 {logged_at}")
            
            with col2:
                if st.button("Edit", key=f"edit_hist_{meal['id']}", use_container_width=True):
                    st.session_state[f"edit_meal_id_{meal['id']}"] = True
            
            with col3:
                if st.button("Duplicate", key=f"dup_hist_{meal['id']}", use_container_width=True):
                    st.session_state[f"dup_meal_id_{meal['id']}"] = True
            
            with col4:
                if st.button("Delete", key=f"delete_hist_{meal['id']}", use_container_width=True):
                    st.session_state[f"confirm_delete_{meal['id']}"] = True
            
            # Delete confirmation dialog
            if st.session_state.get(f"confirm_delete_{meal['id']}", False):
                st.divider()
                st.warning(f"⚠️ Are you sure you want to delete **{meal.get('meal_name', 'this meal')}**?")
                st.caption("This action cannot be undone.")
                
                del_col1, del_col2 = st.columns(2)
                
                with del_col1:
                    if st.button("✅ Yes, Delete", key=f"confirm_delete_yes_{meal['id']}", use_container_width=True):
                        if db_manager.delete_meal(meal['id']):
                            st.toast("Meal deleted!", icon="✅")
                            st.session_state[f"confirm_delete_{meal['id']}"] = False
                            st.rerun()
                        else:
                            st.toast("Failed to delete meal", icon="❌")
                
                with del_col2:
                    if st.button("❌ Cancel", key=f"confirm_delete_no_{meal['id']}", use_container_width=True):
                        st.session_state[f"confirm_delete_{meal['id']}"] = False
            
            # Duplicate meal section
            if st.session_state.get(f"dup_meal_id_{meal['id']}", False):
                st.divider()
                st.subheader(f"Duplicate: {meal.get('meal_name', 'Meal')}")
                
                dup_date = st.date_input(
                    "Log this meal on:",
                    value=date.today(),
                    max_value=date.today(),
                    key=f"dup_date_{meal['id']}"
                )
                
                # Extract time from original meal
                original_logged_at = meal.get('logged_at', '')
                original_time = time(12, 0, 0)
                if original_logged_at:
                    try:
                        original_dt = datetime.fromisoformat(original_logged_at)
                        original_time = original_dt.time()
                    except:
                        pass
                
                dup_time = st.time_input(
                    "Log this meal at:",
                    value=original_time,
                    help="What time did you eat this meal?",
                    key=f"dup_time_{meal['id']}"
                )
                
                dup_col1, dup_col2 = st.columns(2)
                
                with dup_col1:
                    if st.button("✅ Duplicate Meal", key=f"confirm_dup_{meal['id']}", use_container_width=True):
                        meal_data = {
                            "user_id": st.session_state.user_id,
                            "meal_name": meal.get('meal_name', 'Unknown'),
                            "description": meal.get('description', ''),
                            "meal_type": meal.get('meal_type'),
                            "nutrition": meal.get('nutrition', {}),
                            "healthiness_score": meal.get('healthiness_score', 0),
                            "health_notes": meal.get('health_notes', ''),
                            "logged_at": datetime.combine(dup_date, dup_time).isoformat(),
                        }
                        
                        if db_manager.log_meal(meal_data):
                            st.toast(f"{meal.get('meal_name')} duplicated to {dup_date}!", icon="✅")
                            st.session_state[f"dup_meal_id_{meal['id']}"] = False
                        else:
                            st.toast("Failed to duplicate meal", icon="❌")
                
                with dup_col2:
                    if st.button("❌ Cancel", key=f"cancel_dup_{meal['id']}", use_container_width=True):
                        st.session_state[f"dup_meal_id_{meal['id']}"] = False
                
                st.divider()
            
            # Show details
            with st.expander("View Details", expanded=False):
                st.write(f"**Description:** {meal.get('description', 'N/A')}")
                nutrition = meal.get("nutrition", {})
                show_nutrition_facts(nutrition)
            
            # Edit form
            if st.session_state.get(f"edit_meal_id_{meal['id']}", False):
                st.divider()
                st.subheader(f"Edit: {meal.get('meal_name', 'Meal')}")
                
                with st.form(f"edit_hist_form_{meal['id']}"):
                    meal_name = st.text_input("Meal Name", value=meal.get('meal_name', ''))
                    meal_type = st.selectbox(
                        "Meal Type",
                        options=list(MEAL_TYPES.keys()),
                        index=list(MEAL_TYPES.keys()).index(meal.get('meal_type', 'breakfast')) if meal.get('meal_type') in MEAL_TYPES else 0,
                        key=f"type_hist_{meal['id']}"
                    )
                    description = st.text_area("Description", value=meal.get('description', ''), key=f"desc_hist_{meal['id']}")
                    
                    # Edit nutrition
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        calories = st.number_input("Calories", value=float(meal.get('nutrition', {}).get('calories', 0)), min_value=0.0, key=f"cal_hist_{meal['id']}")
                        protein = st.number_input("Protein (g)", value=float(meal.get('nutrition', {}).get('protein', 0)), min_value=0.0, key=f"prot_hist_{meal['id']}")
                        carbs = st.number_input("Carbs (g)", value=float(meal.get('nutrition', {}).get('carbs', 0)), min_value=0.0, key=f"carb_hist_{meal['id']}")
                    
                    with col2:
                        fat = st.number_input("Fat (g)", value=float(meal.get('nutrition', {}).get('fat', 0)), min_value=0.0, key=f"fat_hist_{meal['id']}")
                        sodium = st.number_input("Sodium (mg)", value=float(meal.get('nutrition', {}).get('sodium', 0)), min_value=0.0, key=f"sod_hist_{meal['id']}")
                        sugar = st.number_input("Sugar (g)", value=float(meal.get('nutrition', {}).get('sugar', 0)), min_value=0.0, key=f"sug_hist_{meal['id']}")
                    
                    with col3:
                        fiber = st.number_input("Fiber (g)", value=float(meal.get('nutrition', {}).get('fiber', 0)), min_value=0.0, key=f"fib_hist_{meal['id']}")
                    
                    # Button columns
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.form_submit_button("💾 Save Changes", key=f"save_hist_{meal['id']}", use_container_width=True):
                            updated_meal = {
                                "meal_name": meal_name,
                                "meal_type": meal_type,
                                "description": description,
                                "nutrition": {
                                    "calories": calories,
                                    "protein": protein,
                                    "carbs": carbs,
                                    "fat": fat,
                                    "sodium": sodium,
                                    "sugar": sugar,
                                    "fiber": fiber,
                                }
                            }
                            
                            # Validate meal data before updating
                            is_valid, error_msg = validate_meal_data(
                                meal_name,
                                updated_meal["nutrition"],
                                None  # Edit doesn't change the date
                            )
                            
                            if not is_valid:
                                st.error(f"⚠️ Validation Error: {error_msg}")
                            elif db_manager.update_meal(meal['id'], updated_meal):
                                st.toast("Meal updated!", icon="✅")
                                st.session_state[f"edit_meal_id_{meal['id']}"] = False
                            else:
                                st.toast("Failed to update meal", icon="❌")
                    
                    with btn_col2:
                        if st.form_submit_button("❌ Cancel", key=f"cancel_hist_{meal['id']}", use_container_width=True):
                            st.session_state[f"edit_meal_id_{meal['id']}"] = False
            
            st.divider()
        
        # Compact pagination at bottom
        if total_pages > 1:
            st.divider()
            pag_col1, pag_col2 = st.columns([1, 1], gap="small")
            
            current_page = st.session_state.pagination_page + 1
            with pag_col1:
                if st.button(f"⬅️ Previous ({current_page}/{total_pages})", key="prev_bottom", disabled=(st.session_state.pagination_page == 0), use_container_width=True):
                    st.session_state.pagination_page -= 1
            
            with pag_col2:
                if st.button(f"Next ({current_page}/{total_pages}) ➡️", key="next_bottom", disabled=(st.session_state.pagination_page >= total_pages - 1), use_container_width=True):
                    st.session_state.pagination_page += 1


def profile_page():
    """User profile and health settings page"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #E85C0D 0%, #FF6B16 50%, #FF8A4D 100%);
        padding: 24px 32px;
        border-radius: 16px;
        margin: -1rem -1rem 24px -1rem;
        box-shadow: 
            0 8px 32px rgba(255, 107, 22, 0.3),
            inset 0 1px 1px rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.15);
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 100% 0%, rgba(255, 255, 255, 0.15) 0%, transparent 50%);
            pointer-events: none;
        "></div>
        <h1 style="
            color: white; 
            margin: 0; 
            font-size: 1.75em; 
            font-weight: 700;
            line-height: 1.2;
            position: relative;
            z-index: 1;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <span style="font-size: 1.3em;">👤</span>
            <span>My Profile</span>
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    user_email = st.session_state.user_email
    
    # Create tabs for Profile and Security
    tab1, tab2 = st.tabs(["Profile", "Security"])
    
    with tab1:
        # Fetch profile from database (fresh for this page, not using cache)
        # because users expect to see current profile data when they visit settings
        try:
            user_profile = db_manager.get_health_profile(st.session_state.user_id)
            user_profile = normalize_profile(user_profile) if user_profile else None
        except Exception as e:
            st.error(f"Failed to load profile: {str(e)}")
            user_profile = None
        
        st.markdown(f"**Email:** {user_email}")
        
        # Get or create profile
        if not user_profile:
            st.markdown("## Complete Your Profile")
            
            with st.form("health_profile_form"):
                # Row 1: Full Name and Age Group
                col1, col2 = st.columns(2)
                with col1:
                    full_name = st.text_input("Full Name")
                
                with col2:
                    age_group = st.selectbox(
                        "Age Group",
                        options=list(AGE_GROUP_TARGETS.keys()),
                        help="This helps us set appropriate nutrition targets"
                    )
                
                # Row 2: Gender and Timezone
                col3, col4 = st.columns(2)
                with col3:
                    gender = st.selectbox(
                        "Gender",
                        options=["Male", "Female"],
                        help="This helps us provide personalized nutrition recommendations"
                    )
                
                with col4:
                    # Timezone mapping with descriptive labels showing UTC offset and example cities
                    timezone_dict = {
                        "UTC ±0 (London, Dublin)": "UTC",
                        "UTC-10 (Hawaii)": "US/Hawaii",
                        "UTC-9 (Alaska)": "US/Alaska",
                        "UTC-8 (Pacific: Los Angeles, Vancouver)": "US/Pacific",
                        "UTC-7 (Mountain: Denver, Phoenix)": "US/Mountain",
                        "UTC-6 (Central: Chicago, Mexico City)": "US/Central",
                        "UTC-5 (Eastern: New York, Toronto)": "US/Eastern",
                        "UTC+0 (London, UK)": "Europe/London",
                        "UTC+1 (Paris, Berlin, Rome)": "Europe/Paris",
                        "UTC+3 (Moscow, Istanbul)": "Europe/Moscow",
                        "UTC+4 (Dubai, Abu Dhabi)": "Asia/Dubai",
                        "UTC+5:30 (India: Delhi, Mumbai, Bangalore)": "Asia/Kolkata",
                        "UTC+7 (Bangkok, Hanoi, Ho Chi Minh)": "Asia/Bangkok",
                        "UTC+8 (Shanghai, Singapore, Hong Kong)": "Asia/Shanghai",
                        "UTC+9 (Tokyo, Seoul)": "Asia/Tokyo",
                        "UTC+10 (Sydney, Melbourne)": "Australia/Sydney",
                        "UTC+12 (Auckland, Fiji)": "Pacific/Auckland"
                    }
                    timezone_options = list(timezone_dict.keys())
                    timezone = st.selectbox(
                        "Timezone",
                        options=timezone_options,
                        index=0,
                        help="Select your timezone. The UTC offset and major cities help you find yours quickly."
                    )
                    timezone = timezone_dict[timezone]
                
                # Row 2.5: Height and Weight (Optional)
                col3b, col4b = st.columns(2)
                with col3b:
                    height_cm = st.number_input(
                        "Height (cm) - Optional",
                        min_value=100,
                        max_value=250,
                        value=170,
                        step=1,
                        help="Your height in centimeters (optional)"
                    )
                    height_cm = height_cm if height_cm else None
                
                with col4b:
                    weight_kg = st.number_input(
                        "Weight (kg) - Optional",
                        min_value=30.0,
                        max_value=200.0,
                        value=70.0,
                        step=0.5,
                        help="Your weight in kilograms (optional)"
                    )
                    weight_kg = weight_kg if weight_kg else None
                
                # Row 3: Health Conditions and Dietary Preferences
                col5, col6 = st.columns(2)
                with col5:
                    health_conditions = st.multiselect(
                        "Health Conditions",
                        options=list(HEALTH_CONDITIONS.keys()),
                        format_func=lambda x: HEALTH_CONDITIONS.get(x, x),
                        help="Select any health conditions that apply"
                    )
                
                with col6:
                    dietary_preferences = st.multiselect(
                        "Dietary Preferences",
                        options=list(DIETARY_PREFERENCES.keys()),
                        format_func=lambda x: DIETARY_PREFERENCES.get(x, x),
                        help="Select any dietary restrictions or preferences"
                    )
                
                # Row 4: Health Goal and Water Goal
                col7, col8 = st.columns(2)
                with col7:
                    goal = st.selectbox(
                        "Health Goal",
                        options=list(HEALTH_GOAL_TARGETS.keys()),
                        format_func=lambda x: HEALTH_GOAL_TARGETS.get(x, x),
                        help="What's your primary health goal?"
                    )
                
                with col8:
                    water_goal = st.number_input(
                        "Daily Water Goal (glasses)",
                        min_value=1,
                        max_value=20,
                        value=8,
                        help="Recommended: 8 glasses per day (2 liters)"
                    )
                
                if st.form_submit_button("Save Profile", use_container_width=True):
                    profile_data = {
                        "user_id": st.session_state.user_id,
                        "full_name": full_name,
                        "age_group": age_group,
                        "gender": gender,
                        "timezone": timezone,
                        "height_cm": height_cm,
                        "weight_kg": weight_kg,
                        "health_conditions": health_conditions,
                        "dietary_preferences": dietary_preferences,
                        "health_goal": goal,
                        "water_goal_glasses": int(water_goal),
                        "badges_earned": [],
                        "total_xp": 0,  # Initialize XP to 0 for new users
                    }
                    
                    if db_manager.create_health_profile(st.session_state.user_id, profile_data):
                        # Refresh profile from DB to ensure stored representation matches
                        fetched = db_manager.get_health_profile(st.session_state.user_id) or profile_data
                        st.session_state.user_profile = normalize_profile(fetched)
                        show_notification("Profile created!", "success", use_toast=False)
                        st.rerun()
                    else:
                        show_notification("Failed to create profile", "error", use_toast=False)
        
        else:
            st.markdown("## Update Your Profile")
            
            with st.form("update_profile_form"):
                # Row 1: Full Name and Age Group
                col1, col2 = st.columns(2)
                with col1:
                    full_name = st.text_input("Full Name", value=user_profile.get("full_name", ""))
                
                with col2:
                    # Handle age group with migration for old format (26-35 (Adult) -> 26-35)
                    current_age_group = user_profile.get("age_group", "26-35")
                    # If user has old format with label, try to find matching new format
                    age_group_keys = list(AGE_GROUP_TARGETS.keys())
                    age_group_index = 0
                    try:
                        if current_age_group not in age_group_keys:
                            # Try to find a matching age group key
                            matching_key = None
                            for key in age_group_keys:
                                if key.split(" (")[0] == current_age_group or key in current_age_group:  # Match by age range part
                                    matching_key = key
                                    break
                            current_age_group = matching_key or "26-35"  # Default fallback
                        
                        age_group_index = age_group_keys.index(current_age_group)
                    except (ValueError, IndexError):
                        age_group_index = age_group_keys.index("26-35") if "26-35" in age_group_keys else 0
                    
                    age_group = st.selectbox(
                        "Age Group",
                        options=age_group_keys,
                        index=age_group_index
                    )
                
                # Row 2: Gender and Timezone
                col3, col4 = st.columns(2)
                with col3:
                    gender_options = ["Male", "Female"]
                    gender_value = user_profile.get("gender", "Female")
                    gender_index = gender_options.index(gender_value) if gender_value in gender_options else 1
                    gender = st.selectbox(
                        "Gender",
                        options=gender_options,
                        index=gender_index,
                        help="This helps us provide personalized nutrition recommendations"
                    )
                
                with col4:
                    # Timezone mapping with descriptive labels showing UTC offset and example cities
                    timezone_dict = {
                        "UTC ±0 (London, Dublin)": "UTC",
                        "UTC-10 (Hawaii)": "US/Hawaii",
                        "UTC-9 (Alaska)": "US/Alaska",
                        "UTC-8 (Pacific: Los Angeles, Vancouver)": "US/Pacific",
                        "UTC-7 (Mountain: Denver, Phoenix)": "US/Mountain",
                        "UTC-6 (Central: Chicago, Mexico City)": "US/Central",
                        "UTC-5 (Eastern: New York, Toronto)": "US/Eastern",
                        "UTC+0 (London, UK)": "Europe/London",
                        "UTC+1 (Paris, Berlin, Rome)": "Europe/Paris",
                        "UTC+3 (Moscow, Istanbul)": "Europe/Moscow",
                        "UTC+4 (Dubai, Abu Dhabi)": "Asia/Dubai",
                        "UTC+5:30 (India: Delhi, Mumbai, Bangalore)": "Asia/Kolkata",
                        "UTC+7 (Bangkok, Hanoi, Ho Chi Minh)": "Asia/Bangkok",
                        "UTC+8 (Shanghai, Singapore, Hong Kong)": "Asia/Shanghai",
                        "UTC+9 (Tokyo, Seoul)": "Asia/Tokyo",
                        "UTC+10 (Sydney, Melbourne)": "Australia/Sydney",
                        "UTC+12 (Auckland, Fiji)": "Pacific/Auckland"
                    }
                    timezone_options = list(timezone_dict.keys())
                    timezone_value = user_profile.get("timezone", "UTC")
                    # Find the matching display key for the saved timezone value
                    timezone_index = 0
                    try:
                        for key, value in timezone_dict.items():
                            if value == timezone_value:
                                timezone_index = timezone_options.index(key)
                                break
                    except (ValueError, IndexError):
                        timezone_index = 0  # Default to first option
                    
                    timezone = st.selectbox(
                        "Timezone",
                        options=timezone_options,
                        index=timezone_index,
                        help="Select your timezone. The UTC offset and major cities help you find yours quickly."
                    )
                    timezone = timezone_dict.get(timezone, "UTC")
                
                # Row 2.5: Height and Weight (Optional)
                col3b, col4b = st.columns(2)
                with col3b:
                    # Safe height handling
                    height_value = user_profile.get("height_cm")
                    try:
                        height_default = int(height_value) if height_value is not None else 170
                    except (ValueError, TypeError):
                        height_default = 170
                    
                    height_cm = st.number_input(
                        "Height (cm) - Optional",
                        min_value=100,
                        max_value=250,
                        value=height_default,
                        step=1,
                        help="Your height in centimeters (optional)"
                    )
                    height_cm = height_cm if height_cm != 170 or height_value is not None else None
                
                with col4b:
                    # Safe weight handling
                    weight_value = user_profile.get("weight_kg")
                    try:
                        weight_default = float(weight_value) if weight_value is not None else 70.0
                    except (ValueError, TypeError):
                        weight_default = 70.0
                    
                    weight_kg = st.number_input(
                        "Weight (kg) - Optional",
                        min_value=30.0,
                        max_value=200.0,
                        value=weight_default,
                        step=0.5,
                        help="Your weight in kilograms (optional)"
                    )
                    weight_kg = weight_kg if weight_kg != 70.0 or weight_value is not None else None
                
                # Row 3: Health Conditions and Dietary Preferences
                col5, col6 = st.columns(2)
                with col5:
                    health_conditions = st.multiselect(
                        "Health Conditions",
                        options=list(HEALTH_CONDITIONS.keys()),
                        default=user_profile.get("health_conditions", []),
                        format_func=lambda x: HEALTH_CONDITIONS.get(x, x)
                    )
                
                with col6:
                    dietary_preferences = st.multiselect(
                        "Dietary Preferences",
                        options=list(DIETARY_PREFERENCES.keys()),
                        default=user_profile.get("dietary_preferences", []),
                        format_func=lambda x: DIETARY_PREFERENCES.get(x, x)
                    )
                
                # Row 4: Health Goal and Water Goal
                col7, col8 = st.columns(2)
                with col7:
                    # Handle health goal with safe index lookup
                    current_health_goal = user_profile.get("health_goal", "general_health")
                    goal_keys = list(HEALTH_GOAL_TARGETS.keys())
                    goal_index = 0
                    try:
                        goal_index = goal_keys.index(current_health_goal) if current_health_goal in goal_keys else 0
                    except (ValueError, IndexError):
                        goal_index = 0
                    
                    # Create display names for health goals
                    goal_display_names = {
                        "general_health": "General Health",
                        "weight_loss": "Weight Loss",
                        "weight_gain": "Weight Gain",
                        "muscle_gain": "Muscle Building",
                        "performance": "Athletic Performance",
                    }
                    
                    goal = st.selectbox(
                        "Health Goal",
                        options=goal_keys,
                        index=goal_index,
                        format_func=lambda x: goal_display_names.get(x, x),
                        help="What's your primary health goal?"
                    )
                
                with col8:
                    # Safe water goal handling
                    water_goal_value = user_profile.get("water_goal_glasses", 8)
                    try:
                        water_goal_default = int(water_goal_value) if water_goal_value is not None else 8
                    except (ValueError, TypeError):
                        water_goal_default = 8
                    
                    water_goal = st.number_input(
                        "Daily Water Goal (glasses)",
                        min_value=1,
                        max_value=20,
                        value=water_goal_default,
                        help="Recommended: 8 glasses per day (2 liters)"
                    )
                
                if st.form_submit_button("Update Profile", use_container_width=True):
                    update_data = {
                        "full_name": full_name,
                        "age_group": age_group,
                        "gender": gender,
                        "timezone": timezone,
                        "height_cm": height_cm,
                        "weight_kg": weight_kg,
                        "health_conditions": health_conditions,
                        "dietary_preferences": dietary_preferences,
                        "health_goal": goal,
                        "water_goal_glasses": int(water_goal),
                    }
                    
                    if db_manager.update_health_profile(st.session_state.user_id, update_data):
                        # Refresh profile from DB to ensure we have the latest stored representation
                        fetched = db_manager.get_health_profile(st.session_state.user_id) or update_data
                        st.session_state.user_profile = normalize_profile(fetched)
                        show_notification("Profile updated!", "success", use_toast=False)
                        st.rerun()
                    else:
                        show_notification("Failed to update profile", "error", use_toast=False)
    
    with tab2:
        st.markdown("## Change Password")
        
        with st.form("change_password_form"):
            current_password = st.text_input("Current Password", type="password", help="Enter your current password")
            new_password = st.text_input("New Password", type="password", help="Enter your new password (at least 6 characters)")
            confirm_password = st.text_input("Confirm New Password", type="password", help="Re-enter your new password")
            
            if st.form_submit_button("Change Password", use_container_width=True):
                # Validate inputs
                if not current_password or not new_password or not confirm_password:
                    st.error("❌ Please fill in all password fields")
                elif new_password != confirm_password:
                    st.error("❌ New passwords do not match")
                elif len(new_password) < 6:
                    st.error("❌ New password must be at least 6 characters long")
                else:
                    # Attempt to change password
                    success, message = auth_manager.change_password(current_password, new_password)
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")


# ==================== COACHING ASSISTANT PAGE ====================

def coaching_assistant_page():
    """AI-Powered Nutrition Coaching Assistant - Unified Chat Interface"""
    
    # Add CSS for clean page transitions and responsive chat styling
    st.markdown("""
    <style>
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .coaching-header {
            animation: fadeIn 0.3s ease-in;
        }
        
        .chat-box {
            background: rgba(10, 20, 30, 0.6);
            border: 1px solid #3B82F6;
            border-radius: 12px;
            padding: 16px;
            height: min(550px, 70vh);
            overflow-y: auto;
            margin-bottom: 12px;
        }
        
        @media (max-width: 1024px) {
            .chat-box {
                height: min(480px, 65vh);
                padding: 14px;
            }
        }
        
        @media (max-width: 768px) {
            .chat-box {
                height: min(400px, 60vh);
                padding: 12px;
            }
        }
        
        @media (max-width: 640px) {
            .chat-box {
                height: min(360px, 55vh);
                padding: 12px;
            }
            
            .message-user {
                margin-left: 20px !important;
            }
            
            .message-coach {
                margin-right: 20px !important;
            }
        }
        
        @media (max-width: 480px) {
            .chat-box {
                height: min(300px, 50vh);
                padding: 10px;
            }
            
            .message-user {
                margin-left: 12px !important;
                padding: 10px 12px !important;
            }
            
            .message-coach {
                margin-right: 12px !important;
                padding: 10px 12px !important;
            }
        }
        
        @media (max-height: 600px) {
            .chat-box {
                height: min(250px, 45vh) !important;
                padding: 8px !important;
            }
        }
        
        .chat-box::-webkit-scrollbar {
            width: 8px;
        }
        
        .chat-box::-webkit-scrollbar-track {
            background: rgba(60, 130, 180, 0.1);
            border-radius: 10px;
        }
        
        .chat-box::-webkit-scrollbar-thumb {
            background: rgba(60, 130, 180, 0.3);
            border-radius: 10px;
        }
        
        .chat-box::-webkit-scrollbar-thumb:hover {
            background: rgba(60, 130, 180, 0.5);
        }
        
        .message-user {
            background: linear-gradient(135deg, #10A19D15 0%, #52C4B825 100%);
            border: 1px solid #10A19D;
            border-left: 4px solid #10A19D;
            border-radius: 12px;
            padding: 12px 16px;
            margin-bottom: 12px;
            margin-left: 40px;
            word-wrap: break-word;
        }
        
        .message-coach {
            background: linear-gradient(135deg, #845EF715 0%, #BE80FF25 100%);
            border: 1px solid #845EF7;
            border-left: 4px solid #845EF7;
            border-radius: 12px;
            padding: 12px 16px;
            margin-bottom: 12px;
            margin-right: 40px;
            word-wrap: break-word;
        }
        
        .message-label {
            color: #a0a0a0;
            font-size: 11px;
            font-weight: 700;
            margin-bottom: 4px;
            text-transform: uppercase;
        }
        
        .message-content {
            color: #e0f2f1;
            font-size: 14px;
            line-height: 1.5;
            word-break: break-word;
        }
        
        .context-card {
            background: linear-gradient(135deg, #3B82F615 0%, #60A5FA25 100%);
            border: 1px solid #3B82F6;
            border-left: 4px solid #3B82F6;
            border-radius: 12px;
            padding: 12px 14px;
            font-size: 12px;
            margin-bottom: 12px;
        }
        
        .context-label {
            color: #a0a0a0;
            font-weight: 700;
            margin-bottom: 4px;
            font-size: 11px;
            text-transform: uppercase;
        }
        
        .context-value {
            color: #e0f2f1;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Create a placeholder for content that will be populated after loading
    page_container = st.container()
    
    # Initialize data with loading spinner
    with st.spinner("⏳ Loading your nutrition coach..."):
        # Get user profile (handles loading and caching automatically)
        user_profile = get_or_load_user_profile()
        
        coaching = CoachingAssistant()
        today = date.today()
        today_nutrition = db_manager.get_daily_nutrition_summary(st.session_state.user_id, today)
        
        # Get nutrition targets
        targets = calculate_personal_targets(user_profile)
        
        # Initialize conversation history in session state
        if "coaching_conversation" not in st.session_state:
            st.session_state.coaching_conversation = []
    
    # Render all content in page container after loading completes
    with page_container:
        # Compact header with less space
        st.markdown("""
        <div class="coaching-header" style="
            background: linear-gradient(135deg, #845EF7 0%, #BE80FF 100%);
            padding: 10px 20px;
            border-radius: 12px;
            margin-bottom: 12px;
        ">
            <h2 style="color: white; margin: 0; font-size: 1.3em;">🎯 Nutrition Coach</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Chat messages container with fixed height and scrolling
        # Create a fixed-height scrollable chat area using HTML/CSS
        messages_html = '<div class="chat-box">'
        
        if not st.session_state.coaching_conversation:
            messages_html += '<div style="text-align: center; color: #a0a0a0; padding: 20px;">💬 Start a conversation!</div>'
        else:
            for msg in st.session_state.coaching_conversation:
                role = msg["role"]
                content = msg["content"]
                # Escape HTML special characters in content
                import html
                escaped_content = html.escape(content)
                
                if role == "user":
                    messages_html += f'<div class="message-user"><div class="message-label">You</div><div class="message-content">{escaped_content}</div></div>'
                else:
                    messages_html += f'<div class="message-coach"><div class="message-label">🎯 Coach</div><div class="message-content">{escaped_content}</div></div>'
        
        messages_html += '</div>'
        st.markdown(messages_html, unsafe_allow_html=True)
        
        # Use a form for proper input handling
        with st.form(key="chat_form", clear_on_submit=True):
            form_col1, form_col2, form_col3 = st.columns([4, 1, 1], gap="small")
            
            with form_col1:
                user_input = st.text_input(
                    "Message",
                    placeholder="Ask your coach...",
                    label_visibility="collapsed"
                )
            
            with form_col2:
                send_button = st.form_submit_button("📤 Send", use_container_width=True)
            
            with form_col3:
                clear_button = st.form_submit_button("🔄 Clear", key="clear_coaching_btn", use_container_width=True)
                if clear_button:
                    st.session_state.coaching_conversation = []
        
        # Handle message sending
        if send_button and user_input.strip():
            # Add user message to conversation
            st.session_state.coaching_conversation.append({
                "role": "user",
                "content": user_input
            })
            
            # Get coach response
            with st.spinner("🤖 Coach is thinking..."):
                response = coaching.get_conversation_response(
                    st.session_state.coaching_conversation,
                    user_input,
                    user_profile,
                    today_nutrition,
                    targets
                )
            
            # Add assistant response to conversation
            st.session_state.coaching_conversation.append({
                "role": "assistant",
                "content": response
            })
            
            st.rerun()


# ==================== RESTAURANT MENU ANALYZER PAGE ====================

def restaurant_analyzer_page():
    """Analyze restaurant menus and find healthiest options"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #EE5A52 0%, #FF6B6B 50%, #FFA94D 100%);
        padding: 24px 32px;
        border-radius: 16px;
        margin: -1rem -1rem 24px -1rem;
        box-shadow: 
            0 8px 32px rgba(255, 107, 107, 0.3),
            inset 0 1px 1px rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.15);
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 100% 0%, rgba(255, 255, 255, 0.15) 0%, transparent 50%);
            pointer-events: none;
        "></div>
        <h1 style="
            color: white; 
            margin: 0; 
            font-size: 1.75em; 
            font-weight: 700;
            line-height: 1.2;
            position: relative;
            z-index: 1;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <span style="font-size: 1.3em;">🍽️</span>
            <span>Restaurant Menu Analyzer</span>
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    Eating out doesn't have to derail your nutrition goals! Enter a restaurant menu and get 
    personalized recommendations based on your health profile, goals, and today's nutrition intake.
    """)
    
    # Get user profile (handles loading and caching automatically)
    user_profile = get_or_load_user_profile()
    
    if not user_profile:
        st.warning("⚠️ Please complete your health profile in 'My Profile' for personalized recommendations")
        return
    
    # Initialize menu analyzer
    menu_analyzer = RestaurantMenuAnalyzer()
    
    # Create tabs for input method
    tab_text, tab_photo = st.tabs(["📝 Paste Menu Text", "📸 Upload Menu Photo"])
    
    with tab_text:
        st.markdown("### Enter Menu Text")
        st.caption("Copy and paste the full restaurant menu")
        
        menu_text = st.text_area(
            "Restaurant Menu",
            height=300,
            placeholder="Paste restaurant menu here...\n\nExample:\nAPPETIZERS\n- Bruschetta $8\n- Calamari $12\n\nMAIN COURSES\n- Grilled Salmon $18\n- Pasta Carbonara $16",
            label_visibility="collapsed",
            key="menu_text_input"
        )
        
        if st.button("🔍 Analyze Menu", type="primary", key="analyze_text_btn", use_container_width=True):
            if not menu_text.strip():
                st.warning("Please paste a menu to analyze")
            else:
                with st.spinner("🤖 Analyzing menu with AI..."):
                    # Get today's nutrition
                    today_nutrition = db_manager.get_daily_nutrition_summary(
                        st.session_state.user_id, date.today()
                    )
                    
                    # Get targets
                    targets = calculate_personal_targets(user_profile)
                    
                    # Analyze menu
                    analysis = menu_analyzer.analyze_menu(
                        menu_text,
                        user_profile,
                        today_nutrition,
                        targets
                    )
                    
                    if analysis:
                        st.session_state.menu_analysis = analysis
                        st.success("✅ Menu analyzed!")
                    else:
                        st.error("Could not analyze menu. Please try again.")
    
    with tab_photo:
        st.markdown("### Upload Menu Photo")
        st.caption("Take a photo of the menu (JPG, PNG) | Max 50 MB")
        
        uploaded_file = st.file_uploader(
            "Menu Photo",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
            key="menu_photo_upload",
            help="JPG or PNG format, max 50 MB"
        )
        
        if uploaded_file is not None:
            # Display uploaded image in a smaller preview format
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.image(uploaded_file, caption="Menu Photo Preview", use_column_width=True)
            
            with col2:
                st.markdown("")  # Spacing
                if st.button("📸 Extract Text from Photo", type="primary", use_container_width=True):
                    with st.spinner("🔍 Extracting text from menu..."):
                        try:
                            # Read image file
                            image_data = uploaded_file.getvalue()
                            image_base64 = base64.b64encode(image_data).decode('utf-8')
                            
                            # Use OpenAI Vision to extract menu text
                            from openai import AzureOpenAI
                            client = AzureOpenAI(
                                api_key=AZURE_OPENAI_API_KEY,
                                api_version="2023-05-15",
                                azure_endpoint=AZURE_OPENAI_ENDPOINT
                            )
                            
                            response = client.chat.completions.create(
                                model=AZURE_OPENAI_DEPLOYMENT,
                                messages=[
                                    {"role": "system", "content": "You are an OCR expert. Extract all text from the menu image. Preserve the structure and formatting as much as possible."},
                                    {
                                        "role": "user",
                                        "content": [
                                            {"type": "text", "text": "Extract all text from this menu image:"},
                                            {
                                                "type": "image_url",
                                                "image_url": {
                                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                                }
                                            }
                                        ]
                                    }
                                ],
                                max_tokens=2000
                            )
                            
                            extracted_text = response.choices[0].message.content
                            st.session_state.extracted_menu_text = extracted_text
                            st.success("✅ Text extracted! Auto-analyzing menu...")
                            
                            # Auto-analyze the extracted menu
                            with st.spinner("🤖 Analyzing menu with AI..."):
                                # Get today's nutrition
                                today_nutrition = db_manager.get_daily_nutrition_summary(
                                    st.session_state.user_id, date.today()
                                )
                                
                                # Get targets
                                targets = calculate_personal_targets(user_profile)
                                
                                # Analyze menu
                                analysis = menu_analyzer.analyze_menu(
                                    extracted_text,
                                    user_profile,
                                    today_nutrition,
                                    targets
                                )
                                
                                if analysis:
                                    st.session_state.menu_analysis = analysis
                                    st.success("✅ Menu analyzed and ready for recommendations!")
                                else:
                                    st.error("Could not analyze menu. Please try again.")
                            
                        except Exception as e:
                            st.error(f"Error extracting text: {str(e)}")
            
            # Show extracted text if available
            if "extracted_menu_text" in st.session_state:
                st.markdown("---")
                st.markdown("### 📋 Extracted Text")
                
                with st.expander("View extracted text", expanded=False):
                    st.text_area(
                        "Extracted Menu Text",
                        value=st.session_state.extracted_menu_text,
                        height=200,
                        disabled=True,
                        label_visibility="collapsed"
                    )
                
                st.info("ℹ️ Menu has been automatically analyzed and recommendations are ready below.")
    
    # Display analysis results (shared between both tabs)
    if "menu_analysis" in st.session_state:
        analysis = st.session_state.menu_analysis
        
        st.markdown("---")
        st.markdown("## 📊 Menu Analysis")
        
        # Restaurant assessment
        if "restaurant_analysis" in analysis:
            st.info(f"**Restaurant Assessment:** {analysis['restaurant_analysis']}")
        
        # Best options
        if "best_options" in analysis and analysis["best_options"]:
            st.markdown("### ⭐ Best Options for You")
            
            for i, option in enumerate(analysis["best_options"][:5], 1):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    badge = option.get("badge", "")
                    st.markdown(f"**{i}. {option.get('menu_item', 'N/A')}** {f'🏆 {badge}' if badge else ''}")
                    st.caption(option.get("reason", ""))
                    
                    # Nutrition in cards
                    nutrition = option.get("estimated_nutrition", {})
                    nut_col1, nut_col2, nut_col3, nut_col4 = st.columns(4, gap="small")
                    
                    with nut_col1:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #FF6B6B 0%, #FFA94D 100%);
                            padding: 12px;
                            border-radius: 10px;
                            text-align: center;
                            color: white;
                        ">
                            <div style="font-size: 0.8em; opacity: 0.9;">Calories</div>
                            <div style="font-size: 1.8em; font-weight: bold;">{nutrition.get('calories', 0):.0f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with nut_col2:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #845EF7 0%, #BE123C 100%);
                            padding: 12px;
                            border-radius: 10px;
                            text-align: center;
                            color: white;
                        ">
                            <div style="font-size: 0.8em; opacity: 0.9;">Protein</div>
                            <div style="font-size: 1.8em; font-weight: bold;">{nutrition.get('protein', 0):.0f}g</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with nut_col3:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
                            padding: 12px;
                            border-radius: 10px;
                            text-align: center;
                            color: white;
                        ">
                            <div style="font-size: 0.8em; opacity: 0.9;">Carbs</div>
                            <div style="font-size: 1.8em; font-weight: bold;">{nutrition.get('carbs', 0):.0f}g</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with nut_col4:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
                            padding: 12px;
                            border-radius: 10px;
                            text-align: center;
                            color: white;
                        ">
                            <div style="font-size: 0.8em; opacity: 0.9;">Sodium</div>
                            <div style="font-size: 1.8em; font-weight: bold;">{nutrition.get('sodium', 0):.0f}mg</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Modifications
                    if option.get("modifications"):
                        st.info(f"💡 **Tip:** {option['modifications']}")
                
                st.markdown("---")
        
        # Items to avoid
        if "items_to_avoid" in analysis and analysis["items_to_avoid"]:
            st.markdown("### ⚠️ Items to Avoid")
            
            for item in analysis["items_to_avoid"][:3]:
                st.warning(f"**{item.get('menu_item', 'N/A')}** - {item.get('concern', 'Not ideal')}")
                st.caption(item.get("reason", ""))
        
        # Special recommendations - only show if data is available
        if "special_recommendations" in analysis:
            specs = analysis["special_recommendations"]
            
            # Filter out N/A entries
            has_specs = False
            for key, value in specs.items():
                if isinstance(value, dict) and value.get("item") and value.get("item").lower() != "n/a":
                    has_specs = True
                    break
            
            if has_specs:
                st.markdown("### 🎯 Special Recommendations")
                
                rec_cols = st.columns(2)
                col_idx = 0
                
                if "best_for_calories" in specs and specs["best_for_calories"]:
                    item = specs["best_for_calories"]
                    if item.get("item") and item.get("item").lower() != "n/a":
                        with rec_cols[col_idx % 2]:
                            st.metric("🔥 Lowest Calorie", item.get("item", "N/A"), f"{item.get('calories', 0):.0f} cal")
                        col_idx += 1
                
                if "best_for_protein" in specs and specs["best_for_protein"]:
                    item = specs["best_for_protein"]
                    if item.get("item") and item.get("item").lower() != "n/a":
                        with rec_cols[col_idx % 2]:
                            st.metric("💪 Highest Protein", item.get("item", "N/A"), f"{item.get('protein', 0):.0f}g")
                        col_idx += 1
                
                if "best_for_fiber" in specs and specs["best_for_fiber"]:
                    item = specs["best_for_fiber"]
                    if item.get("item") and item.get("item").lower() != "n/a":
                        with rec_cols[col_idx % 2]:
                            st.metric("🌾 Highest Fiber", item.get("item", "N/A"), f"{item.get('fiber', 0):.0f}g")
                        col_idx += 1
                
                if "best_for_health_conditions" in specs and specs["best_for_health_conditions"]:
                    item = specs["best_for_health_conditions"]
                    if item.get("item") and item.get("item").lower() != "n/a":
                        with rec_cols[col_idx % 2]:
                            st.metric("🏥 Best for Your Health", item.get("item", "N/A"), item.get("reason", ""))
                        col_idx += 1
        
        # Tips
        if "general_tips" in analysis:
            st.markdown("### 💡 General Tips")
            st.info(analysis["general_tips"])


# ==================== HELP & ABOUT PAGE ====================

def help_page():
    """Help and About page"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0D847F 0%, #10A19D 50%, #52C4B8 100%);
        padding: 24px 32px;
        border-radius: 16px;
        margin: -1rem -1rem 24px -1rem;
        box-shadow: 
            0 8px 32px rgba(16, 161, 157, 0.3),
            inset 0 1px 1px rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.15);
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 100% 0%, rgba(255, 255, 255, 0.15) 0%, transparent 50%);
            pointer-events: none;
        "></div>
        <h1 style="
            color: white; 
            margin: 0; 
            font-size: 1.75em; 
            font-weight: 700;
            line-height: 1.2;
            position: relative;
            z-index: 1;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <span style="font-size: 1.3em;">❓</span>
            <span>Help & About</span>
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["About & Features", "How to Use", "FAQ & Tips"])
    
    with tab1:
        st.markdown("## About EatWise")
        st.markdown("""
        **EatWise** is an AI-powered nutrition tracker that helps you log meals, understand your eating patterns, and achieve your health goals. Log with text or photos, get personalized coaching, and dine out confidently with smart restaurant recommendations.
        
        **v2.6.2** | December 2025
        """)
        
        st.markdown("## Key Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📝 Meal Logging")
            st.markdown("""
            Text-based meal descriptions, food photo recognition, and nutritional analysis across multiple meal types.
            """)
            
            st.markdown("### 📊 Analytics Dashboard")
            st.markdown("""
            Daily nutrition trends, macronutrient distribution, and calorie tracking progress.
            """)
            
            st.markdown("### 💡 Smart Insights")
            st.markdown("""
            AI-powered health analysis with personalized recommendations tailored to your profile.
            """)
        
        with col2:
            st.markdown("### 📋 Meal History")
            st.markdown("""
            Browse, edit, and delete logged meals with date range filtering.
            """)
            
            st.markdown("### 🎯 AI Nutrition Coaching")
            st.markdown("""
            Chat with your AI coach for personalized nutrition guidance based on your profile and goals.
            """)
            
            st.markdown("### 🍽️ Restaurant Menu Analyzer")
            st.markdown("""
            Get personalized recommendations, healthier modifications, and item suggestions for dining out.
            """)
    
    with tab2:
        st.markdown("## How to Use EatWise")
        
        st.markdown("### Step 1: Create Your Profile")
        st.markdown("""
        Go to **My Profile** and fill in your information:
        - Full name
        - Age group
        - Gender
        - Timezone
        - Health conditions
        - Dietary preferences
        - Health goal (maintain, gain, lose weight)
        """)
        
        st.markdown("### Step 2: Log Your Meals")
        st.markdown("""
        Visit **Log Meal** to add meals in two ways:
        
        **Text Method:**
        1. Describe what you ate in detail
        2. Select the meal type
        3. Click "Analyze Meal"
        4. Review the nutritional breakdown
        5. Click "Save This Meal"
        
        **Photo Method:**
        1. Upload a clear food photo
        2. Select the meal type
        3. Click "Analyze Photo"
        4. Review detected foods and nutrition
        5. Click "Save This Meal"
        """)
        
        st.markdown("### Step 3: Track Your Progress")
        st.markdown("""
        - **Dashboard**: Quick overview of today's nutrition
        - **Analytics**: View detailed trends over time
        - **Meal History**: Browse and edit past meals
        - **Insights**: Get AI-powered health recommendations
        """)
        
        st.markdown("### Step 4: Get Personalized Coaching (Optional)")
        st.markdown("""
        Visit **🎯 Coaching** to access your AI nutrition coach:
        
        **Chat with Coach:**
        1. Type your question or request in the message box
        2. Click **📤 Send** to get personalized advice
        3. Coach provides guidance based on your profile, health conditions, and current nutrition
        4. Continue the conversation naturally - coach remembers the context
        5. Click **🔄 Clear** to start a fresh conversation
        
        **What You Can Ask:**
        - "What should I eat for dinner?" → Gets personalized meal suggestions
        - "Is pasta healthy?" → Gets advice considering your health conditions
        - "How can I improve my diet?" → Gets strategies based on your profile
        - "What nutrients am I missing?" → Analysis based on your recent meals
        - "How much protein should I eat?" → Recommendations based on your age and goals
        - General nutrition questions tailored to your health situation
        """)
        
        st.markdown("### Step 5: Analyze Restaurant Menus (Optional)")
        st.markdown("""
        Before eating out, visit **🍽️ Eating Out** to get healthy recommendations:
        
        **Using Text Menu:**
        1. Click the "📝 Paste Menu Text" tab
        2. Copy and paste the full restaurant menu
        3. Click "🔍 Analyze Menu"
        4. Review recommendations, items to avoid, and modification tips
        
        **Using Menu Photo:**
        1. Click the "📸 Upload Menu Photo" tab
        2. Upload a clear photo of the menu
        3. Click "📸 Extract Text from Photo" (AI will read the menu for you)
        4. Review extracted text if needed
        5. Click "✅ Analyze Extracted Menu"
        6. Get personalized recommendations for what to order
        
        **What You Get:**
        - ⭐ Best Options: Recommendations tailored to your health profile
        - ⚠️ Items to Avoid: Dishes that don't align with your goals
        - 🎯 Special Recommendations: Lowest calorie, highest protein, etc.
        - 💡 Modification Tips: How to order healthier versions
        - 📊 Nutrition Cards: Beautiful breakdown of each meal option
        """)
    
    with tab3:
        st.markdown("## Frequently Asked Questions")
        
        with st.expander("❓ How accurate is the nutrition analysis?"):
            st.markdown("""
            Our **Hybrid Nutrition System** combines USDA database accuracy with AI intelligence:
            
            - **100+ common foods**: USDA-validated data (99%+ accurate)
            - **All other foods**: AI estimates (85-95% accurate)
            - Common meals (e.g., chicken + rice): Near-exact values
            - You always see which foods came from database vs. estimated
            """)
        
        with st.expander("❓ What foods are in your nutrition database?"):
            st.markdown("""
            **100+ common foods** with precise USDA values:
            
            Proteins (chicken, beef, salmon, eggs, beans), Vegetables (broccoli, spinach, carrots, peppers), Fruits (apples, bananas, berries, avocado), Grains (rice, pasta, bread, oats), Dairy (milk, yogurt, cheese), and common restaurant items.
            
            Missing a food? AI estimates based on similar foods—typically 85-95% accurate.
            """)
        
        with st.expander("❓ Can I edit or delete meals?"):
            st.markdown("""
            Yes! Go to **Meal History**, click Edit to modify details, or Delete to remove completely. Then log the correct information.
            """)
        
        with st.expander("❓ How do recommendations work?"):
            st.markdown("""
            Our AI analyzes your meal history, health profile, current nutrition levels, and dietary preferences—then generates personalized meal suggestions tailored to your goals.
            """)
        
        with st.expander("❓ How is my data stored?"):
            st.markdown("""
            Your data is securely stored in **Supabase** (PostgreSQL):
            - Encrypted in transit and at rest
            - GDPR compliant
            - Only meals and profile stored (no photos)
            """)
        
        with st.expander("❓ Can I trust the restaurant recommendations?"):
            st.markdown("""
            Our AI provides intelligent guidance, but remember:
            - Use recommendations as guidance, not exact values
            - Ask restaurants for nutrition info when available
            - Check modification tips (e.g., "sauce on the side")
            - Actual values may vary by restaurant and portion
            """)
        
        with st.expander("❓ What can I ask the AI Coach?"):
            st.markdown("""
            "What should I eat for dinner?" | "Is pasta healthy?" | "How can I improve my diet?" | "What nutrients am I missing?" | "How much protein should I eat?"
            
            Your coach provides personalized guidance based on your health conditions, age, dietary preferences, and nutrition goals.
            """)
        
        st.markdown("## Portion Estimation Tips")
        
        st.markdown("""
        **Accuracy depends on how clearly you describe your food:**
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **HIGH (±15%)**
            - "150g chicken, 200g rice, 1 tbsp oil"
            
            **MEDIUM (±20-25%)**
            - "A bowl of rice with chicken"
            
            **MEDIUM-LOW (±30-35%)**
            - "Some rice and chicken"
            
            **LOW (±40-50%)**
            - Photo with no text
            """)
        
        with col2:
            st.markdown("""
            **🎯 Improve Accuracy:**
            
            **Text:**
            - Use exact measurements (grams, cups, tbsp)
            - Specify cooking method
            - List all ingredients separately
            
            **Photo:**
            - Include size reference (coin, hand)
            - Good lighting & 45° angle
            - Add text description
            """)
        
        with st.expander("📝 Text Input Rules", expanded=False):
            st.markdown("""
            **Specific Measurements** = HIGH Accuracy
            - Weight: 150g, 400g, 2 oz
            - Volume: 1 cup, 200ml, 2 tbsp
            - Count: 2 eggs, 3 slices
            
            **Portion Descriptors** = MEDIUM Accuracy
            - "A bowl of" → ~250-350g
            - "A plate of" → ~300-400g
            - "A handful" → ~50-100g
            
            **Cooking Methods Matter**
            - Grilled/Baked: baseline
            - Boiled/Steamed: -10% calories
            - Pan-fried: +20% calories
            - Deep-fried: +50-100% calories
            
            **Common Mistakes**
            - Saying "with dressing" instead of "2 tbsp dressing"
            - Forgetting cooking fats (oil, butter)
            - Using "some" instead of specific amounts
            """)
        
        st.markdown("""
        ### Key Insight
        
        Even with ±30-40% variation in single meals, **weekly averages show only ±15% variation, and monthly patterns show ±5-10%**. Random errors cancel out over time! The most important thing is to log consistently.
        """)
    
    st.divider()
    st.markdown("""
    ### 📧 Need More Help?
    Have questions or suggestions? We'd love to hear from you!
    - **GitHub**: https://github.com/scmlewis/eatwise_ai
    - **Report Issues**: Create an issue on GitHub
    
    ---
    **Last Updated**: December 06, 2025 (v2.6.2)
    """)


# ==================== MAIN APP ====================

def main():
    """Main app logic"""
    
    # Add anchor for back-to-top functionality
    st.markdown('<a id="app-top"></a>', unsafe_allow_html=True)
    
    # Add comprehensive responsive mobile styling
    st.markdown("""
    <style>
        /* ========== MOBILE RESPONSIVE STYLING ========== */
        
        /* Base responsive adjustments */
        @media (max-width: 768px) {
            /* Main content area */
            .main .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                padding-top: 1rem !important;
                max-width: 100% !important;
            }
            
            /* Reduce heading sizes on mobile */
            h1 { font-size: 1.5em !important; }
            h2 { font-size: 1.3em !important; }
            h3 { font-size: 1.1em !important; }
            
            /* Make gradient headers more compact */
            .main [style*="linear-gradient"] {
                padding: 10px 15px !important;
                margin-bottom: 15px !important;
            }
            
            /* Streamlit columns responsive */
            [data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 0 !important;
            }
            
            /* Stack metrics vertically on mobile */
            [data-testid="metric-container"] {
                width: 100% !important;
                margin-bottom: 10px !important;
            }
            
            /* Make buttons full width */
            button {
                width: 100% !important;
                font-size: 14px !important;
                padding: 10px 16px !important;
            }
            
            /* Form inputs full width */
            input, textarea, select {
                width: 100% !important;
                font-size: 16px !important; /* Prevents zoom on iOS */
            }
            
            /* Text areas more compact */
            textarea {
                min-height: 120px !important;
            }
            
            /* Tables responsive - enable horizontal scroll */
            table {
                display: block;
                overflow-x: auto;
                white-space: nowrap;
                font-size: 12px !important;
            }
            
            /* Plotly charts responsive */
            [data-testid="stPlotlyChart"] {
                width: 100% !important;
                height: auto !important;
            }
            
            /* Expander more compact */
            [data-testid="stExpander"] {
                font-size: 14px !important;
            }
            
            /* Tabs more compact */
            [data-testid="stTabs"] button {
                font-size: 13px !important;
                padding: 8px 12px !important;
            }
            
            /* Reduce padding in containers */
            [data-testid="stVerticalBlock"] > div {
                padding-top: 0.5rem !important;
                padding-bottom: 0.5rem !important;
            }
            
            /* Image uploads */
            [data-testid="stFileUploader"] {
                font-size: 14px !important;
            }
            
            /* Make sidebar toggle more prominent */
            [data-testid="collapsedControl"] {
                width: 50px !important;
                height: 50px !important;
            }
        }
        
        /* Small mobile devices (phones in portrait) */
        @media (max-width: 480px) {
            .main .block-container {
                padding-left: 0.5rem !important;
                padding-right: 0.5rem !important;
            }
            
            h1 { font-size: 1.3em !important; }
            h2 { font-size: 1.1em !important; }
            
            button {
                font-size: 13px !important;
                padding: 8px 12px !important;
            }
            
            /* Compact stat cards */
            [style*="text-align: center"] {
                padding: 8px !important;
            }
            
            /* Smaller metric text */
            [data-testid="metric-container"] {
                font-size: 12px !important;
            }
        }
        
        /* Tablet and small desktop */
        @media (min-width: 769px) and (max-width: 1024px) {
            .main .block-container {
                padding-left: 2rem !important;
                padding-right: 2rem !important;
            }
        }
        
        /* Sidebar responsive adjustments */
        [data-testid="stSidebar"] {
            width: fit-content !important;
        }
        
        @media (max-width: 768px) {
            [data-testid="stSidebar"] {
                width: 280px !important;
            }
            
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
                font-size: 14px !important;
            }
            
            /* Compact sidebar stats */
            [data-testid="stSidebar"] [style*="font-size: 22px"] {
                font-size: 18px !important;
            }
            
            [data-testid="stSidebar"] [style*="font-size: 20px"] {
                font-size: 16px !important;
            }
        }
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
            word-wrap: break-word;
            overflow-wrap: break-word;
        }
        
        /* Make buttons in sidebar responsive */
        [data-testid="stSidebar"] button {
            word-wrap: break-word;
            white-space: normal !important;
        }
        
        /* Better text wrapping in sidebar */
        [data-testid="stSidebar"] p {
            word-wrap: break-word;
            overflow-wrap: break-word;
        }
        
        /* Navigation menu responsive */
        @media (max-width: 768px) {
            .css-1544g2n, .css-nahz7x {
                font-size: 13px !important;
            }
        }
        
        /* Cards and containers responsive */
        @media (max-width: 768px) {
            [style*="border-radius"] {
                border-radius: 10px !important;
            }
            
            [style*="padding: 12px"] {
                padding: 10px !important;
            }
            
            [style*="padding: 16px"] {
                padding: 12px !important;
            }
            
            [style*="padding: 20px"] {
                padding: 14px !important;
            }
        }
        
        /* Responsive floating button */
        @media (max-width: 768px) {
            .floating-back-to-top {
                bottom: 80px !important;
                right: 15px !important;
            }
            
            .floating-back-to-top a {
                width: 50px !important;
                height: 50px !important;
                font-size: 1.5em !important;
            }
        }
        
        /* Touch-friendly targets */
        @media (hover: none) and (pointer: coarse) {
            button, a, input[type="button"], input[type="submit"] {
                min-height: 44px !important; /* iOS recommendation */
                min-width: 44px !important;
            }
        }
        
        /* Prevent horizontal scroll */
        .main, [data-testid="stApp"] {
            overflow-x: hidden !important;
        }
        
        /* Optimize images for mobile */
        @media (max-width: 768px) {
            img {
                max-width: 100% !important;
                height: auto !important;
            }
        }
        
        /* Better spacing for mobile cards */
        @media (max-width: 768px) {
            [data-testid="stVerticalBlock"] > [data-testid="element-container"] {
                margin-bottom: 0.75rem !important;
            }
        }
        
        /* File uploader responsive */
        @media (max-width: 768px) {
            [data-testid="stFileUploadDropzone"] {
                padding: 1rem !important;
                min-height: 100px !important;
            }
            
            [data-testid="stFileUploadDropzone"] button {
                font-size: 13px !important;
            }
        }
        
        /* Dataframe responsive */
        @media (max-width: 768px) {
            [data-testid="stDataFrame"] {
                font-size: 12px !important;
            }
            
            [data-testid="stDataFrame"] td,
            [data-testid="stDataFrame"] th {
                padding: 4px 8px !important;
            }
        }
        
        /* Improve form layout on mobile */
        @media (max-width: 768px) {
            [data-testid="stForm"] {
                padding: 1rem 0.5rem !important;
            }
            
            [data-testid="stFormSubmitButton"] button {
                margin-top: 1rem !important;
            }
        }
        
        /* Selectbox and multiselect responsive */
        @media (max-width: 768px) {
            [data-testid="stSelectbox"],
            [data-testid="stMultiSelect"] {
                font-size: 14px !important;
            }
        }
        
        /* Date input responsive */
        @media (max-width: 768px) {
            [data-testid="stDateInput"] input {
                font-size: 16px !important;
            }
        }
        
        /* Number input responsive */
        @media (max-width: 768px) {
            [data-testid="stNumberInput"] input {
                font-size: 16px !important;
            }
        }
        
        /* Success/Warning/Error boxes responsive */
        @media (max-width: 768px) {
            [data-testid="stAlert"] {
                font-size: 13px !important;
                padding: 10px !important;
            }
        }
        
        /* Spinner responsive */
        @media (max-width: 768px) {
            [data-testid="stSpinner"] > div {
                font-size: 14px !important;
            }
        }
        
        /* Progress bar responsive */
        @media (max-width: 768px) {
            [data-testid="stProgress"] {
                height: 8px !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    if not is_authenticated():
        login_page()
    else:
        if st.session_state.user_email:
            user_profile = get_or_load_user_profile()
            # Prefetch daily data once for sidebar and dashboard to avoid duplicate DB hits
            today_snapshot = load_daily_snapshot(user_profile, days_back=30)
            dashboard_prefetch = {}
            seven_day_threshold = today_snapshot["today"] - timedelta(days=7)
            recent_meals_7d = []
            recent_meal_dates_7d = []
            for meal, meal_dt in zip(today_snapshot["recent_meals"], today_snapshot["recent_meal_dates"]):
                if meal_dt and meal_dt.date() >= seven_day_threshold:
                    recent_meals_7d.append(meal)
                    recent_meal_dates_7d.append(meal_dt)
            dashboard_prefetch.update(today_snapshot)
            dashboard_prefetch["recent_meals_7d"] = recent_meals_7d
            dashboard_prefetch["recent_meal_dates_7d"] = recent_meal_dates_7d
            
            # Navigation pages dictionary
            pages = {
                "Dashboard": "📊",
                "Log Meal": "📝",
                "Analytics": "📈",
                "Meal History": "📋",
                "Insights": "💡",
                "Eating Out": "🍽️",
                "Coaching": "🎯",
                "My Profile": "👤",
                "Help": "❓",
            }
            
            # Check if quick navigation was triggered
            default_page = "Log Meal" if st.session_state.get("quick_nav_to_meal") else "Dashboard"
            default_index = list(pages.keys()).index(default_page)
            
            # Store nav index in session state
            if "nav_index" not in st.session_state:
                st.session_state.nav_index = default_index
            
            # Modern Navigation with option_menu in sidebar
            # Map pages to icons for better visual appeal
            page_icons = {
                "Dashboard": "house-fill",
                "Log Meal": "plus-circle-fill",
                "Analytics": "bar-chart-fill",
                "Meal History": "clock-history",
                "Insights": "lightbulb-fill",
                "Coaching": "chat-dots-fill",
                "My Profile": "person-fill",
                "Help": "question-circle-fill"
            }
            
            # Add EatWise header above navigation menu
            st.sidebar.markdown(f"""
            <div style="text-align: center; margin-bottom: 16px;">
                <h2 style="color: #10A19D; margin: 0; font-size: 1.6em;">🥗 EatWise</h2>
            </div>
            """, unsafe_allow_html=True)
            
            with st.sidebar:
                selected_page = option_menu(
                    menu_title=None,
                    options=list(pages.keys()),
                    icons=[page_icons.get(page, "circle-fill") for page in pages.keys()],
                    menu_icon="cast",
                    default_index=st.session_state.nav_index,
                    orientation="vertical",
                    key="page_selector"
                )
            st.session_state.nav_index = list(pages.keys()).index(selected_page)
            st.session_state.current_page = selected_page
            
            st.sidebar.markdown("<div style='margin: 12px 0;'></div>", unsafe_allow_html=True)
            
            # ===== QUICK STATS IN SIDEBAR - COMPACT SINGLE ROW =====
            # Get today's data for sidebar stats from the prefetched snapshot
            today_nutrition = today_snapshot["daily_nutrition"]
            streak_info = today_snapshot["streak_info"]
            current_streak = streak_info.get('current_streak', 0)
            water_goal = user_profile.get("water_goal_glasses", 8) if user_profile else 8
            water_today = today_snapshot["water_intake"]
            cal_display = int(today_nutrition.get('calories', 0))
            
            # Create three-column compact stats (Streak, Calories, Water)
            stat_cols = st.sidebar.columns(3, gap="medium")
            
            with stat_cols[0]:
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 22px; font-weight: bold; color: #FFB84D; margin-bottom: 4px;">{current_streak}</div>
                    <div style="font-size: 11px; color: #e0f2f1; font-weight: 500;">Streak</div>
                </div>
                """, unsafe_allow_html=True)
            
            with stat_cols[1]:
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 20px; font-weight: bold; color: #FFB84D; margin-bottom: 4px;">{cal_display}</div>
                    <div style="font-size: 11px; color: #e0f2f1; font-weight: 500;">Calories</div>
                </div>
                """, unsafe_allow_html=True)
            
            with stat_cols[2]:
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 20px; font-weight: bold; color: #3B82F6; margin-bottom: 4px;">{water_today}/{water_goal}</div>
                    <div style="font-size: 11px; color: #e0f2f1; font-weight: 500;">Water</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.sidebar.markdown("<div style='margin: 12px 0;'></div>", unsafe_allow_html=True)
            
            # User info - Below stats
            st.sidebar.markdown(f"👤 **{st.session_state.user_email}**")
            
            # Logout button
            if st.sidebar.button("🚪 Logout", key="logout_btn", use_container_width=True):
                st.session_state.auth_manager.logout()
                st.session_state.clear()
                st.success("✅ Logged out!")
                st.rerun()
            
            st.sidebar.markdown("<div style='margin: 8px 0;'></div>", unsafe_allow_html=True)
            
            # Clear the quick nav flag
            if st.session_state.get("quick_nav_to_meal"):
                st.session_state.quick_nav_to_meal = False
            
            # Route to selected page
            if st.session_state.current_page == "Dashboard":
                dashboard_page(dashboard_prefetch)
            elif st.session_state.current_page == "Log Meal":
                meal_logging_page()
            elif st.session_state.current_page == "Analytics":
                analytics_page()
            elif st.session_state.current_page == "Meal History":
                meal_history_page()
            elif st.session_state.current_page == "Insights":
                insights_page()
            elif st.session_state.current_page == "Eating Out":
                restaurant_analyzer_page()
            elif st.session_state.current_page == "Coaching":
                coaching_assistant_page()
            elif st.session_state.current_page == "My Profile":
                profile_page()
            elif st.session_state.current_page == "Help":
                help_page()


if __name__ == "__main__":
    main()

# Add floating back-to-top button (anchor-based) but only show when authenticated
if is_authenticated():
    st.markdown("""
    <style>
    .floating-back-to-top {
        position: fixed;
        bottom: 100px;
        right: 25px;
        z-index: 999;
    }

    .floating-back-to-top a {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #10A19D 0%, #52C4B8 100%);
        color: white;
        border-radius: 50%;
        text-decoration: none;
        font-size: 1.8em;
        box-shadow: 0 6px 20px rgba(16, 161, 157, 0.5);
        transition: all 0.3s ease;
        border: 2px solid rgba(255, 255, 255, 0.3);
        line-height: 1;
        font-weight: bold;
    }

    .floating-back-to-top a:hover {
        transform: translateY(-8px) scale(1.1);
        box-shadow: 0 10px 30px rgba(16, 161, 157, 0.7);
        border-color: rgba(255, 255, 255, 0.5);
    }

    .floating-back-to-top a:active {
        transform: translateY(-4px) scale(1.05);
    }
    </style>

    <div class="floating-back-to-top">
        <a href="#app-top" title="Back to top">↑</a>
    </div>
    """, unsafe_allow_html=True)
