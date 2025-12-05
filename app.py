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
import io
import csv
import base64
from streamlit_option_menu import option_menu

# Import modules
from config import (
    APP_NAME, APP_DESCRIPTION, SUPABASE_URL, SUPABASE_KEY,
    DAILY_CALORIE_TARGET, DAILY_PROTEIN_TARGET, DAILY_CARBS_TARGET,
    DAILY_FAT_TARGET, DAILY_SODIUM_TARGET, DAILY_SUGAR_TARGET, 
    DAILY_FIBER_TARGET, AGE_GROUP_TARGETS, HEALTH_CONDITION_TARGETS, HEALTH_GOAL_TARGETS,
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
    get_nutrition_status, format_nutrition_dict, get_streak_info,
    get_earned_badges, build_nutrition_by_date, paginate_items,
    show_skeleton_loader, render_icon, get_nutrition_icon
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




# ==================== COMPONENT HELPERS ====================
# Production-grade card and component styling functions



def error_state(title: str, message: str, suggestion: str = None, icon: str = "⚠️"):
    """
    Display a professional error state with helpful suggestions.
    
    Args:
        title: Error title
        message: Error description
        suggestion: Helpful suggestion to resolve the issue
        icon: Error icon emoji
    """
    html_content = f"""
    <div style="
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 138, 138, 0.05) 100%);
        border: 1px solid rgba(255, 107, 107, 0.3);
        border-left: 4px solid #FF6B6B;
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
    ">
        <div style="display: flex; align-items: flex-start; gap: 12px;">
            <div style="font-size: 24px; margin-top: 2px;">{icon}</div>
            <div style="flex: 1;">
                <div style="
                    font-size: 16px;
                    font-weight: bold;
                    color: #FF6B6B;
                    margin-bottom: 8px;
                ">{title}</div>
                <div style="
                    font-size: 14px;
                    color: #a0a0a0;
                    margin-bottom: 12px;
                    line-height: 1.5;
                ">{message}</div>
    """
    
    if suggestion:
        html_content += f"""
                <div style="
                    background: rgba(16, 161, 157, 0.1);
                    border-left: 2px solid #10A19D;
                    padding: 12px;
                    border-radius: 6px;
                    font-size: 13px;
                    color: #10A19D;
                    margin-top: 12px;
                ">
                    💡 <strong>Suggestion:</strong> {suggestion}
                </div>
        """
    
    html_content += """
            </div>
        </div>
    </div>
    """
    
    st.markdown(html_content, unsafe_allow_html=True)


def success_state(title: str, message: str, icon: str = "✅"):
    """
    Display a professional success state.
    
    Args:
        title: Success title
        message: Success description
        icon: Success icon emoji
    """
    html_content = f"""
    <div style="
        background: linear-gradient(135deg, rgba(81, 207, 102, 0.1) 0%, rgba(128, 195, 66, 0.05) 100%);
        border: 1px solid rgba(81, 207, 102, 0.3);
        border-left: 4px solid #51CF66;
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
    ">
        <div style="display: flex; align-items: flex-start; gap: 12px;">
            <div style="font-size: 24px; margin-top: 2px;">{icon}</div>
            <div style="flex: 1;">
                <div style="
                    font-size: 16px;
                    font-weight: bold;
                    color: #51CF66;
                    margin-bottom: 8px;
                ">{title}</div>
                <div style="
                    font-size: 14px;
                    color: #a0a0a0;
                    line-height: 1.5;
                ">{message}</div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(html_content, unsafe_allow_html=True)


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
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&display=swap');
    @import url('https://cdn.jsdelivr.net/npm/tabler-icons@latest/tabler-icons.min.css');
    
    :root {
        --primary-color: #10A19D;
        --primary-dark: #0D7A76;
        --primary-light: #52C4B8;
        --secondary-color: #FF6B6B;
        --success-color: #51CF66;
        --warning-color: #FFA500;
        --danger-color: #FF0000;
        --accent-purple: #845EF7;
        --accent-blue: #3B82F6;
        --font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    }
    
    /* Apply Outfit font globally */
    html, body, [class*="css"] {
        font-family: var(--font-family) !important;
    }
    
    .main {
        padding-top: 2rem;
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
    }
    
    h1, h2, h3 {
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Modern gradient cards */
    .gradient-primary {
        background: linear-gradient(135deg, #10A19D 0%, #52C4B8 100%);
    }
    
    .gradient-purple {
        background: linear-gradient(135deg, #845EF7 0%, #BE80FF 100%);
    }
    
    .gradient-blue {
        background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%);
    }
    
    .gradient-success {
        background: linear-gradient(135deg, #51CF66 0%, #80C342 100%);
    }
    
    .gradient-warning {
        background: linear-gradient(135deg, #FFA500 0%, #FFB84D 100%);
    }
    
    .gradient-danger {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8A8A 100%);
    }
    
    .metric-card {
        background: rgba(16, 161, 157, 0.08);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(82, 196, 184, 0.3);
        padding: 16px;
        border-radius: 12px;
        color: white;
        margin: 8px 0;
        box-shadow: 
            0 1px 3px rgba(0, 0, 0, 0.12),
            0 4px 12px rgba(16, 161, 157, 0.15),
            0 8px 24px rgba(16, 161, 157, 0.1);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        background: rgba(16, 161, 157, 0.12);
        border-color: rgba(82, 196, 184, 0.5);
        box-shadow: 
            0 2px 4px rgba(0, 0, 0, 0.15),
            0 8px 16px rgba(16, 161, 157, 0.25),
            0 16px 32px rgba(16, 161, 157, 0.15);
    }
    
    /* Glass morphism for all cards */
    [data-testid="stColumn"] {
        backdrop-filter: blur(5px);
    }
    
    .card-glass {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 16px;
        box-shadow: 
            0 1px 3px rgba(0, 0, 0, 0.1),
            0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    .nutrition-bar {
        height: 8px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        overflow: hidden;
        margin: 5px 0;
        box-shadow: 
            inset 0 2px 4px rgba(0, 0, 0, 0.2),
            0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .nutrition-bar > div {
        transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(82, 196, 184, 0.3);
    }
    
    .success {
        color: #51CF66;
    }
    
    .warning {
        color: #FFA500;
    }
    
    .danger {
        color: #FF0000;
    }
    
    /* Modern buttons with enhanced shadows */
    .stButton > button {
        background: linear-gradient(135deg, #10A19D 0%, #52C4B8 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 2px 4px rgba(0, 0, 0, 0.1),
            0 4px 12px rgba(16, 161, 157, 0.25),
            0 8px 24px rgba(16, 161, 157, 0.15);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 
            0 4px 8px rgba(0, 0, 0, 0.12),
            0 8px 20px rgba(16, 161, 157, 0.35),
            0 12px 32px rgba(16, 161, 157, 0.2);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }
    
    /* Tabs styling with glass morphism */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        margin-bottom: 1.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(16, 161, 157, 0.08);
        backdrop-filter: blur(8px);
        border-radius: 12px;
        padding: 12px 20px;
        border: 1px solid rgba(82, 196, 184, 0.2);
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(16, 161, 157, 0.12);
        border-color: rgba(82, 196, 184, 0.4);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #10A19D 0%, #52C4B8 100%);
        border-color: rgba(82, 196, 184, 0.8);
        color: white;
        box-shadow: 
            0 2px 4px rgba(0, 0, 0, 0.15),
            0 4px 12px rgba(16, 161, 157, 0.3);
    }
    
    /* Ensure sidebar expansion on all screen sizes after login */
    section[data-testid="stSidebar"] > div {
        width: 250px !important;
    }
    
    /* ===== ACCESSIBILITY IMPROVEMENTS ===== */
    
    /* Input focus states - WCAG AA compliant */
    input:focus, textarea:focus, select:focus {
        outline: 2px solid #10A19D !important;
        outline-offset: 2px !important;
        border-color: #10A19D !important;
        box-shadow: 0 0 0 3px rgba(16, 161, 157, 0.25) !important;
    }
    
    input:focus-visible, textarea:focus-visible, select:focus-visible {
        outline: 2px solid #10A19D !important;
        outline-offset: 2px !important;
    }
    
    /* Better button focus indicators */
    button:focus-visible {
        outline: 2px solid #10A19D !important;
        outline-offset: 2px !important;
    }
    
    /* Disabled state indicators for accessibility */
    button:disabled, input:disabled, select:disabled, textarea:disabled {
        opacity: 0.6 !important;
        cursor: not-allowed !important;
    }
    
    /* Ensure readable text in all states */
    button, input, select, textarea {
        min-height: 44px;
        font-size: 14px;
        line-height: 1.5;
    }
    
    /* Selectbox hover effect */
    [data-testid="stSelectbox"] {
        transition: all 0.2s ease;
    }
    
    /* Selectbox focus styling */
    [data-testid="stSelectbox"]:focus-within {
        transform: translateY(-1px);
    }
    
    /* Better link styling for contrast */
    a {
        color: #10A19D;
        text-decoration: underline;
        transition: all 0.2s ease;
    }
    
    a:hover {
        color: #52C4B8;
        text-decoration-thickness: 2px;
    }
    
    a:focus {
        outline: 2px solid #10A19D;
        outline-offset: 2px;
    }
    
    /* Skip to main content link (hidden by default) */
    .skip-to-main {
        position: absolute;
        left: -9999px;
        z-index: 999;
    }
    
    .skip-to-main:focus {
        position: fixed;
        top: 10px;
        left: 10px;
        padding: 10px 20px;
        background: #10A19D;
        color: white;
        text-decoration: none;
        border-radius: 4px;
        z-index: 1000;
    }
    
    /* Ensure sufficient color contrast for semantic colors */
    .success {
        color: #51CF66;
        font-weight: 600;
    }
    
    .warning {
        color: #FFD43B;
        font-weight: 600;
    }
    
    .danger {
        color: #FF6B6B;
        font-weight: 600;
    }
    
    .info {
        color: #3B82F6;
        font-weight: 600;
    }
    
    /* ===== MEAL CARD HOVER EFFECTS ===== */
    .meal-card {
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        cursor: pointer;
    }
    
    .meal-card:hover {
        transform: scale(1.03);
        box-shadow: 0 12px 32px rgba(16, 161, 157, 0.3) !important;
    }
    
    /* ===== NUTRITION INFO CARD HOVER EFFECTS ===== */
    .nutrition-info {
        transition: filter 0.3s ease, box-shadow 0.3s ease;
    }
    
    .nutrition-info:hover {
        filter: brightness(0.95);
        box-shadow: 0 10px 28px rgba(16, 161, 157, 0.35) !important;
    }
    
    /* ===== BADGE/ACHIEVEMENT CARD HOVER EFFECTS ===== */
    .badge-achievement {
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        cursor: pointer;
    }
    
    .badge-achievement:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 40px rgba(16, 161, 157, 0.4),
                    0 0 20px rgba(16, 161, 157, 0.3) !important;
    }
    
    /* ===== INSIGHT CARD HOVER EFFECTS ===== */
    .insight-box {
        border: 2px solid rgba(16, 161, 157, 0.2);
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    
    .insight-box:hover {
        border-color: #10A19D;
        box-shadow: 0 8px 20px rgba(16, 161, 157, 0.25) !important;
    }
    
    /* ===== STAT CARD HOVER EFFECTS ===== */
    .stat-card {
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        cursor: pointer;
    }
    
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 28px rgba(16, 161, 157, 0.3) !important;
    }
    
    /* ===== CHART CONTAINER HOVER EFFECTS ===== */
    .chart-container {
        transition: box-shadow 0.3s ease, border-color 0.3s ease;
        border: 1px solid rgba(16, 161, 157, 0.2);
    }
    
    .chart-container:hover {
        box-shadow: 0 10px 30px rgba(16, 161, 157, 0.25) !important;
        border-color: rgba(16, 161, 157, 0.5);
    }
    
    /* ===== SUMMARY/PROGRESS CARD HOVER EFFECTS ===== */
    .summary-card {
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .summary-card:hover {
        transform: scale(1.02) translateY(-2px);
        box-shadow: 0 12px 32px rgba(16, 161, 157, 0.35) !important;
    }
    
    /* ===== MACRO BREAKDOWN BOX HOVER EFFECTS ===== */
    .macro-box {
        transition: all 0.3s ease;
        border: 1px solid rgba(16, 161, 157, 0.3);
    }
    
    .macro-box:hover {
        border-color: #10A19D;
        box-shadow: 0 10px 28px rgba(16, 161, 157, 0.3) !important;
    }
    
    /* ===== DASHBOARD INFO BOXES WITH FADE-IN ANIMATION ===== */
    @keyframes dashboardFadeIn {
        from { 
            opacity: 0; 
            transform: translateY(10px);
        }
        to { 
            opacity: 1; 
            transform: translateY(0);
        }
    }
    
    .dashboard-info-box {
        animation: dashboardFadeIn 0.4s ease-out;
        transition: all 0.3s ease;
    }
    
    .dashboard-info-box:hover {
        border-color: rgba(16, 161, 157, 0.8) !important;
        box-shadow: 0 10px 28px rgba(16, 161, 157, 0.3) !important;
    }
    
    /* ===== PATTERN/TIMING CARD HOVER EFFECTS ===== */
    .pattern-card {
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .pattern-card:hover {
        background: rgba(16, 161, 157, 0.15) !important;
        box-shadow: 0 8px 20px rgba(16, 161, 157, 0.25) !important;
    }
    
    /* ===== HEALTH METRIC BOX HOVER EFFECTS ===== */
    .health-metric {
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .health-metric:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 32px rgba(16, 161, 157, 0.3) !important;
    }
    
    /* ===== STREAK BOX HOVER EFFECTS ===== */
    .streak-box {
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .streak-box:hover {
        transform: scale(1.03) translateY(-2px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* ===== PROFILE SECTION HOVER EFFECTS ===== */
    .profile-section {
        transition: all 0.3s ease;
        border: 1px solid rgba(16, 161, 157, 0.2);
    }
    
    .profile-section:hover {
        border-color: rgba(16, 161, 157, 0.6);
        box-shadow: 0 8px 24px rgba(16, 161, 157, 0.2) !important;
    }
    
    /* ===== SUGGESTION/RECOMMENDATION CARD HOVER EFFECTS ===== */
    .suggestion-card {
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .suggestion-card:hover {
        transform: translateX(4px) translateY(-2px);
        box-shadow: 0 10px 28px rgba(16, 161, 157, 0.3) !important;
    }
    
    /* Reduce motion for users who prefer it */
    @media (prefers-reduced-motion: reduce) {
        * {
            animation: none !important;
            transition: none !important;
        }
    }
    
    /* High contrast mode support */
    @media (prefers-contrast: more) {
        input:focus, textarea:focus, select:focus, button:focus {
            outline: 3px solid #10A19D !important;
            outline-offset: 3px !important;
        }
        
        button:disabled {
            opacity: 0.3 !important;
            border: 2px solid #999 !important;
        }
    }
    
    /* ===== ENTRANCE ANIMATIONS ===== */
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    @keyframes slideUpFade {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideDownFade {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes scaleIn {
        from {
            opacity: 0;
            transform: scale(0.95);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    /* Apply entrance animations to main containers */
    .main {
        animation: fadeIn 0.5s ease-out;
    }
    
    [data-testid="stMetricDelta"] {
        animation: slideUpFade 0.6s ease-out;
    }
    
    [data-testid="stMetric"] {
        animation: slideUpFade 0.6s ease-out;
    }
    
    .stTabs [role="tablist"] {
        animation: slideDownFade 0.5s ease-out;
    }
    
    /* Card entrance animations with stagger */
    .meal-card {
        animation: scaleIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .metric-card {
        animation: slideUpFade 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stat-card {
        animation: scaleIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .nutrition-info {
        animation: slideUpFade 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* ===== LOADING SKELETONS ===== */
    .skeleton {
        background: linear-gradient(
            90deg,
            rgba(16, 161, 157, 0.08) 0%,
            rgba(16, 161, 157, 0.15) 50%,
            rgba(16, 161, 157, 0.08) 100%
        );
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 8px;
    }
    
    @keyframes shimmer {
        0% {
            background-position: -200% 0;
        }
        100% {
            background-position: 200% 0;
        }
    }
    
    .skeleton-text {
        height: 14px;
        margin-bottom: 8px;
        border-radius: 4px;
        display: block;
    }
    
    .skeleton-heading {
        height: 24px;
        margin-bottom: 16px;
        border-radius: 4px;
        display: block;
        width: 60%;
    }
    
    .skeleton-card {
        background: rgba(16, 161, 157, 0.06);
        border: 1px solid rgba(16, 161, 157, 0.1);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
    }
    
    .skeleton-card .skeleton-heading {
        margin-top: 0;
    }
    
    .skeleton-line {
        height: 12px;
        margin-bottom: 12px;
        border-radius: 4px;
    }
    
    .skeleton-line:last-child {
        margin-bottom: 0;
    }
    
    .skeleton-bar {
        height: 40px;
        margin-bottom: 12px;
        border-radius: 8px;
    }
    
    /* Icon styling for integration with icon libraries */
    .icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        vertical-align: middle;
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
    
    .icon-primary {
        color: #10A19D;
    }
    
    .icon-success {
        color: #51CF66;
    }
    
    .icon-warning {
        color: #FFD43B;
    }
    
    .icon-danger {
        color: #FF6B6B;
    }
    
    .icon-info {
        color: #3B82F6;
    }
    
    .icon-secondary {
        color: #845EF7;
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

# ==================== EXPORT & SHARE FUNCTIONS ====================

def generate_nutrition_report(meals: List, daily_nutrition: Dict, targets: Dict, report_type: str = "weekly") -> str:
    """Generate a text-based nutrition report"""
    report = f"🥗 EatWise Nutrition Report ({report_type.title()})\n"
    report += "=" * 50 + "\n\n"
    
    report += "📊 SUMMARY\n"
    report += "-" * 50 + "\n"
    report += f"Total Meals Logged: {len(meals)}\n"
    report += f"Average Daily Calories: {daily_nutrition.get('calories', 0):.0f} / {targets.get('calories', 2000)}\n"
    report += f"Average Daily Protein: {daily_nutrition.get('protein', 0):.1f}g / {targets.get('protein', 50)}g\n"
    report += f"Average Daily Carbs: {daily_nutrition.get('carbs', 0):.1f}g / {targets.get('carbs', 300)}g\n"
    report += f"Average Daily Fat: {daily_nutrition.get('fat', 0):.1f}g / {targets.get('fat', 65)}g\n\n"
    
    report += "📋 MEAL LIST\n"
    report += "-" * 50 + "\n"
    for meal in meals[:20]:  # Last 20 meals
        report += f"• {meal.get('meal_name')} ({meal.get('meal_type')})\n"
        report += f"  {meal.get('description', 'N/A')}\n"
        nutrition = meal.get('nutrition', {})
        report += f"  Calories: {nutrition.get('calories', 0):.0f} | Protein: {nutrition.get('protein', 0):.1f}g\n\n"
    
    report += "=" * 50 + "\n"
    report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    
    return report


def generate_csv_export(meals: List) -> str:
    """Generate a CSV export of meals"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Date', 'Meal Name', 'Type', 'Calories', 'Protein (g)', 'Carbs (g)', 'Fat (g)', 'Sodium (mg)', 'Sugar (g)', 'Fiber (g)', 'Description'])
    
    # Write meal data
    for meal in meals:
        nutrition = meal.get('nutrition', {})
        logged_at = meal.get('logged_at', '').split('T')[0] if meal.get('logged_at') else ''
        
        writer.writerow([
            logged_at,
            meal.get('meal_name', ''),
            meal.get('meal_type', ''),
            f"{nutrition.get('calories', 0):.0f}",
            f"{nutrition.get('protein', 0):.1f}",
            f"{nutrition.get('carbs', 0):.1f}",
            f"{nutrition.get('fat', 0):.1f}",
            f"{nutrition.get('sodium', 0):.0f}",
            f"{nutrition.get('sugar', 0):.1f}",
            f"{nutrition.get('fiber', 0):.1f}",
            meal.get('description', '')
        ])
    
    return output.getvalue()


# ==================== AUTHENTICATION PAGES ====================

def login_page():
    """Login and signup page"""
    auth_manager = st.session_state.auth_manager
    # Add custom CSS for login page with full-page background
    st.markdown("""
    <style>
        /* Apply gradient to entire page when on login */
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 25%, #0D7A76 75%, #063d3a 100%) !important;
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
                radial-gradient(circle at 20% 50%, rgba(16, 161, 157, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(82, 196, 184, 0.1) 0%, transparent 50%);
            pointer-events: none;
            z-index: 1;
        }
        
        .main {
            background: transparent !important;
        }
        
        .login-container {
            display: flex;
            gap: 20px;
            align-items: stretch;
        }
        
        .login-hero {
            flex: 1;
            background: linear-gradient(135deg, #10A19D 0%, #52C4B8 100%);
            padding: 30px;
            border-radius: 20px;
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 10px 40px rgba(16, 161, 157, 0.3);
        }
        
        .login-hero h1 {
            font-size: 2.2em;
            margin: 0 0 8px 0;
            font-weight: 800;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.4), 
                         0 0 8px rgba(0, 0, 0, 0.3);
        }
        
        .login-hero h2 {
            font-size: 1.1em;
            margin: 0 0 15px 0;
            font-weight: 300;
            opacity: 0.95;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
        }
        
        .login-hero ul {
            font-size: 0.9em;
            line-height: 1.4;
        }
        
        .login-hero li {
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 10px;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
        }
        
        .login-form-container {
            flex: 1;
            background: linear-gradient(135deg, #0D7A7620 0%, #10A19D10 100%);
            padding: 30px;
            border-radius: 20px;
            border: 2px solid #10A19D;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            box-shadow: 0 10px 40px rgba(16, 161, 157, 0.15);
        }
        
        .login-header {
            margin-bottom: 2px;
            text-align: center;
            padding: 8px 0;
        }
        
        .login-header h3 {
            color: #52C4B8;
            font-size: 1.3em;
            margin: 0;
            margin-bottom: 2px;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
        }
        
        .login-header p {
            margin: 0 !important;
            padding: 0 !important;
        }
        
        .login-tabs {
            margin-top: 20px;
            margin-bottom: 15px;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background: transparent;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border: 2px solid #10A19D40;
            border-radius: 10px;
            color: #d0e0df;
            padding: 8px 16px;
            font-weight: 600;
            font-size: 0.9em;
        }
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #10A19D 0%, #52C4B8 100%);
            color: white;
            border: 2px solid #10A19D;
        }
        
        .form-input-group {
            margin-bottom: 12px;
        }
        
        .form-input-group label {
            display: block;
            margin-bottom: 6px;
            color: #c8f0ed;
            font-weight: 600;
            font-size: 0.85em;
        }
        
        .stTextInput {
            margin-bottom: 15px !important;
        }
        
        .stTextInput input {
            background: #0a0e27 !important;
            color: #e0f2f1 !important;
            border: 2px solid #10A19D40 !important;
            border-radius: 10px !important;
            padding: 10px 12px !important;
            font-size: 0.9em !important;
        }
        
        .stTextInput input::placeholder {
            color: #7a9a98 !important;
            opacity: 0.8 !important;
        }
        
        .stTextInput input:focus {
            border: 2px solid #10A19D !important;
            box-shadow: 0 0 0 3px rgba(16, 161, 157, 0.2) !important;
        }
        
        .stCaption {
            color: #b8dbd9 !important;
        }
        button[kind="secondary"]:has-text("Forgot password?") {
            background: #4a5f5e !important;
            color: #a0a0a0 !important;
            border: 1px solid #5a6f6e !important;
        }
    </style>
    """, unsafe_allow_html=True)
    

    
    col1, col2 = st.columns([1.1, 1], gap="medium")
    
    with col1:
        st.markdown("""
        <div class="login-hero" style="padding-top: 30px;">
            <h1 style="font-size: 3em; margin: 0 0 20px 0; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.4);">EatWise</h1>
            <h2>Your AI-Powered Nutrition Hub</h2>
            <p style="font-size: 0.95em; opacity: 0.9; margin-bottom: 15px; text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);">
                Transform your eating habits with intelligent meal tracking and personalized nutrition insights.
            </p>
            <ul style="list-style: none; padding: 0;">
                <li>📸 Smart meal logging (text or photo)</li>
                <li>📊 Instant nutritional analysis</li>
                <li>📈 Habit tracking and progress monitoring</li>
                <li>💡 AI-powered personalized suggestions</li>
                <li>🎮 Gamification with badges and streaks</li>
            </ul>
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


def dashboard_page():
    """Dashboard/Home page"""
    # Get user profile (handles loading and caching automatically)
    user_profile = get_or_load_user_profile()
    
    # Get user's timezone for greeting
    user_timezone = user_profile.get("timezone", "UTC")
    st.markdown(f"# {get_greeting(user_timezone)} 👋")
    
    # Get today's meals and nutrition
    today = date.today()
    meals = db_manager.get_meals_by_date(st.session_state.user_id, today)
    daily_nutrition = db_manager.get_daily_nutrition_summary(st.session_state.user_id, today)
    
    # ===== STREAK NOTIFICATIONS & MOTIVATIONAL BANNERS =====
    days_back = 7
    end_date = today
    start_date = end_date - timedelta(days=days_back)
    recent_meals = db_manager.get_meals_in_range(st.session_state.user_id, start_date, end_date)
    
    # Get streak info
    meal_dates = [datetime.fromisoformat(m.get("logged_at", "")) for m in recent_meals]
    streak_info = get_streak_info(meal_dates)
    current_streak = streak_info['current_streak']
    longest_streak = streak_info['longest_streak']
    
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
    
    # Get nutrition targets
    age_group = user_profile.get("age_group", "26-35")
    targets = AGE_GROUP_TARGETS.get(age_group, AGE_GROUP_TARGETS["26-35"])
    
    # Apply health condition adjustments
    health_conditions = user_profile.get("health_conditions", [])
    for condition in health_conditions:
        if condition in HEALTH_CONDITION_TARGETS:
            targets.update(HEALTH_CONDITION_TARGETS[condition])
    
    # Apply health goal adjustments
    health_goal = user_profile.get("health_goal", "general_health")
    if health_goal in HEALTH_GOAL_TARGETS:
        targets.update(HEALTH_GOAL_TARGETS[health_goal])
    
    # ===== Statistics & Achievements (Top Section) =====
    # Get data for the last 7 days for statistics
    days_back = 7
    end_date = today
    start_date = end_date - timedelta(days=days_back)
    recent_meals = db_manager.get_meals_in_range(st.session_state.user_id, start_date, end_date)
    
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
    
    meal_dates = [datetime.fromisoformat(m.get("logged_at", "")) for m in recent_meals]
    streak_info = get_streak_info(meal_dates)
    
    achieve_cols = st.columns(2, gap="small")
    
    # Current Streak Card
    with achieve_cols[0]:
        current_streak = streak_info['current_streak']
        streak_emoji = "🔥" if current_streak > 0 else "⭕"
        st.markdown(f"""
        <div class="streak-box" style="
            background: linear-gradient(135deg, #FF671520 0%, #FF671540 100%);
            border: 1px solid #FF6715;
            border-left: 5px solid #FF6715;
            border-radius: 12px;
            padding: 20px 16px;
            text-align: center;
            min-height: 160px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(255, 103, 21, 0.2);
        ">
            <div style="font-size: 40px; margin-bottom: 10px;">{streak_emoji}</div>
            <div style="font-size: 11px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; font-weight: 700;">Current Streak</div>
            <div style="font-size: 36px; font-weight: 900; color: #FFB84D; margin-bottom: 6px;">{current_streak}</div>
            <div style="font-size: 11px; color: #FF6715; font-weight: 700;">days in a row</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Longest Streak Card
    with achieve_cols[1]:
        longest_streak = streak_info['longest_streak']
        st.markdown(f"""
        <div class="streak-box" style="
            background: linear-gradient(135deg, #FFD43B20 0%, #FFC94D40 100%);
            border: 1px solid #FFD43B;
            border-left: 5px solid #FFD43B;
            border-radius: 12px;
            padding: 20px 16px;
            text-align: center;
            min-height: 160px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(255, 212, 59, 0.2);
        ">
            <div style="font-size: 40px; margin-bottom: 10px;">🏅</div>
            <div style="font-size: 11px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; font-weight: 700;">Longest Streak</div>
            <div style="font-size: 36px; font-weight: 900; color: #FFD43B; margin-bottom: 6px;">{longest_streak}</div>
            <div style="font-size: 11px; color: #FFD43B; font-weight: 700;">personal record</div>
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
    today = date.today()
    daily_nutrition = db_manager.get_daily_nutrition_summary(st.session_state.user_id, today)
    water_intake = db_manager.get_daily_water_intake(st.session_state.user_id, today)
    
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
        current_water = db_manager.get_daily_water_intake(st.session_state.user_id, today)
        water_percentage = min((current_water / water_goal) * 100, 100) if water_goal > 0 else 0
        
        # Determine water status
        if current_water >= water_goal:
            water_status = "🎉 Daily goal achieved!"
            water_status_color = "#51CF66"
            water_bg = "linear-gradient(135deg, #51CF6620 0%, #69DB7C40 100%)"
            water_border = "#51CF66"
        elif current_water >= water_goal * 0.75:
            water_status = "💪 Almost there! Keep going!"
            water_status_color = "#FFD43B"
            water_bg = "linear-gradient(135deg, #FFD43B20 0%, #FCC41940 100%)"
            water_border = "#FFD43B"
        else:
            water_status = "💧 Stay hydrated! Keep drinking"
            water_status_color = "#3B82F6"
            water_bg = "linear-gradient(135deg, #3B82F620 0%, #60A5FA40 100%)"
            water_border = "#3B82F6"
        
        # Water intake card
        st.markdown(f"""
        <div style="
            background: {water_bg};
            border: 2px solid {water_border};
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            margin-bottom: 12px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <span style="color: #e0f2f1; font-weight: 700; font-size: 16px;">💧 Water Intake</span>
                <span style="color: {water_status_color}; font-weight: bold; font-size: 15px;">{current_water}/{water_goal}</span>
            </div>
            <div style="background: #0a0e27; border-radius: 8px; height: 14px; overflow: hidden; margin-bottom: 12px;">
                <div style="background: linear-gradient(90deg, {water_border} 0%, {water_status_color} 100%); height: 100%; width: {water_percentage}%; transition: width 0.3s ease;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <span style="color: {water_status_color}; font-weight: 600; font-size: 14px;">{water_status}</span>
                <span style="color: #a0a0a0; font-size: 13px;">{water_percentage:.0f}%</span>
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
            cal_color = "#51CF66"
        elif cal_percentage >= 80:
            cal_color = "#51CF66"
            cal_status = "✅ On track"
        elif cal_percentage >= 50:
            cal_color = "#FFD43B"
            cal_status = "⚠️ Below target"
        else:
            cal_color = "#FF6B6B"
            cal_status = "📉 Well below"
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {cal_color}20 0%, {cal_color}40 100%);
            border: 2px solid {cal_color};
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            margin-bottom: 12px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                <span style="color: #e0f2f1; font-weight: 700; font-size: 16px;">🔥 Daily Calories</span>
                <span style="color: {cal_color}; font-weight: bold; font-size: 15px;">{cal_value}/{cal_target}</span>
            </div>
            <div style="background: #0a0e27; border-radius: 8px; height: 14px; overflow: hidden; margin-bottom: 12px;">
                <div style="background: linear-gradient(90deg, {cal_color} 0%, {cal_color} 100%); height: 100%; width: {min(cal_percentage, 100)}%; transition: width 0.3s ease;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                <span style="color: {cal_color}; font-weight: 600; font-size: 14px;">{cal_status}</span>
                <span style="color: #a0a0a0; font-size: 13px;">{cal_percentage:.0f}%</span>
            </div>
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
            "unit": "g"
        },
        {
            "icon": "🥗",
            "label": "Carbs",
            "value": f"{daily_nutrition['carbs']:.1f}",
            "target": targets["carbs"],
            "percentage": calculate_nutrition_percentage(daily_nutrition["carbs"], targets["carbs"]),
            "unit": "g"
        },
        {
            "icon": "🧈",
            "label": "Fat",
            "value": f"{daily_nutrition['fat']:.1f}",
            "target": targets["fat"],
            "percentage": calculate_nutrition_percentage(daily_nutrition["fat"], targets["fat"]),
            "unit": "g"
        },
        {
            "icon": "🧂",
            "label": "Sodium",
            "value": f"{daily_nutrition['sodium']:.0f}",
            "target": targets["sodium"],
            "percentage": calculate_nutrition_percentage(daily_nutrition["sodium"], targets["sodium"]),
            "unit": "mg"
        },
        {
            "icon": "🍬",
            "label": "Sugar",
            "value": f"{daily_nutrition['sugar']:.1f}",
            "target": targets["sugar"],
            "percentage": calculate_nutrition_percentage(daily_nutrition["sugar"], targets["sugar"]),
            "unit": "g"
        }
    ]
    
    # Create 3-column grid for compact display
    cols = st.columns(3, gap="small")  # Compact spacing between cards
    
    for idx, card in enumerate(nutrition_cards):
        with cols[idx % 3]:
            percentage = card["percentage"]
            
            # Determine color and status
            if card["label"] in ["Sodium", "Sugar"]:
                # Harmful nutrients - red for exceeding
                if percentage > 100:
                    color = "#FF6B6B"
                    gradient_color = "#FF8A8A"
                    status_icon = "⚠️"
                    status_text = f"Over by {percentage-100:.0f}%"
                elif percentage >= 80:
                    color = "#FFD43B"
                    gradient_color = "#FCC41A"
                    status_icon = "⚠️"
                    status_text = f"{percentage:.0f}%"
                else:
                    color = "#51CF66"
                    gradient_color = "#80C342"
                    status_icon = "✅"
                    status_text = f"{percentage:.0f}%"
            else:
                # Good nutrients - green for on target
                if percentage > 100:
                    color = "#51CF66"  # Green for over (protein ok to exceed)
                    gradient_color = "#80C342"
                    status_icon = "⚡"
                    status_text = f"+{percentage-100:.0f}%"
                elif percentage >= 80:
                    color = "#51CF66"
                    gradient_color = "#80C342"
                    status_icon = "✅"
                    status_text = f"{percentage:.0f}%"
                else:
                    color = "#FFD43B"
                    gradient_color = "#FCC41A"
                    status_icon = "⚠️"
                    status_text = f"{percentage:.0f}%"
            
            st.markdown(f"""
            <div class="nutrition-info" style="
                background: linear-gradient(135deg, {color}20 0%, {gradient_color}40 100%);
                border: 1px solid {color};
                border-left: 5px solid {color};
                border-radius: 14px;
                padding: 16px;
                text-align: center;
                min-height: 180px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                box-shadow: 0 4px 15px rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.15);
                transition: all 0.3s ease;
            ">
                <div>
                    <div style="font-size: 32px; margin-bottom: 8px;">{card['icon']}</div>
                    <div style="font-size: 10px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; font-weight: 700;">{card['label']}</div>
                </div>
                <div>
                    <div style="font-size: 28px; font-weight: 900; color: #FFB84D; margin-bottom: 10px;">{card['value']}{card['unit']}</div>
                    <div style="background: #0a0e27; border-radius: 4px; height: 5px; margin-bottom: 8px;"><div style="background: linear-gradient(90deg, {color} 0%, {gradient_color} 100%); height: 100%; width: {min(percentage, 100)}%; border-radius: 4px;"></div></div>
                    <div style="font-size: 10px; color: #a0a0a0; margin-bottom: 6px;">of {card['target']}{card['unit']}</div>
                </div>
                <div style="font-size: 10px; color: {color}; font-weight: 700;">{status_icon} {status_text}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # ===== MACRO BREAKDOWN & INSIGHTS =====
    st.markdown("")
    st.markdown("## 📊 Nutrition Breakdown & Patterns")
    
    # Create a responsive grid layout
    breakdown_col1, breakdown_col2 = st.columns([1.2, 1], gap="medium")
    
    # MACRO BALANCE - Left side
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
    
    # EATING PATTERNS - Right side (replaced "Most Frequent Foods")
    with breakdown_col2:
        st.markdown("""
        <div class="dashboard-info-box" style="
            background: linear-gradient(135deg, rgba(255, 107, 22, 0.1) 0%, rgba(16, 161, 157, 0.05) 100%);
            border: 1px solid rgba(255, 107, 22, 0.3);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 16px;
        ">
            <h3 style="color: #e0f2f1; margin-top: 0; font-size: 18px;">🍽️ Today's Eating Patterns</h3>
        """, unsafe_allow_html=True)
        
        # Calculate meal type distribution
        time_pattern = {}
        for meal in meals[:30]:
            logged_at = meal.get('logged_at', '')
            if logged_at:
                hour = int(logged_at.split('T')[1].split(':')[0])
                period = "Breakfast" if 6 <= hour < 10 else \
                        "Lunch" if 10 <= hour < 15 else \
                        "Dinner" if 15 <= hour < 21 else \
                        "Snacks"
                time_pattern[period] = time_pattern.get(period, 0) + 1
        
        # Ensure all meal types are shown, even with 0 count
        period_order = ["Breakfast", "Lunch", "Dinner", "Snacks"]
        pattern_cols = st.columns(4, gap="medium")
        
        for idx, period in enumerate(period_order):
            with pattern_cols[idx]:
                emoji = {"Breakfast": "🌅", "Lunch": "🍴", "Dinner": "🌙", "Snacks": "🍿"}.get(period, "📌")
                count = time_pattern.get(period, 0)
                
                st.markdown(f"""
                <div class="pattern-card" style="text-align: center; padding: 14px; background: rgba(16, 161, 157, 0.15); border-radius: 8px;">
                    <div style="font-size: 28px; margin-bottom: 10px;">{emoji}</div>
                    <div style="font-size: 22px; font-weight: bold; color: #e0f2f1; margin-bottom: 6px;">{count}</div>
                    <div style="font-size: 13px; color: #a0a0a0; font-weight: 600;">{period}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
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
                    st.markdown(nutrition_analyzer.get_nutrition_facts_html(nutrition), unsafe_allow_html=True)
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
        background: linear-gradient(135deg, #10A19D 0%, #52C4B8 100%);
        padding: 10px 20px;
        border-radius: 12px;
        margin-bottom: 16px;
    ">
        <h1 style="color: white; margin: 0; font-size: 1.5em; line-height: 1.2;">📸 Log Your Meal</h1>
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
                meal = meal_options[selected_quick_meal]
                meal_data = {
                    "user_id": st.session_state.user_id,
                    "meal_name": meal.get('meal_name', 'Unknown'),
                    "description": meal.get('description', ''),
                    "meal_type": meal.get('meal_type'),
                    "nutrition": meal.get('nutrition', {}),
                    "healthiness_score": meal.get('healthiness_score', 0),
                    "health_notes": meal.get('health_notes', ''),
                    "logged_at": datetime.now().isoformat(),
                }
                
                if db_manager.log_meal(meal_data):
                    # Award XP for logging meal
                    db_manager.add_xp(st.session_state.user_id, GamificationManager.XP_REWARDS['meal_logged'])
                    st.toast("Meal added! +25 XP", icon="✅")
                    st.rerun()
                else:
                    st.toast("Failed to add meal", icon="❌")
        
        st.divider()
    
    st.markdown("""
    ### Choose how you'd like to log your meal:
    1. **Text Description** - Describe your meal in words
    2. **Photo** - Take a photo of your meal
    3. **Batch Log** - Log multiple meals for past days
    """)
    
    tab1, tab2, tab3 = st.tabs(["📝 Text", "📸 Photo", "📅 Batch Log"])
    
    with tab1:
        st.markdown("## Describe Your Meal")
        
        meal_description = st.text_area(
            "What did you eat? (Be as detailed as you'd like)",
            placeholder="E.g., Chicken fried rice with broccoli, 2 glasses of milk, an apple...",
            height=150
        )
        
        meal_type = st.selectbox(
            "Meal Type",
            options=list(MEAL_TYPES.keys()),
            format_func=lambda x: MEAL_TYPES.get(x, x)
        )
        
        if st.button("Analyze Meal", use_container_width=True):
            if meal_description:
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
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(nutrition_analyzer.get_nutrition_facts_html(analysis['nutrition']), unsafe_allow_html=True)
            
            with col2:
                healthiness = analysis.get('healthiness_score', 0)
                st.metric("Healthiness Score", f"{healthiness}/100")
            
            st.info(f"**Health Notes:** {analysis.get('health_notes', 'N/A')}")
            
            # Date selector - ask RIGHT BEFORE saving
            st.markdown("### 📅 When did you eat this?")
            meal_date = st.date_input(
                "Select date",
                value=date.today(),
                max_value=date.today(),
                help="You can log meals from past dates",
                key="text_meal_date"
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
                    "logged_at": datetime.combine(meal_date, time(12, 0, 0)).isoformat(),
                }
                
                if db_manager.log_meal(meal_data):
                    # Award XP for logging meal
                    db_manager.add_xp(st.session_state.user_id, GamificationManager.XP_REWARDS['meal_logged'])
                    # Clear the analysis from session state
                    del st.session_state.meal_analysis
                    del st.session_state.meal_type
                    st.toast("Meal saved! +25 XP", icon="✅")
                    st.rerun()
                else:
                    error_state(
                        "Failed to Save Meal",
                        "We couldn't save your meal to the database. This might be a temporary connection issue.",
                        suggestion="Please check your internet connection and try again.",
                        icon="💾"
                    )
    
    with tab2:
        st.markdown("## Upload Food Photo")
        
        uploaded_file = st.file_uploader(
            "Choose a food photo",
            type=["jpg", "jpeg", "png"],
            help="Upload a clear photo of your meal"
        )
        
        meal_type = st.selectbox(
            "Meal Type",
            options=list(MEAL_TYPES.keys()),
            format_func=lambda x: MEAL_TYPES.get(x, x),
            key="photo_meal_type"
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Your meal", use_column_width=True)
            
            if st.button("Analyze Photo", use_container_width=True):
                with st.spinner("🤖 Analyzing your photo..."):
                    image_data = uploaded_file.getvalue()
                    analysis = nutrition_analyzer.analyze_food_image(image_data)
                    
                    if analysis:
                        # Store analysis in session state (meal_type is already in session via selectbox key)
                        st.session_state.photo_analysis = analysis
                        success_state("Photo Analyzed Successfully", "Your meal has been analyzed and is ready to save!")
                    else:
                        error_state(
                            "Analysis Failed",
                            "We couldn't analyze your photo. This might happen if the image is unclear or doesn't show food.",
                            suggestion="Try uploading a clearer photo with better lighting and focus on the food.",
                            icon="🔍"
                        )
        
        # Display analysis if it exists in session state
        if "photo_analysis" in st.session_state:
            analysis = st.session_state.photo_analysis
            # meal_type is already managed by the selectbox widget via key="photo_meal_type"
            
            # Display detected foods
            st.markdown("### Detected Foods")
            for food in analysis.get('detected_foods', []):
                st.write(f"- {food['name']} ({food['quantity']})")
            
            # Display nutrition
            st.markdown(nutrition_analyzer.get_nutrition_facts_html(analysis['total_nutrition']), unsafe_allow_html=True)
            
            st.info(f"**Confidence:** {analysis.get('confidence', 0)}%")
            st.info(f"**Notes:** {analysis.get('notes', 'N/A')}")
            
            # Date selector - ask RIGHT BEFORE saving
            st.markdown("### 📅 When did you eat this?")
            meal_date = st.date_input(
                "Select date",
                value=date.today(),
                max_value=date.today(),
                help="You can log meals from past dates",
                key="photo_meal_date"
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
                    "logged_at": datetime.combine(meal_date, time(12, 0, 0)).isoformat(),
                }
                
                if db_manager.log_meal(meal_data):
                    # Award XP for logging meal
                    db_manager.add_xp(st.session_state.user_id, GamificationManager.XP_REWARDS['meal_logged'])
                    # Clear the analysis from session state
                    del st.session_state.photo_analysis
                    # Set flag to show success message on next render
                    st.session_state._photo_meal_saved = True
                    st.toast("Meal saved! +25 XP", icon="✅")
                    st.rerun()
                else:
                    error_state(
                        "Failed to Save Meal",
                        "We couldn't save your meal to the database. This might be a temporary connection issue.",
                        suggestion="Please check your internet connection and try again.",
                        icon="💾"
                    )
    
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
            
            # Create columns for meal types
            meal_col1, meal_col2, meal_col3 = st.columns(3)
            
            with meal_col1:
                breakfast = st.text_input(
                    f"Breakfast",
                    placeholder="e.g., Oatmeal with berries",
                    key=f"batch_breakfast_{date_str}"
                )
            
            with meal_col2:
                lunch = st.text_input(
                    f"Lunch",
                    placeholder="e.g., Grilled chicken with vegetables",
                    key=f"batch_lunch_{date_str}"
                )
            
            with meal_col3:
                dinner = st.text_input(
                    f"Dinner",
                    placeholder="e.g., Salmon with rice",
                    key=f"batch_dinner_{date_str}"
                )
            
            day_meals[date_str] = {
                "breakfast": breakfast,
                "lunch": lunch,
                "dinner": dinner
            }
            
            current_date += timedelta(days=1)
        
        st.divider()
        
        if st.button("📥 Analyze & Save All Meals", key="batch_save_btn", use_container_width=True):
            total_saved = 0
            total_failed = 0
            
            with st.spinner("🤖 Analyzing and saving meals..."):
                for date_str, meals_dict in day_meals.items():
                    for meal_type, description in meals_dict.items():
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
                                        time(12, 0, 0)
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
        background: linear-gradient(135deg, #845EF7 0%, #BE80FF 100%);
        padding: 15px 25px;
        border-radius: 15px;
        margin-bottom: 20px;
    ">
        <h1 style="color: white; margin: 0; font-size: 1.6em; line-height: 1.2;">📈 Analytics & Insights</h1>
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
        if st.button("Last 7 days", use_container_width=True, key="btn_7days"):
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
    age_group = user_profile.get("age_group", "26-35")
    targets = AGE_GROUP_TARGETS.get(age_group, AGE_GROUP_TARGETS["26-35"])
    
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
    
    # ===== Meal Type Distribution =====
    st.markdown("## 🍽️ Meal Type Distribution")
    
    meal_types_count = {}
    for meal in meals:
        meal_type = meal.get("meal_type", "unknown")
        meal_types_count[meal_type] = meal_types_count.get(meal_type, 0) + 1
    
    if meal_types_count:
        fig_pie = px.pie(
            values=list(meal_types_count.values()),
            names=[MEAL_TYPES.get(k, k) for k in meal_types_count.keys()],
            title="Meals by Type"
        )
        st.plotly_chart(fig_pie, use_container_width=True)


def show_meal_quality(meals):
    """Display best and worst meals quality section"""
    st.markdown("## 🏆 Your Meal Quality")
    
    # Sort meals by healthiness score
    sorted_meals = sorted(meals, key=lambda x: x.get('healthiness_score', 0), reverse=True)
    
    if sorted_meals:
        best_worst_col1, best_worst_col2 = st.columns(2)
        
        with best_worst_col1:
            st.markdown("### ✅ Healthiest Meals")
            for idx, meal in enumerate(sorted_meals[:3], 1):
                score = meal.get('healthiness_score', 0)
                st.write(f"{idx}. **{meal.get('meal_name')}** - Score: {score}/100")
                st.caption(meal.get('description', 'N/A')[:100])
        
        with best_worst_col2:
            st.markdown("### ⚠️ Meals to Improve")
            for idx, meal in enumerate(reversed(sorted_meals[-3:]), 1):
                score = meal.get('healthiness_score', 0)
                st.write(f"{idx}. **{meal.get('meal_name')}** - Score: {score}/100")
                st.caption(meal.get('description', 'N/A')[:100])


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
                            st.markdown(nutrition_analyzer.get_nutrition_facts_html(rec.get('estimated_nutrition', {})), unsafe_allow_html=True)
                        
                        with col2:
                            st.info(f"**Why:** {rec.get('why_recommended', '')}")
                        
                        if rec.get('health_benefits'):
                            st.success(f"**Benefits:** {', '.join(rec.get('health_benefits', []))}")


def show_weekly_meal_plan(user_profile):
    """Display weekly meal plan section"""
    st.markdown("## 📅 Weekly Meal Plan")
    
    if st.button("Generate 7-Day Meal Plan", use_container_width=True):
        with st.spinner("🤖 Creating your personalized meal plan..."):
            meal_plan = recommender.get_weekly_meal_plan(
                user_profile,
                AGE_GROUP_TARGETS.get(user_profile.get("age_group", "26-35"), AGE_GROUP_TARGETS["26-35"]),
                user_profile.get("dietary_preferences", [])
            )
            
            if meal_plan:
                for day, meals_list in meal_plan.items():
                    with st.expander(f"📅 {day}"):
                        for meal in meals_list:
                            st.write(f"**{meal.get('meal_type').title()}:** {meal.get('meal_name')}")
                            st.caption(meal.get('description', ''))


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
        background: linear-gradient(135deg, #51CF66 0%, #80C342 100%);
        padding: 15px 25px;
        border-radius: 15px;
        margin-bottom: 20px;
    ">
        <h1 style="color: white; margin: 0; font-size: 1.6em; line-height: 1.2;">💡 Health Insights & Recommendations</h1>
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
    age_group = user_profile.get("age_group", "26-35")
    targets = AGE_GROUP_TARGETS.get(age_group, AGE_GROUP_TARGETS["26-35"])
    
    # Today's summary
    today_nutrition = db_manager.get_daily_nutrition_summary(st.session_state.user_id, date.today())
    
    # ===== BEST & WORST MEALS =====
    st.divider()
    show_meal_quality(meals)
    
    # ===== Personalized Recommendations =====
    st.divider()
    show_meal_recommendations(user_profile, meals, today_nutrition, targets)
    
    # ===== Weekly Meal Plan =====
    st.divider()
    show_weekly_meal_plan(user_profile)
    
    # ===== Health Insights =====
    st.divider()
    show_health_insights(meals, user_profile, st.session_state)
    
    # ===== NUTRITION COMPARISON (TODAY VS WEEKLY AVG) =====
    st.divider()
    st.markdown("## 📊 Today vs Weekly Average")
    
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    weekly_meals = db_manager.get_meals_in_range(st.session_state.user_id, start_date, end_date)
    
    if weekly_meals:
        weekly_nutrition = {
            "calories": sum(m.get('nutrition', {}).get('calories', 0) for m in weekly_meals) / 7,
            "protein": sum(m.get('nutrition', {}).get('protein', 0) for m in weekly_meals) / 7,
            "carbs": sum(m.get('nutrition', {}).get('carbs', 0) for m in weekly_meals) / 7,
            "fat": sum(m.get('nutrition', {}).get('fat', 0) for m in weekly_meals) / 7,
        }
        
        comp_col1, comp_col2, comp_col3, comp_col4 = st.columns(4)
        
        nutrients = [("Calories", "calories", "🔥"), ("Protein", "protein", "💪"), ("Carbs", "carbs", "🌾"), ("Fat", "fat", "🧈")]
        
        for idx, (col, (label, key, emoji)) in enumerate(zip([comp_col1, comp_col2, comp_col3, comp_col4], nutrients)):
            with col:
                today_val = today_nutrition.get(key, 0)
                avg_val = weekly_nutrition.get(key, 0)
                
                if today_val > avg_val:
                    trend = "↑ Above avg"
                    trend_color = "#FFD43B"
                    delta = today_val - avg_val
                elif today_val < avg_val:
                    trend = "↓ Below avg"
                    trend_color = "#FF6B6B"
                    delta = avg_val - today_val
                else:
                    trend = "= On track"
                    trend_color = "#51CF66"
                    delta = 0
                
                unit = "g" if key != "calories" else ""
                st.metric(f"{emoji} {label}", f"{today_val:.1f}{unit}", f"{delta:.1f}{unit} {trend}")
    
    # ===== MEAL TYPE DISTRIBUTION =====
    st.divider()
    st.markdown("## 🍽️ Meal Type Distribution This Week")
    
    if weekly_meals:
        meal_type_counts = {}
        for meal in weekly_meals:
            meal_type = meal.get("meal_type", "unknown")
            meal_type_counts[meal_type] = meal_type_counts.get(meal_type, 0) + 1
        
        if meal_type_counts:
            dist_col1, dist_col2 = st.columns(2)
            
            with dist_col1:
                meal_type_df = pd.DataFrame(list(meal_type_counts.items()), columns=["Type", "Count"])
                fig_dist = px.bar(meal_type_df, x="Type", y="Count", title="Meals by Type", color="Count")
                st.plotly_chart(fig_dist, use_container_width=True)
            
            with dist_col2:
                st.markdown("### Your eating patterns:")
                total_week_meals = sum(meal_type_counts.values())
                for meal_type, count in sorted(meal_type_counts.items(), key=lambda x: x[1], reverse=True):
                    pct = (count / total_week_meals) * 100
                    st.write(f"**{meal_type.title()}:** {count} meals ({pct:.0f}%)")
    
    # ===== NUTRITION TARGETS SUMMARY =====
    st.divider()
    st.markdown("## 🎯 Your Nutrition Targets")
    
    if user_profile:
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
    
    # ===== Export Data =====
    st.divider()
    st.markdown("## 📥 Export Your Data")
    
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        if st.button("📄 Export as CSV", use_container_width=True):
            csv_data = generate_csv_export(meals)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"eatwise_meals_{date.today()}.csv",
                mime="text/csv",
                key="csv_download"
            )
    
    with export_col2:
        if st.button("📋 Export Report", use_container_width=True):
            report = generate_nutrition_report(meals, today_nutrition, targets, "recent")
            st.download_button(
                label="📥 Download Report",
                data=report,
                file_name=f"eatwise_report_{date.today()}.txt",
                mime="text/plain",
                key="report_download"
            )
    
    with export_col3:
        if st.button("📊 Share Weekly Summary", use_container_width=True):
            end_date = date.today()
            start_date = end_date - timedelta(days=7)
            weekly_meals = db_manager.get_meals_in_range(st.session_state.user_id, start_date, end_date)
            
            if weekly_meals:
                weekly_nutrition = {
                    "calories": sum(m.get('nutrition', {}).get('calories', 0) for m in weekly_meals) / 7,
                    "protein": sum(m.get('nutrition', {}).get('protein', 0) for m in weekly_meals) / 7,
                    "carbs": sum(m.get('nutrition', {}).get('carbs', 0) for m in weekly_meals) / 7,
                    "fat": sum(m.get('nutrition', {}).get('fat', 0) for m in weekly_meals) / 7,
                }
                
                summary = generate_nutrition_report(weekly_meals, weekly_nutrition, targets, "weekly")
                with st.expander("📊 Weekly Summary Preview", expanded=True):
                    st.text_area("Copy your weekly summary:", value=summary, height=250, disabled=True, key="weekly_summary_share")
                
                st.download_button(
                    label="📥 Download Weekly Summary",
                    data=summary,
                    file_name=f"eatwise_weekly_summary_{date.today()}.txt",
                    mime="text/plain",
                    key="summary_download"
                )


def meal_history_page():
    """View and manage all logged meals"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%);
        padding: 15px 25px;
        border-radius: 15px;
        margin-bottom: 20px;
    ">
        <h1 style="color: white; margin: 0; font-size: 1.6em; line-height: 1.2;">📋 Meal History</h1>
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
                st.caption(f"📅 {meal.get('logged_at', 'N/A')}")
            
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
                            "logged_at": datetime.combine(dup_date, time(12, 0, 0)).isoformat(),
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
                st.markdown(nutrition_analyzer.get_nutrition_facts_html(nutrition), unsafe_allow_html=True)
            
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
                            
                            if db_manager.update_meal(meal['id'], updated_meal):
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
                    st.rerun()
            
            with pag_col2:
                if st.button(f"Next ({current_page}/{total_pages}) ➡️", key="next_bottom", disabled=(st.session_state.pagination_page >= total_pages - 1), use_container_width=True):
                    st.session_state.pagination_page += 1
                    st.rerun()


def profile_page():
    """User profile and health settings page"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #FF6B16 0%, #FF8A4D 100%);
        padding: 15px 25px;
        border-radius: 15px;
        margin-bottom: 20px;
    ">
        <h1 style="color: white; margin: 0; font-size: 1.6em; line-height: 1.2;">👤 My Profile</h1>
    </div>
    """, unsafe_allow_html=True)
    
    user_email = st.session_state.user_email
    
    # Create tabs for Profile and Security
    tab1, tab2 = st.tabs(["Profile", "Security"])
    
    with tab1:
        # Fetch profile from database (fresh for this page, not using cache)
        # because users expect to see current profile data when they visit settings
        user_profile = db_manager.get_health_profile(st.session_state.user_id)
        user_profile = normalize_profile(user_profile) if user_profile else None
        
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
                        options=["Male", "Female", "Other", "Prefer not to say"],
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
                    if current_age_group not in AGE_GROUP_TARGETS.keys():
                        # Try to find a matching age group key
                        matching_key = None
                        for key in AGE_GROUP_TARGETS.keys():
                            if key.split(" (")[0] == current_age_group or key in current_age_group:  # Match by age range part
                                matching_key = key
                                break
                        current_age_group = matching_key or "26-35"  # Default fallback
                    
                    age_group_index = list(AGE_GROUP_TARGETS.keys()).index(current_age_group)
                    age_group = st.selectbox(
                        "Age Group",
                        options=list(AGE_GROUP_TARGETS.keys()),
                        index=age_group_index
                    )
                
                # Row 2: Gender and Timezone
                col3, col4 = st.columns(2)
                with col3:
                    gender_options = ["Male", "Female", "Other", "Prefer not to say"]
                    gender_value = user_profile.get("gender", "Prefer not to say")
                    gender_index = gender_options.index(gender_value) if gender_value in gender_options else 3
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
                    for key, value in timezone_dict.items():
                        if value == timezone_value:
                            timezone_index = timezone_options.index(key)
                            break
                    timezone = st.selectbox(
                        "Timezone",
                        options=timezone_options,
                        index=timezone_index,
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
                        value=int(user_profile.get("height_cm", 170)) if user_profile.get("height_cm") else 170,
                        step=1,
                        help="Your height in centimeters (optional)"
                    )
                    height_cm = height_cm if height_cm else None
                
                with col4b:
                    weight_kg = st.number_input(
                        "Weight (kg) - Optional",
                        min_value=30.0,
                        max_value=200.0,
                        value=float(user_profile.get("weight_kg", 70.0)) if user_profile.get("weight_kg") else 70.0,
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
                    goal_index = goal_keys.index(current_health_goal) if current_health_goal in goal_keys else 0
                    
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
                    water_goal = st.number_input(
                        "Daily Water Goal (glasses)",
                        min_value=1,
                        max_value=20,
                        value=user_profile.get("water_goal_glasses", 8),
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
        age_group = user_profile.get("age_group", "26-35")
        targets = AGE_GROUP_TARGETS.get(age_group, AGE_GROUP_TARGETS["26-35"])
        
        # Apply health condition adjustments
        health_conditions = user_profile.get("health_conditions", [])
        for condition in health_conditions:
            if condition in HEALTH_CONDITION_TARGETS:
                targets.update(HEALTH_CONDITION_TARGETS[condition])
        
        # Apply health goal adjustments
        health_goal = user_profile.get("health_goal", "general_health")
        if health_goal in HEALTH_GOAL_TARGETS:
            targets.update(HEALTH_GOAL_TARGETS[health_goal])
        
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
                    st.rerun()
        
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
        background: linear-gradient(135deg, #FF6B6B 0%, #FFA94D 100%);
        padding: 15px 25px;
        border-radius: 15px;
        margin-bottom: 20px;
    ">
        <h1 style="color: white; margin: 0; font-size: 1.6em; line-height: 1.2;">🍽️ Restaurant Menu Analyzer</h1>
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
                    age_group = user_profile.get("age_group", "26-35")
                    targets = AGE_GROUP_TARGETS.get(age_group, AGE_GROUP_TARGETS["26-35"])
                    
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
        st.caption("Take a photo of the menu (JPG, PNG)")
        
        uploaded_file = st.file_uploader(
            "Menu Photo",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
            key="menu_photo_upload"
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
                                age_group = user_profile.get("age_group", "26-35")
                                targets = AGE_GROUP_TARGETS.get(age_group, AGE_GROUP_TARGETS["26-35"])
                                
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
        background: linear-gradient(135deg, #10A19D 0%, #52C4B8 100%);
        padding: 15px 25px;
        border-radius: 15px;
        margin-bottom: 20px;
    ">
        <h1 style="color: white; margin: 0; font-size: 1.6em; line-height: 1.2;">❓ Help & About</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["About", "Features", "How to Use", "FAQ"])
    
    with tab1:
        st.markdown("## About EatWise")
        st.markdown("""
        **EatWise** is an AI-powered nutrition tracking and health insights application designed to help you:
        
        - 🍎 Log meals using text descriptions or food photos
        - 📊 Track nutrition intake and analyze eating patterns
        - 💡 Receive personalized meal recommendations
        - 📈 Monitor health progress with detailed analytics
        - 🎯 Achieve your health and fitness goals
        
        ### Technology Stack
        - **Frontend**: Streamlit (Python)
        - **Backend**: Supabase (PostgreSQL)
        - **AI/ML**: Azure OpenAI (GPT-4)
        - **Deployment**: Streamlit Cloud
        
        ### Version
        **v1.0.0** - Initial Release
        """)
    
    with tab2:
        st.markdown("## Key Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📝 Meal Logging")
            st.markdown("""
            - Text-based meal descriptions
            - Food photo recognition
            - Nutritional analysis
            - Multiple meal types (breakfast, lunch, dinner, snack, beverage)
            """)
            
            st.markdown("### 📊 Analytics Dashboard")
            st.markdown("""
            - Daily nutrition trends
            - Macronutrient distribution
            - Meal type breakdown
            - Calorie tracking progress
            """)
            
            st.markdown("### 💡 Smart Insights")
            st.markdown("""
            - AI-powered health analysis
            - Personalized recommendations
            - Strength identification
            - Areas for improvement
            """)
        
        with col2:
            st.markdown("### 📋 Meal History")
            st.markdown("""
            - Browse all logged meals
            - Edit meal details
            - Delete meals
            - Date range filtering
            """)
            
            st.markdown("### 🎯 AI Nutrition Coaching")
            st.markdown("""
            - Chat with AI coach about nutrition
            - Ask personalized nutrition questions
            - Receive guidance based on your profile
            - Multi-turn conversations with context awareness
            - Clear chat to start fresh anytime
            """)
            
            st.markdown("### 🍽️ Restaurant Menu Analyzer")
            st.markdown("""
            - Paste restaurant menus for analysis
            - Upload menu photos with OCR
            - Get personalized recommendations
            - See items to avoid
            - Modification suggestions for healthier ordering
            """)
    
    with tab3:
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
    
    with tab4:
        st.markdown("## Frequently Asked Questions")
        
        with st.expander("❓ How accurate is the nutrition analysis?"):
            st.markdown("""
            Our **Hybrid Nutrition System** ensures maximum accuracy:
            
            **How It Works:**
            1. **AI Ingredient Detection**: GPT-4 analyzes your text or photo to identify specific foods
            2. **Database Lookup**: For 100+ common foods, we use USDA-validated nutrition data
            3. **Intelligent Estimation**: For less common ingredients, AI applies smart heuristics based on food category
            4. **Coverage Reporting**: You see which foods came from the database vs. estimated
            
            **Database Coverage:**
            - 100+ common foods with exact USDA values
            - All vegetables, fruits, proteins, grains, dairy
            - Restaurant chains and prepared foods
            
            **Accuracy Level:**
            - Database foods: 99%+ accurate (USDA-validated)
            - Estimated foods: 85-95% accurate (AI-based category estimation)
            - For medical or precise nutritional needs, consult a nutritionist
            
            **What This Means:**
            - Common meals (chicken + rice): Near-exact values
            - Specialty dishes: Realistic estimates within 5-10%
            - You always know which values are from database vs. estimated
            """)
        
        with st.expander("❓ What foods are in your nutrition database?"):
            st.markdown("""
            Our database includes 100+ common foods with precise USDA nutrition values:
            
            **Proteins:**
            - Chicken breast, ground beef, salmon, tuna, tofu, eggs, beans
            
            **Vegetables:**
            - Broccoli, spinach, carrots, tomatoes, lettuce, bell peppers, zucchini, mushrooms, and more
            
            **Fruits:**
            - Apples, bananas, oranges, berries, avocado, grapes, peaches
            
            **Grains & Carbs:**
            - Brown rice, white rice, pasta, bread, oats, quinoa, sweet potatoes
            
            **Dairy:**
            - Milk, yogurt, cheese (cheddar, mozzarella), cottage cheese
            
            **Prepared Foods:**
            - Common restaurant items, fast food chains, packaged meals
            
            **Missing a Food?**
            - If your food isn't in the database, AI estimates based on similar foods
            - The coverage report shows which values are database-backed vs. estimated
            - Estimates are typically 85-95% accurate for similar food categories
            """)
        
            st.markdown("""
            Yes! Go to **Meal History** and:
            1. Find the meal you want to edit
            2. Click the "Edit" button
            3. Modify any details or nutrition values
            4. Click "Save Changes"
            """)
        
        with st.expander("❓ What if a meal was logged incorrectly?"):
            st.markdown("""
            You can either:
            1. **Edit it**: Go to **Meal History**, click Edit, and update the information
            2. **Delete it**: Click Delete to remove it completely
            
            Then log it again with the correct information.
            """)
        
        with st.expander("❓ How do recommendations work?"):
            st.markdown("""
            Our AI analyzes:
            - Your recent meal history
            - Your health profile and goals
            - Your current nutrition levels
            - Your dietary preferences
            
            Then generates personalized meal suggestions to help you meet your goals.
            """)
        
        with st.expander("❓ Can I access the app on mobile?"):
            st.markdown("""
            Yes! EatWise is fully responsive and works on:
            - Smartphones (iOS & Android)
            - Tablets
            - Desktops
            
            Just use your browser to access https://eatwise-ai.streamlit.app/
            """)
        
        with st.expander("❓ How does the restaurant menu analyzer work?"):
            st.markdown("""
            The **Eating Out** feature helps you make healthy choices when dining:
            
            **Text Menu Option:**
            1. Paste the restaurant menu
            2. AI analyzes it against your health profile and goals
            3. Get personalized recommendations
            
            **Photo Menu Option:**
            1. Upload a menu photo
            2. AI reads the text automatically (OCR)
            3. Same analysis and recommendations as text
            
            The analyzer considers:
            - Your health conditions
            - Your dietary preferences
            - Your nutrition goals
            - Your remaining daily nutrition budget
            """)
        
        with st.expander("❓ What do the nutrition cards show?"):
            st.markdown("""
            Each recommended meal option displays:
            - **Calories**: Total energy content
            - **Protein**: Important for muscle and satiety
            - **Carbs**: Carbohydrates for energy
            - **Sodium**: Salt content (important if you monitor sodium)
            
            All nutrition estimates are realistic approximations based on:
            - Typical portions
            - Cooking methods mentioned
            - Standard food composition data
            """)
        
        with st.expander("❓ Can I trust the restaurant recommendations?"):
            st.markdown("""
            Our AI provides intelligent recommendations, but remember:
            
            **Accuracy factors:**
            - AI estimates nutrition from descriptions
            - Actual values may vary by restaurant
            - Portion sizes can differ
            
            **Best practices:**
            - Use recommendations as guidance, not exact values
            - When unsure, ask the restaurant for nutrition info
            - Check modification tips (like "sauce on the side")
            - Trust your body and adjust as needed
            """)
        
        with st.expander("❓ How is my data stored?"):
            st.markdown("""
            Your data is securely stored in **Supabase** (PostgreSQL database):
            - Encrypted in transit and at rest
            - Regular backups
            - GDPR compliant
            - Only your meals and profile are stored (no photos)
            """)
        
        with st.expander("❓ Is there a way to export my data?"):
            st.markdown("""
            Currently, you can view all your meals in the **Meal History** section.
            Export functionality is coming in future updates!
            """)
        
        with st.expander("❓ What can I ask the AI Coaching feature?"):
            st.markdown("""
            You can ask your AI nutrition coach many things:
            - "What should I eat for dinner?" → Gets personalized meal suggestions
            - "Is pasta healthy?" → Gets advice considering your health conditions
            - "How can I improve my diet?" → Gets strategies based on your profile
            - "What nutrients am I missing?" → Analysis of your recent meals
            - "How much protein should I eat?" → Recommendations based on your age and goals
            
            The coach provides personalized guidance considering your health conditions, 
            age, dietary preferences, and nutrition goals.
            """)
        
        with st.expander("❓ How often should I use the Coaching feature?"):
            st.markdown("""
            - **Anytime**: Ask your coach whenever you need nutrition guidance
            - **After meals**: Get feedback on what you just logged
            - **When deciding**: Get suggestions when choosing what to eat
            - **For tips**: Ask for personalized nutrition advice
            
            The more you interact with your coach, the better it understands your goals!
            """)
    
    st.divider()
    st.markdown("""
    ### 📧 Need More Help?
    Have questions or suggestions? We'd love to hear from you!
    - **GitHub**: https://github.com/scmlewis/eatwise_ai
    - **Report Issues**: Create an issue on GitHub
    
    ---
    **Last Updated**: November 21, 2025 (v1.1.0 - Added AI Nutrition Coaching)
    """)


# ==================== MAIN APP ====================

def main():
    """Main app logic"""
    
    # Add anchor for back-to-top functionality
    st.markdown('<a id="app-top"></a>', unsafe_allow_html=True)
    
    # Add responsive sidebar CSS
    st.markdown("""
    <style>
        /* Sidebar responsive adjustments */
        [data-testid="stSidebar"] {
            width: fit-content !important;
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
    </style>
    """, unsafe_allow_html=True)
    
    if not is_authenticated():
        login_page()
    else:
        # Sidebar navigation with modern active indicator
        st.sidebar.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #10A19D 0%, #52C4B8 100%);
            padding: 12px 20px;
            border-radius: 12px;
            margin-bottom: 8px;
            text-align: center;
            word-wrap: break-word;
        ">
            <h1 style="color: white; margin: 0; font-size: 1.5em; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.4), 0 0 8px rgba(0, 0, 0, 0.3);">🥗 EatWise</h1>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.user_email:
            # User info - with word wrapping
            st.sidebar.markdown(f"👤 **{st.session_state.user_email}**")
            
            # Logout button
            if st.sidebar.button("🚪 Logout", key="logout_btn", use_container_width=True):
                st.session_state.auth_manager.logout()
                st.session_state.clear()
                st.success("✅ Logged out!")
                st.rerun()
            
            st.sidebar.markdown("<div style='margin: 8px 0;'></div>", unsafe_allow_html=True)
            
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
            
            st.sidebar.markdown("<div style='margin: 8px 0;'></div>", unsafe_allow_html=True)
            
            # ===== QUICK STATS IN SIDEBAR - COMPACT SINGLE ROW =====
            # Get today's data for sidebar stats
            today_meals = db_manager.get_meals_by_date(st.session_state.user_id, date.today())
            today_nutrition = db_manager.get_daily_nutrition_summary(st.session_state.user_id, date.today())
            
            # Get user profile (handles loading and caching automatically)
            user_profile = get_or_load_user_profile()
            
            # Streak info - Use same logic as dashboard
            # Get meals from last 30 days for accurate streak calculation
            days_back = 30
            streak_end_date = date.today()
            streak_start_date = streak_end_date - timedelta(days=days_back)
            recent_all_meals = db_manager.get_meals_in_range(st.session_state.user_id, streak_start_date, streak_end_date)
            meal_dates_all = [datetime.fromisoformat(m.get("logged_at", "")) for m in recent_all_meals]
            streak_info = get_streak_info(meal_dates_all)
            current_streak = streak_info.get('current_streak', 0)
            
            # Get water intake
            water_goal = user_profile.get("water_goal_glasses", 8) if user_profile else 8
            water_today = db_manager.get_daily_water_intake(st.session_state.user_id, date.today())
            
            # Calories calculation
            if user_profile:
                age_group = user_profile.get("age_group", "26-35")
                targets = AGE_GROUP_TARGETS.get(age_group, AGE_GROUP_TARGETS["26-35"])
                cal_display = int(today_nutrition['calories'])
            else:
                cal_display = int(today_nutrition['calories'])
            
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
            
            st.sidebar.markdown("<div style='margin: 8px 0;'></div>", unsafe_allow_html=True)
            
            # Clear the quick nav flag
            if st.session_state.get("quick_nav_to_meal"):
                st.session_state.quick_nav_to_meal = False
            
            
            # Route to selected page
            if st.session_state.current_page == "Dashboard":
                dashboard_page()
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

# Add floating back-to-top button (anchor-based)
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
