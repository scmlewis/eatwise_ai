"""Constants for EatWise Application"""

# Meal Types
MEAL_TYPES = {
    "breakfast": "🍳 Breakfast",
    "lunch": "🍽️ Lunch",
    "dinner": "🍲 Dinner",
    "snack": "🍎 Snack",
    "beverage": "🥤 Beverage",
}

# Health Conditions
HEALTH_CONDITIONS = {
    "diabetes": "Diabetes Management",
    "hypertension": "High Blood Pressure",
    "weight_loss": "Weight Loss Goal",
    "weight_gain": "Weight Gain Goal",
    "vegetarian": "Vegetarian",
    "vegan": "Vegan",
    "gluten_free": "Gluten Free",
    "nut_allergy": "Nut Allergy",
}

# Gamification
BADGES = {
    "early_bird": {"name": "Early Bird", "description": "Logged 5 breakfasts", "icon": "🌅"},
    "night_owl": {"name": "Night Owl", "description": "Logged 5 dinners", "icon": "🌙"},
    "streak_warrior": {"name": "Streak Warrior", "description": "7-day logging streak", "icon": "🔥"},
    "health_champion": {"name": "Health Champion", "description": "Met nutrition targets for 7 days", "icon": "🏆"},
    "foodie": {"name": "Foodie", "description": "Logged 50 meals", "icon": "👨‍🍳"},
    "sodium_watchdog": {"name": "Sodium Watchdog", "description": "5 days under sodium target", "icon": "👀"},
}

STREAK_MILESTONE_BADGES = [3, 7, 14, 30]  # 3-day, 7-day, 14-day, 30-day streaks

# Nutrition Benchmark Messages
BENCHMARK_MESSAGES = {
    "excellent": "🌟 Excellent! You nailed today's nutrition goals!",
    "good": "👍 Good job! You're on track.",
    "fair": "🟡 Fair. A few adjustments can help.",
    "needs_improvement": "⚠️ Needs improvement. Let's make better choices tomorrow.",
}

# Color Scheme
COLORS = {
    "primary": "#10A19D",
    "secondary": "#FF6B6B",
    "success": "#51CF66",
    "warning": "#FFA500",
    "danger": "#FF0000",
    "light_bg": "#F8F9FA",
    "dark_text": "#2C3E50",
}

# Localization (supports English and Chinese)
TRANSLATIONS = {
    "en": {
        "app_title": "EatWise - AI Nutrition Hub",
        "dashboard": "Dashboard",
        "meal_logging": "Log Meal",
        "analytics": "Analytics",
        "insights": "Insights",
        "profile": "My Profile",
        "logout": "Logout",
    },
    "zh": {
        "app_title": "EatWise - AI营养中心",
        "dashboard": "仪表板",
        "meal_logging": "记录餐食",
        "analytics": "分析",
        "insights": "洞察",
        "profile": "我的资料",
        "logout": "登出",
    },
}
