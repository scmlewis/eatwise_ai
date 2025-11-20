"""
EatWise - AI-Powered Nutrition Hub
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta, time
from typing import Optional, Dict, List
import json
import io
import csv

# Import modules
from config import (
    APP_NAME, APP_DESCRIPTION, SUPABASE_URL, SUPABASE_KEY,
    DAILY_CALORIE_TARGET, DAILY_PROTEIN_TARGET, DAILY_CARBS_TARGET,
    DAILY_FAT_TARGET, DAILY_SODIUM_TARGET, DAILY_SUGAR_TARGET, 
    DAILY_FIBER_TARGET, AGE_GROUP_TARGETS, HEALTH_CONDITION_TARGETS
)
from constants import MEAL_TYPES, HEALTH_CONDITIONS, BADGES, COLORS, BENCHMARK_MESSAGES
from auth import AuthManager, init_auth_session, is_authenticated
from database import DatabaseManager
from nutrition_analyzer import NutritionAnalyzer
from recommender import RecommendationEngine
from nutrition_components import display_nutrition_targets_progress
from utils import (
    init_session_state, get_greeting, calculate_nutrition_percentage,
    get_nutrition_status, format_nutrition_dict, get_streak_info,
    get_earned_badges, build_nutrition_by_date, paginate_items
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

# ==================== PAGE CONFIG ====================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# ==================== STYLING ====================

st.markdown("""
<style>
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
    }
    
    .main {
        padding-top: 2rem;
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
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
        background: linear-gradient(135deg, #10A19D 0%, #52C4B8 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin: 10px 0;
        box-shadow: 0 8px 20px rgba(16, 161, 157, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 28px rgba(16, 161, 157, 0.4);
    }
    
    .nutrition-bar {
        height: 8px;
        background: #e0e0e0;
        border-radius: 4px;
        overflow: hidden;
        margin: 5px 0;
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
    
    /* Modern buttons */
    .stButton > button {
        background: linear-gradient(135deg, #10A19D 0%, #52C4B8 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(16, 161, 157, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 161, 157, 0.4);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #10A19D10 0%, #52C4B810 100%);
        border-radius: 8px;
        padding: 10px 16px;
        border: 1px solid #10A19D;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #10A19D 0%, #52C4B8 100%);
        color: white;
    }
    
    /* Ensure sidebar expansion on all screen sizes after login */
    section[data-testid="stSidebar"] > div {
        width: 250px !important;
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
    # Add custom CSS for login page
    st.markdown("""
    <style>
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
        }
        
        .login-hero h2 {
            font-size: 1.1em;
            margin: 0 0 15px 0;
            font-weight: 300;
            opacity: 0.95;
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
        }
        
        .login-form-container {
            flex: 1;
            background: linear-gradient(135deg, #0D7A7620 0%, #10A19D10 100%);
            padding: 30px;
            border-radius: 20px;
            border: 2px solid #10A19D;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 10px 40px rgba(16, 161, 157, 0.15);
        }
        
        .login-header {
            margin-bottom: 15px;
            text-align: center;
        }
        
        .login-header h3 {
            color: #52C4B8;
            font-size: 1.4em;
            margin: 0;
            margin-bottom: 5px;
        }
        
        .login-tabs {
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
            color: #a0a0a0;
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
            color: #e0f2f1;
            font-weight: 600;
            font-size: 0.85em;
        }
        
        .stTextInput input {
            background: #0a0e27 !important;
            color: #e0f2f1 !important;
            border: 2px solid #10A19D40 !important;
            border-radius: 10px !important;
            padding: 10px 12px !important;
            font-size: 0.9em !important;
        }
        
        .stTextInput input:focus {
            border: 2px solid #10A19D !important;
            box-shadow: 0 0 0 3px rgba(16, 161, 157, 0.2) !important;
        }
        
        /* Forgot Password Button - Subtle Gray Style */
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
        <div class="login-hero">
            <h1>🥗 EatWise</h1>
            <h2>Your AI-Powered Nutrition Hub</h2>
            <p style="font-size: 0.95em; opacity: 0.9; margin-bottom: 15px;">
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
        st.markdown("""
        <div class="login-form-container">
            <div class="login-header">
                <h3>Get Started</h3>
                <p style="color: #a0a0a0; margin: 0; font-size: 0.85em;">Join thousands of users tracking their nutrition</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
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
                        st.session_state.user_profile = user_data
                        show_notification("Login successful! Redirecting...", "success", use_toast=False)
                        st.rerun()
                    else:
                        show_notification(message, "error", use_toast=False)
                else:
                    show_notification("Please enter email and password", "warning", use_toast=False)
            
            # Forgot password button - same width as login button
            st.markdown("""
            <p style="text-align: center; color: #a0a0a0; margin-top: 12px; font-size: 0.8em;">
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
            <p style="text-align: center; color: #a0a0a0; margin-top: 12px; font-size: 0.8em;">
                Already have an account? Login in the Login tab ↖️
            </p>
            """, unsafe_allow_html=True)



def dashboard_page():
    """Dashboard/Home page"""
    # Display pending notification from previous rerun if exists
    if "pending_notification" in st.session_state:
        msg, notif_type = st.session_state.pending_notification
        show_notification(msg, notif_type, use_toast=True)
        del st.session_state.pending_notification
    
    user_profile = st.session_state.user_profile
    if not user_profile:
        user_profile = db_manager.get_health_profile(st.session_state.user_id)
        # normalize after fetch
        user_profile = normalize_profile(user_profile) if user_profile else user_profile
        if not user_profile:
            st.info("Please complete your profile first!")
            profile_page()
            return
    
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
    
    # Motivational notifications
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
    
    st.divider()
    
    # Get nutrition targets
    age_group = user_profile.get("age_group", "26-35")
    targets = AGE_GROUP_TARGETS.get(age_group, AGE_GROUP_TARGETS["26-35"])
    
    # Apply health condition adjustments
    health_conditions = user_profile.get("health_conditions", [])
    for condition in health_conditions:
        if condition in HEALTH_CONDITION_TARGETS:
            targets.update(HEALTH_CONDITION_TARGETS[condition])
    
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
    
    st.markdown("## 🏆 Achievements")
    
    meal_dates = [datetime.fromisoformat(m.get("logged_at", "")) for m in recent_meals]
    streak_info = get_streak_info(meal_dates)
    
    achieve_cols = st.columns(2, gap="small")
    
    # Current Streak Card
    with achieve_cols[0]:
        current_streak = streak_info['current_streak']
        streak_emoji = "🔥" if current_streak > 0 else "⭕"
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #FF671520 0%, #FF671540 100%);
            border: 1px solid #FF6715;
            border-left: 5px solid #FF6715;
            border-radius: 12px;
            padding: 16px 16px;
            text-align: center;
            min-height: 140px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(255, 103, 21, 0.2);
        ">
            <div style="font-size: 32px; margin-bottom: 8px;">{streak_emoji}</div>
            <div style="font-size: 10px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; font-weight: 700;">Current Streak</div>
            <div style="font-size: 28px; font-weight: 900; color: #FFB84D; margin-bottom: 4px;">{current_streak}</div>
            <div style="font-size: 9px; color: #FF6715; font-weight: 700;">days in a row</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Longest Streak Card
    with achieve_cols[1]:
        longest_streak = streak_info['longest_streak']
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #FFD43B20 0%, #FFC94D40 100%);
            border: 1px solid #FFD43B;
            border-left: 5px solid #FFD43B;
            border-radius: 12px;
            padding: 16px 16px;
            text-align: center;
            min-height: 140px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(255, 212, 59, 0.2);
        ">
            <div style="font-size: 32px; margin-bottom: 8px;">🏅</div>
            <div style="font-size: 10px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; font-weight: 700;">Longest Streak</div>
            <div style="font-size: 28px; font-weight: 900; color: #FFD43B; margin-bottom: 4px;">{longest_streak}</div>
            <div style="font-size: 9px; color: #FFD43B; font-weight: 700;">personal record</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display earned badges
    if user_profile.get("badges_earned"):
        st.markdown("### 🎖️ Earned Badges")
        badges_earned = get_earned_badges(user_profile.get("badges_earned", []))
        badge_cols = st.columns(min(len(badges_earned), 4), gap="medium")
        
        for idx, (badge_id, badge_info) in enumerate(badges_earned.items()):
            if idx < len(badge_cols):
                with badge_cols[idx]:
                    st.markdown(f"""
                    <div style="
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
    
    st.divider()
    
    # ===== WATER INTAKE TRACKER =====
    st.markdown("## 💧 Water Intake")
    
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
    
    # Water notifications are handled via st.toast() in button callbacks below
    
    # Water intake card
    st.markdown(f"""
    <div style="
        background: {water_bg};
        border: 2px solid {water_border};
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        margin-bottom: 12px;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="color: #e0f2f1; font-weight: 600; font-size: 15px;">💧 Water Intake</span>
            <span style="color: {water_status_color}; font-weight: bold; font-size: 13px;">{current_water}/{water_goal} glasses</span>
        </div>
        <div style="background: #0a0e27; border-radius: 8px; height: 12px; overflow: hidden; margin-bottom: 10px;">
            <div style="background: linear-gradient(90deg, {water_border} 0%, {water_status_color} 100%); height: 100%; width: {water_percentage}%; transition: width 0.3s ease;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="color: {water_status_color}; font-weight: 600; font-size: 13px;">{water_status}</span>
            <span style="color: #a0a0a0; font-size: 12px;">{water_percentage:.0f}% Complete</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Water action buttons
    water_btn_col1, water_btn_col2, water_btn_col3 = st.columns(3)
    
    with water_btn_col1:
        if st.button("➕ Add Glass", use_container_width=True, key="add_water_btn"):
            if db_manager.log_water(st.session_state.user_id, 1, today):
                st.toast("✅ Glass added!", icon="💧")
                st.rerun()
            else:
                st.toast("❌ Failed to log water", icon="⚠️")
    
    with water_btn_col2:
        if st.button("➖ Remove", use_container_width=True, key="remove_water_btn"):
            if current_water > 0:
                if db_manager.log_water(st.session_state.user_id, -1, today):
                    st.toast("✅ Removed 1 glass", icon="💧")
                    st.rerun()
                else:
                    st.toast("❌ Failed to remove water", icon="⚠️")
            else:
                st.toast("⚠️ No water logged yet", icon="💧")
    
    with water_btn_col3:
        if st.button("🏁 Mark Complete", use_container_width=True, key="fill_water_btn", disabled=(current_water >= water_goal)):
            remaining = max(0, water_goal - current_water)
            if remaining > 0 and db_manager.log_water(st.session_state.user_id, remaining, today):
                st.toast(f"✅ Added {remaining} glasses to complete goal!", icon="🎉")
                st.rerun()
            else:
                st.toast("❌ Failed to complete water goal", icon="⚠️")
    
    st.divider()
    
    # ===== Quick Stats =====
    st.markdown("## 📊 Today's Nutrition Summary")
    
    # Unified nutrition cards with all key info + progress bars
    nutrition_cards = [
        {
            "icon": "🔥",
            "label": "Calories",
            "value": f"{daily_nutrition['calories']:.0f}",
            "target": targets["calories"],
            "percentage": calculate_nutrition_percentage(daily_nutrition["calories"], targets["calories"]),
            "unit": "cal"
        },
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
            <div style="
                background: linear-gradient(135deg, {color}20 0%, {gradient_color}40 100%);
                border: 1px solid {color};
                border-left: 5px solid {color};
                border-radius: 14px;
                padding: 14px;
                text-align: center;
                min-height: 160px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                box-shadow: 0 4px 15px rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.15);
                transition: all 0.3s ease;
            ">
                <div>
                    <div style="font-size: 28px; margin-bottom: 6px;">{card['icon']}</div>
                    <div style="font-size: 9px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; font-weight: 700;">{card['label']}</div>
                </div>
                <div>
                    <div style="font-size: 24px; font-weight: 900; color: #FFB84D; margin-bottom: 8px;">{card['value']}{card['unit']}</div>
                    <div style="background: #0a0e27; border-radius: 4px; height: 4px; margin-bottom: 6px;"><div style="background: linear-gradient(90deg, {color} 0%, {gradient_color} 100%); height: 100%; width: {min(percentage, 100)}%; border-radius: 4px;"></div></div>
                    <div style="font-size: 8px; color: #a0a0a0; margin-bottom: 4px;">of {card['target']}{card['unit']}</div>
                </div>
                <div style="font-size: 8px; color: {color}; font-weight: 700;">{status_icon} {status_text}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # ===== MACRO BREAKDOWN & INSIGHTS =====
    st.divider()
    st.markdown("## 📊 Nutrition Breakdown & Patterns")
    
    # Create a responsive grid layout
    breakdown_col1, breakdown_col2 = st.columns([1.2, 1], gap="medium")
    
    # MACRO BALANCE - Left side
    with breakdown_col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(16, 161, 157, 0.1) 0%, rgba(255, 107, 22, 0.05) 100%);
            border: 1px solid rgba(16, 161, 157, 0.3);
            border-radius: 12px;
            padding: 20px;
        ">
            <h3 style="color: #e0f2f1; margin-top: 0;">🔥 Today's Macro Balance</h3>
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
        <div style="
            background: linear-gradient(135deg, rgba(255, 107, 22, 0.1) 0%, rgba(16, 161, 157, 0.05) 100%);
            border: 1px solid rgba(255, 107, 22, 0.3);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
        ">
            <h3 style="color: #e0f2f1; margin-top: 0;">🍽️ Today's Eating Patterns</h3>
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
                <div style="text-align: center; padding: 12px; background: rgba(16, 161, 157, 0.15); border-radius: 8px;">
                    <div style="font-size: 24px; margin-bottom: 8px;">{emoji}</div>
                    <div style="font-size: 18px; font-weight: bold; color: #e0f2f1;">{count}</div>
                    <div style="font-size: 12px; color: #a0a0a0;">{period}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Remove duplicate EATING TIME PATTERNS section that was below
    
    # ===== Today's Meals =====
    st.markdown("## 🍽️ Today's Meals")
    
    if meals:
        for meal in meals:
            st.markdown(f"""
            <div style="
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
    # Display pending notification from previous rerun if exists
    if "pending_notification" in st.session_state:
        msg, notif_type = st.session_state.pending_notification
        show_notification(msg, notif_type, use_toast=True)
        del st.session_state.pending_notification
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #10A19D 0%, #52C4B8 100%);
        padding: 15px 25px;
        border-radius: 15px;
        margin-bottom: 20px;
    ">
        <h1 style="color: white; margin: 0; font-size: 1.6em; line-height: 1.2;">📸 Log Your Meal</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== TIME-BASED SUGGESTIONS =====
    from datetime import datetime as dt
    current_hour = dt.now().hour
    
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
            if st.button("➕ Quick Add", use_container_width=True, key="quick_add_btn"):
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
                    st.session_state.pending_notification = ("Meal added!", "success")
                    st.rerun()
                else:
                    show_notification("Failed to add meal", "error", use_toast=True)
        
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
                        st.session_state.pending_notification = ("Meal analyzed!", "success")
                    else:
                        show_notification("Could not analyze meal. Please try again.", "error", use_toast=True)
            else:
                show_notification("Please describe your meal", "warning", use_toast=True)
        
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
            if st.button("Save This Meal", use_container_width=True):
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
                    st.session_state.pending_notification = ("Meal saved successfully!", "success")
                    # Clear the analysis from session state
                    del st.session_state.meal_analysis
                    del st.session_state.meal_type
                    st.rerun()
                else:
                    show_notification("Failed to save meal", "error", use_toast=True)
    
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
                        show_notification("Photo analyzed!", "success", use_toast=True)
                    else:
                        show_notification("Could not analyze photo. Please try again.", "error", use_toast=True)
        
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
            if st.button("Save This Meal", use_container_width=True, key="save_photo_meal"):
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
                    st.session_state.pending_notification = ("Meal saved successfully!", "success")
                    # Clear the analysis from session state
                    del st.session_state.photo_analysis
                    st.rerun()
                else:
                    show_notification("Failed to save meal", "error", use_toast=True)
    
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
        
        if st.button("📥 Analyze & Save All Meals", use_container_width=True, key="batch_save_btn"):
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
    
    user_profile = st.session_state.user_profile
    if not user_profile:
        user_profile = db_manager.get_health_profile(st.session_state.user_id)
        if not user_profile:
            st.info("Please complete your profile first!")
            return

    # Normalize profile structure to avoid mapping issues (strings vs lists etc.)
    try:
        user_profile = normalize_profile(user_profile)
        st.session_state.user_profile = user_profile
    except Exception:
        # non-fatal - fall back to raw profile
        pass

    # Optional debug output to inspect profile objects when mapping targets
    try:
        if st.sidebar.checkbox("Debug: show profile objects", key="dbg_profile_objects"):
            st.sidebar.markdown("**Debug: Profile Objects**")
            st.sidebar.write("session_profile:", st.session_state.get("user_profile"))
            st.sidebar.write("db_profile:", db_manager.get_health_profile(st.session_state.user_id))
            st.sidebar.write("Available age groups:", list(AGE_GROUP_TARGETS.keys()))
    except Exception:
        # Keep debug optional and non-blocking if sidebar isn't available
        pass
    
    # Initialize days from session state or use default
    if "analytics_days" not in st.session_state:
        st.session_state.analytics_days = 7
    
    # Time period button options
    st.markdown("### Select time period")
    col1, col2, col3 = st.columns(3, gap="small")
    
    with col1:
        if st.button("Last 7 days", use_container_width=True):
            st.session_state.analytics_days = 7
            st.rerun()
    
    with col2:
        if st.button("Last 2 weeks", use_container_width=True):
            st.session_state.analytics_days = 14
            st.rerun()
    
    with col3:
        if st.button("Last 30 days", use_container_width=True):
            st.session_state.analytics_days = 30
            st.rerun()
    
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
        nutrition = meal.get("Nutrition", {})
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
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #FF6B1620 0%, #FF6B1640 100%);
            border: 1px solid #FF6B16;
            border-left: 5px solid #FF6B16;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(255, 107, 22, 0.2);
            transition: transform 0.2s ease;
        ">
            <div style="font-size: 28px; margin-bottom: 6px;">🔥</div>
            <div style="font-size: 11px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; font-weight: 700;">Avg Calories</div>
            <div style="font-size: 28px; font-weight: 900; color: #FFB84D; margin-bottom: 8px;">{avg_cal:.0f}</div>
            <div style="font-size: 9px; color: #FF6B16; font-weight: 700; margin-bottom: 6px;">of {target_cal}</div>
            <div style="background: #0a0e27; border-radius: 4px; height: 4px; margin-bottom: 8px;"><div style="background: linear-gradient(90deg, #FF6B16 0%, #FF8A4A 100%); height: 100%; width: {min(cal_pct, 100)}%; border-radius: 4px;"></div></div>
            <div style="font-size: 9px; color: #FF6B16; font-weight: 600;">{cal_status} {cal_pct:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Total Meals Card
    with stats_cols[1]:
        total_meals = len(meals)
        meals_status = "🔥" if total_meals >= 14 else ("✅" if total_meals >= 7 else "⚠️")
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #10A19D20 0%, #52C4B840 100%);
            border: 1px solid #10A19D;
            border-left: 5px solid #10A19D;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(16, 161, 157, 0.2);
        ">
            <div style="font-size: 28px; margin-bottom: 6px;">🍽️</div>
            <div style="font-size: 11px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; font-weight: 700;">Total Meals</div>
            <div style="font-size: 28px; font-weight: 900; color: #5DDCD6; margin-bottom: 8px;">{total_meals}</div>
            <div style="font-size: 9px; color: #10A19D; font-weight: 700; margin-bottom: 6px;">{days} days</div>
            <div style="background: #0a0e27; border-radius: 4px; height: 4px; margin-bottom: 8px;"><div style="background: linear-gradient(90deg, #10A19D 0%, #52C4B8 100%); height: 100%; width: {min((total_meals/21)*100, 100)}%; border-radius: 4px;"></div></div>
            <div style="font-size: 9px; color: #10A19D; font-weight: 600;">{meals_status} {(total_meals/days):.1f}/day</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Avg Meals Per Day Card
    with stats_cols[2]:
        avg_meals_per_day = total_meals / days if days > 0 else 0
        meal_freq_status = "✅" if 2 <= avg_meals_per_day <= 4 else ("⚠️" if avg_meals_per_day < 2 else "⚡")
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #845EF720 0%, #BE80FF40 100%);
            border: 1px solid #845EF7;
            border-left: 5px solid #845EF7;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(132, 94, 247, 0.2);
        ">
            <div style="font-size: 28px; margin-bottom: 6px;">📈</div>
            <div style="font-size: 11px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; font-weight: 700;">Meals/Day</div>
            <div style="font-size: 28px; font-weight: 900; color: #B89FFF; margin-bottom: 8px;">{avg_meals_per_day:.1f}</div>
            <div style="font-size: 9px; color: #845EF7; font-weight: 700; margin-bottom: 6px;">avg</div>
            <div style="background: #0a0e27; border-radius: 4px; height: 4px; margin-bottom: 8px;"><div style="background: linear-gradient(90deg, #845EF7 0%, #BE80FF 100%); height: 100%; width: {min((avg_meals_per_day/5)*100, 100)}%; border-radius: 4px;"></div></div>
            <div style="font-size: 9px; color: #845EF7; font-weight: 600;">{meal_freq_status}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Avg Protein Card
    with stats_cols[3]:
        avg_protein = df["protein"].mean() if len(df) > 0 else 0
        target_protein = targets['protein']
        protein_pct = (avg_protein / target_protein * 100) if target_protein > 0 else 0
        protein_status = "✅" if 80 <= protein_pct <= 120 else ("⚠️" if protein_pct < 80 else "⚡")
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #51CF6620 0%, #80C34240 100%);
            border: 1px solid #51CF66;
            border-left: 5px solid #51CF66;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(81, 207, 102, 0.2);
        ">
            <div style="font-size: 28px; margin-bottom: 6px;">💪</div>
            <div style="font-size: 11px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; font-weight: 700;">Avg Protein</div>
            <div style="font-size: 28px; font-weight: 900; color: #7FDB8F; margin-bottom: 8px;">{avg_protein:.1f}g</div>
            <div style="font-size: 9px; color: #51CF66; font-weight: 700; margin-bottom: 6px;">of {target_protein}g</div>
            <div style="background: #0a0e27; border-radius: 4px; height: 4px; margin-bottom: 8px;"><div style="background: linear-gradient(90deg, #51CF66 0%, #80C342 100%); height: 100%; width: {min(protein_pct, 100)}%; border-radius: 4px;"></div></div>
            <div style="font-size: 9px; color: #51CF66; font-weight: 600;">{protein_status} {protein_pct:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
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
    
    user_profile = st.session_state.user_profile
    if not user_profile:
        user_profile = db_manager.get_health_profile(st.session_state.user_id)
        if not user_profile:
            st.info("Please complete your profile first!")
            return
    
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
    
    # ===== Personalized Recommendations =====
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
    
    # ===== Weekly Meal Plan =====
    st.markdown("## 📅 Weekly Meal Plan")
    
    if st.button("Generate 7-Day Meal Plan", use_container_width=True):
        with st.spinner("🤖 Creating your personalized meal plan..."):
            meal_plan = recommender.get_weekly_meal_plan(
                user_profile,
                targets,
                user_profile.get("dietary_preferences", [])
            )
            
            if meal_plan:
                for day, meals_list in meal_plan.items():
                    with st.expander(f"📅 {day}"):
                        for meal in meals_list:
                            st.write(f"**{meal.get('meal_type').title()}:** {meal.get('meal_name')}")
                            st.caption(meal.get('description', ''))
    
    # ===== BEST & WORST MEALS =====
    st.divider()
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
    
    # ===== Health Insights =====
    st.markdown("## 📊 Health Insights")
    st.caption("💡 Click the button below to analyze your eating patterns (this uses API calls)")
    
    if st.button("🤖 Analyze Health Insights", use_container_width=True):
        with st.spinner("🤖 Analyzing your eating patterns..."):
            nutrition_history = db_manager.get_weekly_nutrition_summary(st.session_state.user_id, date.today())
            
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
                        # Show copyable text area
                        st.info("📝 Select all text below and copy (Ctrl+C):")
                        st.text_area("Insights:", value=insights_text, height=250, disabled=True, key="copy_insights")
                
                with col2:
                    if st.button("🔗 Share as Text", use_container_width=True):
                        # Show formatted text for sharing
                        with st.expander("📧 Shareable Format", expanded=True):
                            st.text_area("Copy and share this:", value=insights_text, height=250, disabled=True, key="share_insights")
    
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
    
    # ===== NUTRITION TIPS =====
    st.divider()
    st.markdown("## 💡 Nutrition Tips")
    
    nutrition_tips = [
        "🥗 Eat a variety of colorful vegetables - each color has different nutrients!",
        "💧 Aim to drink 8 glasses of water daily for optimal hydration",
        "🍗 Include lean proteins in every meal to keep you feeling full longer",
        "🌾 Whole grains are better than refined grains for sustained energy",
        "🥑 Healthy fats from avocados, nuts, and olive oil support heart health",
        "🍓 Berries are packed with antioxidants and vitamins",
        "🥦 Cruciferous vegetables like broccoli are anti-inflammatory powerhouses",
        "🍚 Balance your macros: aim for 40% carbs, 30% protein, 30% fat",
        "⏰ Eat smaller meals more frequently to maintain stable energy levels",
        "🚫 Limit added sugars - they provide empty calories",
        "🧂 Reduce sodium intake to support heart and kidney health",
        "🥜 Nuts and seeds are great sources of protein and healthy fats",
        "🍌 Potassium-rich foods help maintain healthy blood pressure",
        "🥕 Vitamin A from orange vegetables supports eye health",
        "🍊 Citrus fruits are excellent sources of vitamin C for immunity",
    ]
    
    import random
    daily_tip = random.choice(nutrition_tips)
    st.info(f"**Did you know?** {daily_tip}")
    
    # ===== NUTRITION TARGETS SUMMARY =====
    st.divider()
    st.markdown("## 🎯 Your Nutrition Targets")
    
    if user_profile:
        # ===== PERSONALIZATION CONTEXT =====
        # Only render the three context boxes when meaningful profile values exist.
        age_group = user_profile.get('age_group', 'N/A')
        health_goal_val = user_profile.get('health_goal', 'N/A')
        health_conditions_list = user_profile.get('health_conditions', []) or []

        has_personalization = (
            (age_group and age_group != 'N/A') or
            (health_goal_val and health_goal_val != 'N/A') or
            (isinstance(health_conditions_list, list) and len(health_conditions_list) > 0)
        )

        if has_personalization:
            st.markdown("**Your targets are personalized based on:**")
            context_cols = st.columns(3, gap="small")

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

            with context_cols[2]:
                health_conditions = ', '.join(health_conditions_list) or 'None'
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #8B5CF620 0%, #D97706 40 100%);
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
            # If no personalization data available, hide the decorative boxes and prompt to complete profile.
            st.info("Complete your profile under 'My Profile' to see personalized targets.")
        
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
                use_container_width=True,
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
                use_container_width=True,
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
                    use_container_width=True,
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
        if st.button("🔍 Search", use_container_width=True, key="search_meals_btn"):
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
                    if db_manager.delete_meal(meal['id']):
                        st.session_state.pending_notification = ("Meal deleted!", "success")
                        st.rerun()
                    else:
                        show_notification("Failed to delete meal", "error", use_toast=True)
            
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
                    if st.button("✅ Duplicate Meal", use_container_width=True, key=f"confirm_dup_{meal['id']}"):
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
                            st.session_state.pending_notification = (f"{meal.get('meal_name')} duplicated to {dup_date}!", "success")
                            st.session_state[f"dup_meal_id_{meal['id']}"] = False
                            st.rerun()
                        else:
                            show_notification("Failed to duplicate meal", "error", use_toast=True)
                
                with dup_col2:
                    if st.button("❌ Cancel", use_container_width=True, key=f"cancel_dup_{meal['id']}"):
                        st.session_state[f"dup_meal_id_{meal['id']}"] = False
                        st.rerun()
                
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
                        if st.form_submit_button("💾 Save Changes", use_container_width=True, key=f"save_hist_{meal['id']}"):
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
                                st.session_state.pending_notification = ("Meal updated!", "success")
                                st.session_state[f"edit_meal_id_{meal['id']}"] = False
                                st.rerun()
                            else:
                                show_notification("Failed to update meal", "error", use_toast=True)
                    
                    with btn_col2:
                        if st.form_submit_button("❌ Cancel", use_container_width=True, key=f"cancel_hist_{meal['id']}"):
                            st.session_state[f"edit_meal_id_{meal['id']}"] = False
                            st.rerun()
            
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
        # Always fetch fresh profile from database
        user_profile = db_manager.get_health_profile(st.session_state.user_id)
        
        st.markdown(f"**Email:** {user_email}")
        
        # Get or create profile
        if not user_profile:
            st.markdown("## Complete Your Profile")
            
            with st.form("health_profile_form"):
                full_name = st.text_input("Full Name")
                age_group = st.selectbox(
                    "Age Group",
                    options=list(AGE_GROUP_TARGETS.keys()),
                    help="This helps us set appropriate nutrition targets"
                )
                
                gender = st.selectbox(
                    "Gender",
                    options=["Male", "Female", "Other", "Prefer not to say"],
                    help="This helps us provide personalized nutrition recommendations"
                )
                
                timezone = st.selectbox(
                    "Timezone",
                    options=[
                        "UTC", "UTC-12", "UTC-11", "UTC-10", "UTC-9", "UTC-8", "UTC-7", "UTC-6", "UTC-5", "UTC-4", "UTC-3", "UTC-2", "UTC-1",
                        "UTC+1", "UTC+2", "UTC+3", "UTC+4", "UTC+5", "UTC+5:30", "UTC+6", "UTC+7", "UTC+8", "UTC+9", "UTC+10", "UTC+11", "UTC+12"
                    ],
                    index=0,
                    help="Your timezone for meal timing recommendations"
                )
                
                health_conditions = st.multiselect(
                    "Health Conditions",
                    options=list(HEALTH_CONDITIONS.keys()),
                    format_func=lambda x: HEALTH_CONDITIONS.get(x, x),
                    help="Select any health conditions that apply"
                )
                
                dietary_preferences = st.multiselect(
                    "Dietary Preferences",
                    options=["vegetarian", "vegan", "gluten_free", "halal", "kosher"],
                    help="Select any dietary restrictions"
                )
                
                goal = st.selectbox(
                    "Health Goal",
                    options=["maintain", "weight_loss", "weight_gain", "muscle_gain", "general_health"],
                    help="What's your primary health goal?"
                )
                
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
                        "health_conditions": health_conditions,
                        "dietary_preferences": dietary_preferences,
                        "health_goal": goal,
                        "water_goal_glasses": water_goal,
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
                full_name = st.text_input("Full Name", value=user_profile.get("full_name", ""))
                age_group = st.selectbox(
                    "Age Group",
                    options=list(AGE_GROUP_TARGETS.keys()),
                    index=list(AGE_GROUP_TARGETS.keys()).index(user_profile.get("age_group", "26-35"))
                )
                
                gender_options = ["Male", "Female", "Other", "Prefer not to say"]
                gender_value = user_profile.get("gender", "Prefer not to say")
                gender_index = gender_options.index(gender_value) if gender_value in gender_options else 3
                gender = st.selectbox(
                    "Gender",
                    options=gender_options,
                    index=gender_index,
                    help="This helps us provide personalized nutrition recommendations"
                )
                
                timezone_options = [
                    "UTC", "UTC-12", "UTC-11", "UTC-10", "UTC-9", "UTC-8", "UTC-7", "UTC-6", "UTC-5", "UTC-4", "UTC-3", "UTC-2", "UTC-1",
                    "UTC+1", "UTC+2", "UTC+3", "UTC+4", "UTC+5", "UTC+5:30", "UTC+6", "UTC+7", "UTC+8", "UTC+9", "UTC+10", "UTC+11", "UTC+12"
                ]
                timezone_value = user_profile.get("timezone", "UTC")
                timezone_index = timezone_options.index(timezone_value) if timezone_value in timezone_options else 0
                timezone = st.selectbox(
                    "Timezone",
                    options=timezone_options,
                    index=timezone_index,
                    help="Your timezone for meal timing recommendations"
                )
                
                health_conditions = st.multiselect(
                    "Health Conditions",
                    options=list(HEALTH_CONDITIONS.keys()),
                    default=user_profile.get("health_conditions", []),
                    format_func=lambda x: HEALTH_CONDITIONS.get(x, x)
                )
                
                dietary_preferences = st.multiselect(
                    "Dietary Preferences",
                    options=["vegetarian", "vegan", "gluten_free", "halal", "kosher"],
                    default=user_profile.get("dietary_preferences", [])
                )
                
                goal = st.selectbox(
                    "Health Goal",
                    options=["maintain", "weight_loss", "weight_gain", "muscle_gain", "general_health"],
                    index=["maintain", "weight_loss", "weight_gain", "muscle_gain", "general_health"].index(
                        user_profile.get("health_goal", "maintain")
                    )
                )
                
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
                        "health_conditions": health_conditions,
                        "dietary_preferences": dietary_preferences,
                        "health_goal": goal,
                        "water_goal_glasses": water_goal,
                    }
                    
                    if db_manager.update_health_profile(st.session_state.user_id, update_data):
                        # Refresh the session profile so other pages reflect updated values immediately
                        fetched = db_manager.get_health_profile(st.session_state.user_id) or {**user_profile, **update_data}
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
        
        with col2:
            st.markdown("### 💡 Smart Insights")
            st.markdown("""
            - AI-powered health analysis
            - Personalized recommendations
            - Strength identification
            - Areas for improvement
            """)
            
            st.markdown("### 📋 Meal History")
            st.markdown("""
            - Browse all logged meals
            - Edit meal details
            - Delete meals
            - Date range filtering
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
    
    with tab4:
        st.markdown("## Frequently Asked Questions")
        
        with st.expander("❓ How accurate is the nutrition analysis?"):
            st.markdown("""
            Our AI-powered analysis provides realistic estimates based on:
            - Your detailed descriptions or food photos
            - Standard portion sizes
            - USDA food composition databases
            
            For medical or precise nutritional needs, consult a nutritionist.
            """)
        
        with st.expander("❓ Can I edit meals after logging them?"):
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
    
    st.divider()
    st.markdown("""
    ### 📧 Need More Help?
    Have questions or suggestions? We'd love to hear from you!
    - **GitHub**: https://github.com/scmlewis/eatwise_ai
    - **Report Issues**: Create an issue on GitHub
    
    ---
    **Last Updated**: November 19, 2025 (v1.0.0)
    """)


# ==================== MAIN APP ====================

def main():
    """Main app logic"""
    
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
        # Sidebar navigation
        st.sidebar.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #10A19D 0%, #52C4B8 100%);
            padding: 12px 20px;
            border-radius: 12px;
            margin-bottom: 8px;
            text-align: center;
            word-wrap: break-word;
        ">
            <h1 style="color: white; margin: 0; font-size: 1.5em;">🥗 EatWise</h1>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.user_email:
            # User info - with word wrapping
            st.sidebar.markdown(f"👤 **{st.session_state.user_email}**")
            
            # Logout button
            if st.sidebar.button("🚪 Logout", use_container_width=True, key="logout_btn"):
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
                "My Profile": "👤",
                "Help": "❓",
            }
            
            # Check if quick navigation was triggered
            default_page = "Log Meal" if st.session_state.get("quick_nav_to_meal") else "Dashboard"
            default_index = list(pages.keys()).index(default_page)
            
            # Store nav index in session state
            if "nav_index" not in st.session_state:
                st.session_state.nav_index = default_index
            
            # Navigation in sidebar - radio buttons instead of dropdown
            st.sidebar.markdown("**Navigation**")
            selected_page = st.sidebar.radio(
                "Pages",
                options=list(pages.keys()),
                index=st.session_state.nav_index,
                format_func=lambda x: f"{pages[x]} {x}",
                label_visibility="collapsed",
                key="page_selector"
            )
            st.session_state.nav_index = list(pages.keys()).index(selected_page)
            
            st.sidebar.markdown("<div style='margin: 8px 0;'></div>", unsafe_allow_html=True)
            
            # ===== QUICK STATS IN SIDEBAR - COMPACT SINGLE ROW =====
            # Get today's data for sidebar stats
            today_meals = db_manager.get_meals_by_date(st.session_state.user_id, date.today())
            today_nutrition = db_manager.get_daily_nutrition_summary(st.session_state.user_id, date.today())
            user_profile = st.session_state.user_profile
            
            # Streak info
            if len(today_meals) > 0:
                recent_all_meals = db_manager.get_recent_meals(st.session_state.user_id, limit=30)
                meal_dates_all = [datetime.fromisoformat(m.get("logged_at", "")) for m in recent_all_meals]
                streak_info = get_streak_info(meal_dates_all)
                current_streak = streak_info.get('current_streak', 0)
            else:
                current_streak = 0
            
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
                    <div style="font-size: 24px; font-weight: bold; color: #FFB84D; margin-bottom: 4px;">{current_streak}</div>
                    <div style="font-size: 11px; color: #e0f2f1; font-weight: 500;">Streak</div>
                </div>
                """, unsafe_allow_html=True)
            
            with stat_cols[1]:
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #FFB84D; margin-bottom: 4px;">{cal_display}</div>
                    <div style="font-size: 11px; color: #e0f2f1; font-weight: 500;">Calories</div>
                </div>
                """, unsafe_allow_html=True)
            
            with stat_cols[2]:
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #3B82F6; margin-bottom: 4px;">{water_today}/{water_goal}</div>
                    <div style="font-size: 11px; color: #e0f2f1; font-weight: 500;">Water</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.sidebar.markdown("<div style='margin: 8px 0;'></div>", unsafe_allow_html=True)
            
            # Daily Insight in sidebar - More compact
            insight_header = st.sidebar.container()
            with insight_header:
                st.markdown("### 💡 Daily Insight", help="Nutrition tips and insights for better health")
                try:
                    insight = recommender.get_nutrition_trivia()
                    st.markdown(f"<div style='background: rgba(16, 161, 157, 0.1); padding: 12px; border-radius: 8px; border-left: 3px solid #10A19D; font-size: 13px; line-height: 1.4;'>{insight}</div>", unsafe_allow_html=True)
                except:
                    st.markdown("<div style='background: rgba(16, 161, 157, 0.1); padding: 12px; border-radius: 8px; border-left: 3px solid #10A19D; font-size: 13px;'>💭 Log meals to get personalized tips!</div>", unsafe_allow_html=True)
            
            # Clear the quick nav flag
            if st.session_state.get("quick_nav_to_meal"):
                st.session_state.quick_nav_to_meal = False
            
            
            # Route to selected page
            if selected_page == "Dashboard":
                dashboard_page()
            elif selected_page == "Log Meal":
                meal_logging_page()
            elif selected_page == "Analytics":
                analytics_page()
            elif selected_page == "Meal History":
                meal_history_page()
            elif selected_page == "Insights":
                insights_page()
            elif selected_page == "My Profile":
                profile_page()
            elif selected_page == "Help":
                help_page()


if __name__ == "__main__":
    main()
