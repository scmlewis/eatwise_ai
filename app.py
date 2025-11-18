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
        --secondary-color: #FF6B6B;
        --success-color: #51CF66;
        --warning-color: #FFA500;
        --danger-color: #FF0000;
    }
    
    .main {
        padding-top: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
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
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("# 🥗 Welcome to EatWise")
        st.markdown("### Your AI-Powered Nutrition Hub")
        st.markdown("""
        Track your meals, understand your nutrition, and get personalized recommendations.
        
        **Features:**
        - 📸 Smart meal logging (text or photo)
        - 📊 Instant nutritional analysis
        - 📈 Habit tracking and progress monitoring
        - 💡 AI-powered personalized suggestions
        - 🎮 Gamification with badges and streaks
        """)
    
    with col2:
        st.markdown("### Get Started")
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.markdown("#### Login to your account")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            
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
                    st.warning("Please enter email and password")
        
        with tab2:
            st.markdown("#### Create new account")
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_password")
            full_name = st.text_input("Full Name", key="signup_name")
            
            if st.button("Sign Up", key="signup_btn", use_container_width=True):
                if new_email and new_password and full_name:
                    success, message = auth_manager.sign_up(new_email, new_password, full_name)
                    if success:
                        st.success("✅ Account created! Please login.")
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.warning("Please fill all fields")


# ==================== MAIN APP PAGES ====================

def dashboard_page():
    """Dashboard/Home page"""
    st.markdown(f"# {get_greeting()} 👋")
    
    user_profile = st.session_state.user_profile
    if not user_profile:
        user_profile = db_manager.get_health_profile(st.session_state.user_id)
        if not user_profile:
            st.info("Please complete your profile first!")
            profile_page()
            return
    
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
            elif card["percentage"] >= 80:
                color = "#51CF66"  # Green for good
            else:
                color = "#FFD43B"  # Yellow for low
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {color}20 0%, {color}40 100%);
                border: 2px solid {color};
                border-radius: 10px;
                padding: 12px;
                text-align: center;
                min-height: 130px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                gap: 6px;
            ">
                <div style="font-size: 28px;">{card['icon']}</div>
                <div style="font-size: 10px; color: #a0a0a0; text-transform: uppercase; letter-spacing: 0.5px;">{card['label']}</div>
                <div style="font-size: 18px; font-weight: bold; color: #e0f2f1;">{card['value']}</div>
                <div style="font-size: 9px; color: {color}; font-weight: 600;">↑ {card['percentage']:.0f}% {card['target']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # ===== Nutrition Bars =====
    st.markdown("### Nutrition Targets Progress")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Calories
        cal_pct = min(calculate_nutrition_percentage(daily_nutrition["calories"], targets["calories"]), 100)
        st.write("🔥 Calories")
        st.progress(cal_pct / 100, text=f"{cal_pct:.0f}%")
        
        # Protein
        protein_pct = min(calculate_nutrition_percentage(daily_nutrition["protein"], targets["protein"]), 100)
        st.write("💪 Protein")
        st.progress(protein_pct / 100, text=f"{protein_pct:.0f}%")
        
        # Carbs
        carbs_pct = min(calculate_nutrition_percentage(daily_nutrition["carbs"], targets["carbs"]), 100)
        st.write("🍚 Carbs")
        st.progress(carbs_pct / 100, text=f"{carbs_pct:.0f}%")
    
    with col2:
        # Fat
        fat_pct = min(calculate_nutrition_percentage(daily_nutrition["fat"], targets["fat"]), 100)
        st.write("🫒 Fat")
        st.progress(fat_pct / 100, text=f"{fat_pct:.0f}%")
        
        # Sodium
        sodium_pct = min(calculate_nutrition_percentage(daily_nutrition["sodium"], targets["sodium"]), 100)
        st.write("🧂 Sodium")
        st.progress(sodium_pct / 100, text=f"{sodium_pct:.0f}%")
        
        # Sugar
        sugar_pct = min(calculate_nutrition_percentage(daily_nutrition["sugar"], targets["sugar"]), 100)
        st.write("🍬 Sugar")
        st.progress(sugar_pct / 100, text=f"{sugar_pct:.0f}%")
    
    # ===== Today's Meals =====
    st.markdown("## 🍽️ Today's Meals")
    
    if meals:
        for meal in meals:
            col1, col2, col3, col4 = st.columns([2, 0.5, 0.5, 0.5])
            
            with col1:
                st.write(f"🍴 **{meal.get('meal_name', 'Unknown Meal')}** - {meal.get('meal_type', 'meal')}")
                st.caption(f"Logged at: {meal.get('logged_at', 'N/A')}")
            
            with col2:
                if st.button("Edit", key=f"edit_{meal['id']}", use_container_width=True):
                    st.session_state[f"edit_meal_id_{meal['id']}"] = True
            
            with col3:
                portion = st.number_input(
                    f"Multiplier",
                    value=1.0,
                    min_value=0.1,
                    max_value=5.0,
                    step=0.1,
                    key=f"multiplier_{meal['id']}",
                    help="Adjust portion size"
                )
            
            with col4:
                if st.button("Delete", key=f"delete_{meal['id']}", use_container_width=True):
                    if db_manager.delete_meal(meal['id']):
                        st.success("Meal deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete meal")
            
            # Show meal details
            with st.expander("View Details", expanded=False):
                st.write(f"**Description:** {meal.get('description', 'N/A')}")
                nutrition = meal.get("nutrition", {})
                
                # Apply multiplier to nutrition
                multiplied_nutrition = {k: v * portion for k, v in nutrition.items()}
                
                st.text(nutrition_analyzer.get_nutrition_facts(multiplied_nutrition))
            
            # Edit modal
            if st.session_state.get(f"edit_meal_id_{meal['id']}", False):
                st.divider()
                st.subheader(f"Edit: {meal.get('meal_name', 'Meal')}")
                
                with st.form(f"edit_form_{meal['id']}"):
                    meal_name = st.text_input("Meal Name", value=meal.get('meal_name', ''))
                    meal_type = st.selectbox(
                        "Meal Type",
                        options=list(MEAL_TYPES.keys()),
                        index=list(MEAL_TYPES.keys()).index(meal.get('meal_type', 'breakfast')) if meal.get('meal_type') in MEAL_TYPES else 0
                    )
                    description = st.text_area("Description", value=meal.get('description', ''))
                    
                    # Edit nutrition
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        calories = st.number_input("Calories", value=float(meal.get('nutrition', {}).get('calories', 0)), min_value=0.0)
                        protein = st.number_input("Protein (g)", value=float(meal.get('nutrition', {}).get('protein', 0)), min_value=0.0)
                        carbs = st.number_input("Carbs (g)", value=float(meal.get('nutrition', {}).get('carbs', 0)), min_value=0.0)
                    
                    with col2:
                        fat = st.number_input("Fat (g)", value=float(meal.get('nutrition', {}).get('fat', 0)), min_value=0.0)
                        sodium = st.number_input("Sodium (mg)", value=float(meal.get('nutrition', {}).get('sodium', 0)), min_value=0.0)
                        sugar = st.number_input("Sugar (g)", value=float(meal.get('nutrition', {}).get('sugar', 0)), min_value=0.0)
                    
                    with col3:
                        fiber = st.number_input("Fiber (g)", value=float(meal.get('nutrition', {}).get('fiber', 0)), min_value=0.0)
                    
                    if st.form_submit_button("Save Changes", use_container_width=True):
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
    else:
        st.info("No meals logged yet. Start by logging a meal!")
    
    # ===== Quick Add Meal =====
    st.markdown("## ➕ Quick Add Meal")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("📸 Log a Meal", use_container_width=True, key="quick_add_meal"):
            st.session_state.quick_nav_to_meal = True
            st.rerun()
    
    # ===== Insights =====
    st.markdown("## 💡 Daily Insight")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        insight = recommender.get_nutrition_trivia()
        st.info(f"💬 {insight}")


def meal_logging_page():
    """Meal logging page"""
    st.markdown("# 📸 Log Your Meal")
    
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
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.text(nutrition_analyzer.get_nutrition_facts(analysis['nutrition']))
            
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
            
            # Portion size multiplier
            st.markdown("### 📏 Portion Size")
            portion_multiplier = st.selectbox(
                "How much did you eat?",
                options=[0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0],
                index=2,
                format_func=lambda x: f"{x:.2f}x" if x != 1.0 else "1x (Normal portion)"
            )
            
            # Apply multiplier to nutrition and display
            multiplied_nutrition = {k: v * portion_multiplier for k, v in analysis['nutrition'].items()}
            st.info(f"**Nutrition (with {portion_multiplier:.2f}x multiplier):**")
            st.text(nutrition_analyzer.get_nutrition_facts(multiplied_nutrition))
            
            # Save meal
            if st.button("Save This Meal", use_container_width=True):
                meal_data = {
                    "user_id": st.session_state.user_id,
                    "meal_name": analysis.get('meal_name', 'Unknown'),
                    "description": analysis.get('description', ''),
                    "meal_type": meal_type,
                    "nutrition": multiplied_nutrition,
                    "portion_multiplier": portion_multiplier,
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
                        # Store analysis in session state
                        st.session_state.photo_analysis = analysis
                        st.session_state.photo_meal_type = meal_type
                        st.success("✅ Photo analyzed!")
                    else:
                        st.error("❌ Could not analyze photo. Please try again.")
        
        # Display analysis if it exists in session state
        if "photo_analysis" in st.session_state:
            analysis = st.session_state.photo_analysis
            meal_type = st.session_state.photo_meal_type
            
            # Display detected foods
            st.markdown("### Detected Foods")
            for food in analysis.get('detected_foods', []):
                st.write(f"- {food['name']} ({food['quantity']})")
            
            # Display nutrition
            st.text(nutrition_analyzer.get_nutrition_facts(analysis['total_nutrition']))
            
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
            
            # Portion size multiplier
            st.markdown("### 📏 Portion Size")
            portion_multiplier = st.selectbox(
                "How much did you eat?",
                options=[0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0],
                index=2,
                format_func=lambda x: f"{x:.2f}x" if x != 1.0 else "1x (Normal portion)",
                key="photo_portion_mult"
            )
            
            # Apply multiplier to nutrition and display
            multiplied_nutrition = {k: v * portion_multiplier for k, v in analysis['total_nutrition'].items()}
            st.info(f"**Nutrition (with {portion_multiplier:.2f}x multiplier):**")
            st.text(nutrition_analyzer.get_nutrition_facts(multiplied_nutrition))
            
            # Save meal
            if st.button("Save This Meal", use_container_width=True, key="save_photo_meal"):
                meal_data = {
                    "user_id": st.session_state.user_id,
                    "meal_name": f"Meal from photo",
                    "description": ", ".join([f"{f['name']} ({f['quantity']})" for f in analysis.get('detected_foods', [])]),
                    "meal_type": meal_type,
                    "nutrition": multiplied_nutrition,
                    "portion_multiplier": portion_multiplier,
                    "healthiness_score": 75,  # Default score
                    "health_notes": analysis.get('notes', ''),
                    "logged_at": datetime.combine(meal_date, time(12, 0, 0)).isoformat(),
                }
                
                if db_manager.log_meal(meal_data):
                    st.success("✅ Meal saved successfully!")
                    # Clear the analysis from session state
                    del st.session_state.photo_analysis
                    del st.session_state.photo_meal_type
                    st.rerun()
                else:
                    st.error("❌ Failed to save meal")


def analytics_page():
    """Analytics and insights page"""
    st.markdown("# 📈 Analytics & Insights")
    
    user_profile = st.session_state.user_profile
    if not user_profile:
        user_profile = db_manager.get_health_profile(st.session_state.user_id)
        if not user_profile:
            st.info("Please complete your profile first!")
            return
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        days = st.slider("Select time period", 1, 30, 7, help="Days to analyze")
    
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
    
    # ===== Statistics =====
    st.markdown("## 📉 Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_cal = df["calories"].mean() if len(df) > 0 else 0
        st.metric("Avg. Daily Calories", f"{avg_cal:.0f}", f"Target: {targets['calories']}")
    
    with col2:
        total_meals = len(meals)
        st.metric("Total Meals", total_meals)
    
    with col3:
        avg_meals_per_day = total_meals / days if days > 0 else 0
        st.metric("Avg. Meals/Day", f"{avg_meals_per_day:.1f}")
    
    with col4:
        avg_protein = df["protein"].mean() if len(df) > 0 else 0
        st.metric("Avg. Protein", f"{avg_protein:.1f}g", f"Target: {targets['protein']}g")
    
    # ===== Streaks & Badges =====
    st.markdown("## 🏆 Achievements")
    
    meal_dates = [datetime.fromisoformat(m.get("logged_at", "")) for m in meals]
    streak_info = get_streak_info(meal_dates)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("🔥 Current Streak", f"{streak_info['current_streak']} days")
    
    with col2:
        st.metric("🏅 Longest Streak", f"{streak_info['longest_streak']} days")
    
    # Display earned badges
    if user_profile.get("badges_earned"):
        st.markdown("### Earned Badges")
        badges_earned = get_earned_badges(user_profile.get("badges_earned", []))
        badge_cols = st.columns(len(badges_earned))
        
        for idx, (badge_id, badge_info) in enumerate(badges_earned.items()):
            with badge_cols[idx]:
                st.write(f"{badge_info.get('icon', '🏆')} **{badge_info.get('name', 'Badge')}'**")
                st.caption(badge_info.get('description', ''))


def insights_page():
    """Health insights and recommendations page"""
    st.markdown("# 💡 Health Insights & Recommendations")
    
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
                        
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.text(nutrition_analyzer.get_nutrition_facts(rec.get('estimated_nutrition', {})))
                        
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
    st.markdown("# 📋 Meal History")
    
    user_id = st.session_state.user_id
    
    # Date range filters
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
    
    with col2:
        end_date = st.date_input("End Date", value=date.today())
    
    with col3:
        if st.button("📊 Search", use_container_width=True):
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
            col1, col2, col3, col4 = st.columns([2, 0.5, 0.5, 0.5])
            
            with col1:
                st.write(f"🍴 **{meal.get('meal_name', 'Unknown')}** - {meal.get('meal_type', 'meal')}")
                st.caption(f"📅 {meal.get('logged_at', 'N/A')}")
            
            with col2:
                if st.button("Edit", key=f"edit_hist_{meal['id']}", use_container_width=True):
                    st.session_state[f"edit_meal_id_{meal['id']}"] = True
            
            with col3:
                portion = st.number_input(
                    f"Portion",
                    value=1.0,
                    min_value=0.1,
                    max_value=5.0,
                    step=0.1,
                    key=f"portion_hist_{meal['id']}",
                    help="Portion multiplier"
                )
            
            with col4:
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
                multiplied_nutrition = {k: v * portion for k, v in nutrition.items()}
                st.text(nutrition_analyzer.get_nutrition_facts(multiplied_nutrition))
            
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
                    
                    if st.form_submit_button("Save Changes", use_container_width=True):
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
            
            st.divider()


def profile_page():
    """User profile and health settings page"""
    st.markdown("# 👤 My Profile")
    
    user_email = st.session_state.user_email
    
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


# ==================== MAIN APP ====================

def main():
    """Main app logic"""
    
    if not is_authenticated():
        login_page()
    else:
        # Sidebar navigation
        st.sidebar.markdown(f"# 🥗 {APP_NAME}")
        st.sidebar.markdown("---")
        
        if st.session_state.user_email:
            st.sidebar.markdown(f"**Logged in as:**\n{st.session_state.user_email}")
            st.sidebar.markdown("---")
        
        # Navigation
        pages = {
            "Dashboard": "📊",
            "Log Meal": "📝",
            "Analytics": "📈",
            "Meal History": "📋",
            "Insights": "💡",
            "My Profile": "👤",
        }
        
        # Check if quick navigation was triggered
        default_page = "Log Meal" if st.session_state.get("quick_nav_to_meal") else "Dashboard"
        
        selected_page = st.sidebar.radio(
            "Navigation",
            options=list(pages.keys()),
            index=list(pages.keys()).index(default_page),
            format_func=lambda x: f"{pages[x]} {x}"
        )
        
        # Clear the quick nav flag
        if st.session_state.get("quick_nav_to_meal"):
            st.session_state.quick_nav_to_meal = False
        
        st.sidebar.markdown("---")
        
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            auth_manager.logout()
            st.session_state.clear()
            st.success("✅ Logged out!")
            st.rerun()
        
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


if __name__ == "__main__":
    main()
