import os
from dotenv import load_dotenv

load_dotenv()

# Validate critical environment variables
REQUIRED_ENV_VARS = {
    "SUPABASE_URL": os.getenv("SUPABASE_URL"),
    "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
    "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
    "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
}

missing_vars = [k for k, v in REQUIRED_ENV_VARS.items() if not v]
if missing_vars:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(missing_vars)}. "
        f"Please create a .env file with these values."
    )

# Supabase Configuration
SUPABASE_URL = REQUIRED_ENV_VARS["SUPABASE_URL"]
SUPABASE_KEY = REQUIRED_ENV_VARS["SUPABASE_KEY"]

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY = REQUIRED_ENV_VARS["AZURE_OPENAI_API_KEY"]
AZURE_OPENAI_ENDPOINT = REQUIRED_ENV_VARS["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-35-turbo")

# App Configuration
APP_NAME = "EatWise"
APP_DESCRIPTION = "AI-Powered Nutrition Hub"
DEBUG = os.getenv("DEBUG", "False") == "True"

# Nutrition Targets (Daily Recommendations)
DAILY_CALORIE_TARGET = 2000
DAILY_PROTEIN_TARGET = 50  # grams
DAILY_CARBS_TARGET = 300  # grams
DAILY_FAT_TARGET = 65  # grams
DAILY_SODIUM_TARGET = 2300  # mg
DAILY_SUGAR_TARGET = 50  # grams
DAILY_FIBER_TARGET = 25  # grams

# Age Group Recommendations (with personalized nutrition targets)
AGE_GROUP_TARGETS = {
    "13-19": {"calories": 2200, "protein": 59, "carbs": 300, "fat": 73, "sodium": 2300, "sugar": 50},
    "20-25": {"calories": 2400, "protein": 56, "carbs": 330, "fat": 80, "sodium": 2300, "sugar": 50},
    "26-35": {"calories": 2200, "protein": 50, "carbs": 300, "fat": 73, "sodium": 2300, "sugar": 50},
    "36-45": {"calories": 2000, "protein": 50, "carbs": 275, "fat": 65, "sodium": 2300, "sugar": 50},
    "46-55": {"calories": 1900, "protein": 50, "carbs": 260, "fat": 63, "sodium": 2300, "sugar": 50},
    "56-65": {"calories": 1800, "protein": 50, "carbs": 245, "fat": 60, "sodium": 2300, "sugar": 50},
    "65+": {"calories": 1600, "protein": 50, "carbs": 220, "fat": 53, "sodium": 2300, "sugar": 50},
}

# Health Condition Targets (Adjustments for specific medical conditions)
HEALTH_CONDITION_TARGETS = {
    "diabetes": {"calories": 1800, "carbs": 200, "sugar": 25, "fiber": 35},
    "hypertension": {"sodium": 1500},
    "heart_disease": {"sodium": 1500, "fat": 50},
    "lactose_intolerance": {},  # Handled via dietary restrictions
    "celiac_disease": {},  # Handled via dietary restrictions
}

# Health Goal Targets (Adjustments for specific health goals)
HEALTH_GOAL_TARGETS = {
    "general_health": {},  # No specific adjustments, use age group defaults
    "weight_loss": {"calories": 1500, "protein": 80},
    "weight_gain": {"calories": 3000, "protein": 100},
    "muscle_gain": {"calories": 2800, "protein": 120},
    "performance": {"calories": 2600, "protein": 100, "carbs": 400},
}
