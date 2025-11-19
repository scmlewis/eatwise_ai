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
    get_earned_badges
)

# ==================== PAGE CONFIG ====================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
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
                        st.success("✅ Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.warning("⚠️ Please enter email and password")
            
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
                        st.error("❌ Password must be at least 6 characters")
                    else:
                        success, message = auth_manager.sign_up(new_email, new_password, full_name)
                        if success:
                            st.success("✅ Account created! Please login with your credentials.")
                        else:
                            st.error(f"❌ {message}")
                else:
                    st.warning("⚠️ Please fill all fields")
            
            st.markdown("""
            <p style="text-align: center; color: #a0a0a0; margin-top: 12px; font-size: 0.8em;">
                Already have an account? Login in the Login tab ↖️
            </p>
            """, unsafe_allow_html=True)



def dashboard_page():
    """Dashboard/Home page"""
    user_profile = st.session_state.user_profile
    if not user_profile:
        user_profile = db_manager.get_health_profile(st.session_state.user_id)
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
    
    # Prepare data for statistics
    nutrition_by_date = {}
    for meal in recent_meals:
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
    
    # Convert to DataFrame for statistics
    df = pd.DataFrame(list(nutrition_by_date.items()), columns=["Date", "Nutrition"])
    df["calories"] = df["Nutrition"].apply(lambda x: x["calories"])
    df["protein"] = df["Nutrition"].apply(lambda x: x["protein"])
    df["carbs"] = df["Nutrition"].apply(lambda x: x["carbs"])
    df["fat"] = df["Nutrition"].apply(lambda x: x["fat"])
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    
    # Display Statistics with Modern Card Layout
    st.markdown("## 📊 Statistics (Last 7 Days)")
    
    stats_cols = st.columns(4, gap="medium")
    
    # Avg Daily Calories Card
    with stats_cols[0]:
        avg_cal = df["calories"].mean() if len(df) > 0 else 0
        target_cal = targets['calories']
        cal_pct = (avg_cal / target_cal * 100) if target_cal > 0 else 0
        cal_color = "#51CF66" if 80 <= cal_pct <= 120 else ("#FFD43B" if cal_pct < 80 else "#FF6B6B")
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #FF6B1620 0%, #FF6B1640 100%);
            border: 2px solid #FF6B16;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(255, 107, 22, 0.2);
        ">
            <div style="font-size: 32px; margin-bottom: 8px;">🔥</div>
            <div style="font-size: 11px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; font-weight: 600;">Avg. Daily Calories</div>
            <div style="font-size: 24px; font-weight: bold; color: #e0f2f1; margin-bottom: 6px;">{avg_cal:.0f}</div>
            <div style="font-size: 10px; color: #FF6B16; font-weight: 600;">Target: {target_cal}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Total Meals Card
    with stats_cols[1]:
        total_meals = len(recent_meals)
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #10A19D20 0%, #52C4B840 100%);
            border: 2px solid #10A19D;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(16, 161, 157, 0.2);
        ">
            <div style="font-size: 32px; margin-bottom: 8px;">🍽️</div>
            <div style="font-size: 11px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; font-weight: 600;">Total Meals</div>
            <div style="font-size: 24px; font-weight: bold; color: #e0f2f1; margin-bottom: 6px;">{total_meals}</div>
            <div style="font-size: 10px; color: #10A19D; font-weight: 600;">In {days_back} days</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Avg Meals Per Day Card
    with stats_cols[2]:
        avg_meals_per_day = total_meals / days_back if days_back > 0 else 0
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #845EF720 0%, #BE80FF40 100%);
            border: 2px solid #845EF7;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(132, 94, 247, 0.2);
        ">
            <div style="font-size: 32px; margin-bottom: 8px;">📈</div>
            <div style="font-size: 11px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; font-weight: 600;">Avg. Meals/Day</div>
            <div style="font-size: 24px; font-weight: bold; color: #e0f2f1; margin-bottom: 6px;">{avg_meals_per_day:.1f}</div>
            <div style="font-size: 10px; color: #845EF7; font-weight: 600;">meals per day</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Avg Protein Card
    with stats_cols[3]:
        avg_protein = df["protein"].mean() if len(df) > 0 else 0
        target_protein = targets['protein']
        protein_pct = (avg_protein / target_protein * 100) if target_protein > 0 else 0
        protein_color = "#51CF66" if 80 <= protein_pct <= 120 else ("#FFD43B" if protein_pct < 80 else "#FF6B6B")
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #51CF6620 0%, #80C34240 100%);
            border: 2px solid #51CF66;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(81, 207, 102, 0.2);
        ">
            <div style="font-size: 32px; margin-bottom: 8px;">💪</div>
            <div style="font-size: 11px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; font-weight: 600;">Avg. Protein</div>
            <div style="font-size: 24px; font-weight: bold; color: #e0f2f1; margin-bottom: 6px;">{avg_protein:.1f}g</div>
            <div style="font-size: 10px; color: #51CF66; font-weight: 600;">Target: {target_protein}g</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display Achievements with Modern Card Layout
    st.markdown("## 🏆 Achievements")
    
    meal_dates = [datetime.fromisoformat(m.get("logged_at", "")) for m in recent_meals]
    streak_info = get_streak_info(meal_dates)
    
    achieve_cols = st.columns(2, gap="medium")
    
    # Current Streak Card
    with achieve_cols[0]:
        current_streak = streak_info['current_streak']
        streak_emoji = "🔥" if current_streak > 0 else "⭕"
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #FF671520 0%, #FF671540 100%);
            border: 2px solid #FF6715;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 6px 20px rgba(255, 103, 21, 0.25);
        ">
            <div style="font-size: 40px; margin-bottom: 12px;">{streak_emoji}</div>
            <div style="font-size: 12px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; font-weight: 600;">Current Streak</div>
            <div style="font-size: 32px; font-weight: bold; color: #e0f2f1;">{current_streak}</div>
            <div style="font-size: 11px; color: #FF6715; margin-top: 8px; font-weight: 600;">days in a row</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Longest Streak Card
    with achieve_cols[1]:
        longest_streak = streak_info['longest_streak']
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #FFD43B20 0%, #FFC94D40 100%);
            border: 2px solid #FFD43B;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 6px 20px rgba(255, 212, 59, 0.25);
        ">
            <div style="font-size: 40px; margin-bottom: 12px;">🏅</div>
            <div style="font-size: 12px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; font-weight: 600;">Longest Streak</div>
            <div style="font-size: 32px; font-weight: bold; color: #e0f2f1;">{longest_streak}</div>
            <div style="font-size: 11px; color: #FFD43B; margin-top: 8px; font-weight: 600;">personal record</div>
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
                        border: 2px solid #10A19D;
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
    
    # ===== Quick Stats =====
    st.markdown("## 📊 Today's Summary")
    
    col1, col2, col3, col4 = st.columns(4, gap="small")
    
    cards_data = [
        {
            "col": col1,
            "icon": "🔥",
            "label": "Calories",
            "value": f"{daily_nutrition['calories']:.0f}",
            "percentage": calculate_nutrition_percentage(daily_nutrition["calories"], targets["calories"]),
            "target": f"of {targets['calories']}"
        },
        {
            "col": col2,
            "icon": "💪",
            "label": "Protein",
            "value": f"{daily_nutrition['protein']:.1f}g",
            "percentage": calculate_nutrition_percentage(daily_nutrition["protein"], targets["protein"]),
            "target": f"of {targets['protein']}g"
        },
        {
            "col": col3,
            "icon": "🧂",
            "label": "Sodium",
            "value": f"{daily_nutrition['sodium']:.0f}mg",
            "percentage": calculate_nutrition_percentage(daily_nutrition["sodium"], targets["sodium"]),
            "target": f"of {targets['sodium']}mg"
        },
        {
            "col": col4,
            "icon": "🍬",
            "label": "Sugar",
            "value": f"{daily_nutrition['sugar']:.1f}g",
            "percentage": calculate_nutrition_percentage(daily_nutrition["sugar"], targets["sugar"]),
            "target": f"of {targets['sugar']}g"
        }
    ]
    
    for card in cards_data:
        with card["col"]:
            # Determine color based on percentage
            if card["percentage"] > 100:
                color = "#FF6B6B"  # Red for over
                gradient_color = "#FF8A8A"
            elif card["percentage"] >= 80:
                color = "#51CF66"  # Green for good
                gradient_color = "#80C342"
            else:
                color = "#FFD43B"  # Yellow for low
                gradient_color = "#FFC94D"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {color}20 0%, {gradient_color}40 100%);
                border: 2px solid {color};
                border-radius: 10px;
                padding: 12px;
                text-align: center;
                min-height: 130px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                gap: 6px;
                box-shadow: 0 4px 12px rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.15);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            ">
                <div style="font-size: 28px;">{card['icon']}</div>
                <div style="font-size: 10px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">{card['label']}</div>
                <div style="font-size: 18px; font-weight: bold; color: #e0f2f1;">{card['value']}</div>
                <div style="font-size: 9px; color: {color}; font-weight: 600;">↑ {card['percentage']:.0f}% {card['target']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Display Nutrition Targets Progress in styled box
    display_nutrition_targets_progress(daily_nutrition, targets)
    
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
    
    st.markdown("""
    ### Choose how you'd like to log your meal:
    1. **Text Description** - Describe your meal in words
    2. **Photo** - Take a photo of your meal
    """)
    
    tab1, tab2 = st.tabs(["📝 Text", "📸 Photo"])
    
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
                        st.success("✅ Meal analyzed!")
                    else:
                        st.error("❌ Could not analyze meal. Please try again.")
            else:
                st.warning("Please describe your meal")
        
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
                    st.success("✅ Meal saved successfully!")
                    # Clear the analysis from session state
                    del st.session_state.meal_analysis
                    del st.session_state.meal_type
                    st.rerun()
                else:
                    st.error("❌ Failed to save meal")
    
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
                        st.success("✅ Photo analyzed!")
                    else:
                        st.error("❌ Could not analyze photo. Please try again.")
        
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
                    st.success("✅ Meal saved successfully!")
                    # Clear the analysis from session state
                    del st.session_state.photo_analysis
                    st.rerun()
                else:
                    st.error("❌ Failed to save meal")


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
    
    # Time period button options
    st.markdown("### Select time period")
    col1, col2, col3 = st.columns(3, gap="small")
    
    days = 7  # Default value
    with col1:
        if st.button("Last 7 days", use_container_width=True):
            days = 7
            st.session_state.analytics_days = 7
    
    with col2:
        if st.button("Last 2 weeks", use_container_width=True):
            days = 14
            st.session_state.analytics_days = 14
    
    with col3:
        if st.button("Last 30 days", use_container_width=True):
            days = 30
            st.session_state.analytics_days = 30
    
    # Use session state value if it exists
    if "analytics_days" in st.session_state:
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
    
    # ===== Nutrition Trends =====
    st.markdown("## 📊 Nutrition Trends")
    
    # Prepare data for charts
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
        
        st.markdown(f"### Found {len(meals)} meals")
        st.divider()
        
        # Display meals with edit/delete options
        for meal in meals:
            col1, col2, col3 = st.columns([2, 0.5, 0.5])
            
            with col1:
                st.write(f"🍴 **{meal.get('meal_name', 'Unknown')}** - {meal.get('meal_type', 'meal')}")
                st.caption(f"📅 {meal.get('logged_at', 'N/A')}")
            
            with col2:
                if st.button("Edit", key=f"edit_hist_{meal['id']}", use_container_width=True):
                    st.session_state[f"edit_meal_id_{meal['id']}"] = True
            
            with col3:
                if st.button("Delete", key=f"delete_hist_{meal['id']}", use_container_width=True):
                    if db_manager.delete_meal(meal['id']):
                        st.success("Meal deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete meal")
            
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
                                st.success("✅ Meal updated!")
                                st.session_state[f"edit_meal_id_{meal['id']}"] = False
                                st.rerun()
                            else:
                                st.error("❌ Failed to update meal")
                    
                    with btn_col2:
                        if st.form_submit_button("❌ Cancel", use_container_width=True, key=f"cancel_hist_{meal['id']}"):
                            st.session_state[f"edit_meal_id_{meal['id']}"] = False
                            st.rerun()
            
            st.divider()


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
                        "badges_earned": [],
                    }
                    
                    if db_manager.create_health_profile(st.session_state.user_id, profile_data):
                        st.session_state.user_profile = profile_data
                        st.success("✅ Profile created!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to create profile")
        
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
                
                if st.form_submit_button("Update Profile", use_container_width=True):
                    update_data = {
                        "full_name": full_name,
                        "age_group": age_group,
                        "gender": gender,
                        "timezone": timezone,
                        "health_conditions": health_conditions,
                        "dietary_preferences": dietary_preferences,
                        "health_goal": goal,
                    }
                    
                    if db_manager.update_health_profile(st.session_state.user_id, update_data):
                        st.success("✅ Profile updated!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to update profile")
    
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
    
    if not is_authenticated():
        login_page()
    else:
        # Sidebar navigation
        st.sidebar.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #10A19D 0%, #52C4B8 100%);
            padding: 12px 20px;
            border-radius: 12px;
            margin-bottom: 10px;
            text-align: center;
        ">
            <h1 style="color: white; margin: 0; font-size: 1.5em;">🥗 {APP_NAME}</h1>
        </div>
        """, unsafe_allow_html=True)
        st.sidebar.markdown("---")
        
        if st.session_state.user_email:
            st.sidebar.markdown(f"**Logged in as:**\n{st.session_state.user_email}")
            
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
            
            st.sidebar.markdown("---")
            
            # Daily Insight in sidebar
            st.sidebar.markdown("## 💡 Daily Insight")
            try:
                insight = recommender.get_nutrition_trivia()
                st.sidebar.info(f"💬 {insight}")
            except:
                st.sidebar.info("💬 Log more meals to get personalized insights!")
            
            st.sidebar.markdown("---")
            
            # Logout button below daily insight
            if st.sidebar.button("🚪 Logout", use_container_width=True):
                st.session_state.auth_manager.logout()
                st.session_state.clear()
                st.success("✅ Logged out!")
                st.rerun()
            
            # Clear the quick nav flag
            if st.session_state.get("quick_nav_to_meal"):
                st.session_state.quick_nav_to_meal = False
            
            # Add floating Back to Top button
            st.markdown(
                """
                <style>
                    .back-to-top {
                        position: fixed;
                        bottom: 30px;
                        right: 30px;
                        z-index: 999;
                    }
                    .back-to-top button {
                        background: linear-gradient(135deg, #10A19D 0%, #52C4B8 100%);
                        color: white;
                        border: none;
                        border-radius: 50%;
                        width: 56px;
                        height: 56px;
                        font-size: 20px;
                        cursor: pointer;
                        box-shadow: 0 4px 15px rgba(16, 161, 157, 0.4);
                        transition: all 0.3s ease;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        padding: 0;
                        line-height: 1;
                    }
                    .back-to-top button:hover {
                        background: linear-gradient(135deg, #52C4B8 0%, #10A19D 100%);
                        box-shadow: 0 6px 20px rgba(16, 161, 157, 0.6);
                        transform: translateY(-2px);
                    }
                    .back-to-top button:active {
                        transform: translateY(0px);
                    }
                </style>
                <div class="back-to-top">
                    <button id="backToTopBtn" title="Back to top">↑</button>
                </div>
                <script>
                    var backToTopBtn = document.getElementById('backToTopBtn');
                    if (backToTopBtn) {
                        backToTopBtn.addEventListener('click', function() {
                            window.scrollTo({
                                top: 0,
                                behavior: 'smooth'
                            });
                        });
                    }
                </script>
                """,
                unsafe_allow_html=True
            )
            
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
