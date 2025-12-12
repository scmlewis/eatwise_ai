"""Nutrition Analysis Module for EatWise"""
import json
import logging
from typing import Dict, List, Tuple, Optional
from openai import AzureOpenAI
from openai import APIError, RateLimitError, APIConnectionError
import streamlit as st
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT
import base64
from io import BytesIO
from utils import sanitize_user_input, get_user_friendly_error

logger = logging.getLogger(__name__)


class NutritionAnalyzer:
    """Analyzes food items and provides nutritional information using Azure OpenAI"""
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version="2023-05-15",
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        # Common food nutrition database (fallback)
        self.food_database = self._load_food_database()
    
    def _load_food_database(self) -> Dict:
        """Load common food nutrition data (per 100g serving, USDA-based)"""
        return {
            # Proteins
            "chicken breast": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6, "sodium": 74, "sugar": 0, "fiber": 0},
            "chicken thigh": {"calories": 209, "protein": 26, "carbs": 0, "fat": 11, "sodium": 81, "sugar": 0, "fiber": 0},
            "ground beef": {"calories": 250, "protein": 26, "carbs": 0, "fat": 15, "sodium": 75, "sugar": 0, "fiber": 0},
            "salmon": {"calories": 280, "protein": 25, "carbs": 0, "fat": 20, "sodium": 75, "sugar": 0, "fiber": 0},
            "tuna": {"calories": 132, "protein": 29, "carbs": 0, "fat": 1.3, "sodium": 41, "sugar": 0, "fiber": 0},
            "tilapia": {"calories": 96, "protein": 20, "carbs": 0, "fat": 1.7, "sodium": 81, "sugar": 0, "fiber": 0},
            "egg": {"calories": 78, "protein": 6.3, "carbs": 0.6, "fat": 5.3, "sodium": 70, "sugar": 0.4, "fiber": 0},
            "tofu": {"calories": 76, "protein": 8.1, "carbs": 1.9, "fat": 4.8, "sodium": 7, "sugar": 0.3, "fiber": 1.2},
            "greek yogurt": {"calories": 59, "protein": 10, "carbs": 3.3, "fat": 0.4, "sodium": 41, "sugar": 0.7, "fiber": 0},
            "cottage cheese": {"calories": 98, "protein": 11, "carbs": 3.4, "fat": 5, "sodium": 390, "sugar": 0.3, "fiber": 0},
            "turkey": {"calories": 135, "protein": 29, "carbs": 0, "fat": 1, "sodium": 50, "sugar": 0, "fiber": 0},
            "pork chops": {"calories": 242, "protein": 27, "carbs": 0, "fat": 14, "sodium": 70, "sugar": 0, "fiber": 0},
            "beef steak": {"calories": 271, "protein": 26, "carbs": 0, "fat": 18, "sodium": 59, "sugar": 0, "fiber": 0},
            "shrimp": {"calories": 99, "protein": 24, "carbs": 0.2, "fat": 0.3, "sodium": 148, "sugar": 0, "fiber": 0},
            "lentils": {"calories": 116, "protein": 9, "carbs": 20, "fat": 0.4, "sodium": 2, "sugar": 2, "fiber": 7.9},
            "chickpeas": {"calories": 164, "protein": 8.9, "carbs": 27, "fat": 2.6, "sodium": 7, "sugar": 5.2, "fiber": 6.4},
            "black beans": {"calories": 132, "protein": 8.9, "carbs": 24, "fat": 0.5, "sodium": 2, "sugar": 0.3, "fiber": 8.7},
            
            # Grains & Carbs
            "white rice": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3, "sodium": 2, "sugar": 0, "fiber": 0.4},
            "brown rice": {"calories": 111, "protein": 2.6, "carbs": 23, "fat": 0.9, "sodium": 10, "sugar": 0.3, "fiber": 1.8},
            "pasta": {"calories": 131, "protein": 5, "carbs": 25, "fat": 1.1, "sodium": 1, "sugar": 1, "fiber": 1.5},
            "oats": {"calories": 389, "protein": 16.9, "carbs": 66.3, "fat": 6.9, "sodium": 30, "sugar": 0, "fiber": 10.6},
            "bread": {"calories": 80, "protein": 3, "carbs": 14, "fat": 1, "sodium": 140, "sugar": 2, "fiber": 2},
            "whole wheat bread": {"calories": 81, "protein": 4, "carbs": 14, "fat": 1.5, "sodium": 380, "sugar": 1.5, "fiber": 2.4},
            "cereal": {"calories": 150, "protein": 3, "carbs": 30, "fat": 2, "sodium": 190, "sugar": 12, "fiber": 2},
            "quinoa": {"calories": 120, "protein": 4.4, "carbs": 21.3, "fat": 1.9, "sodium": 7, "sugar": 1.6, "fiber": 2.8},
            "sweet potato": {"calories": 86, "protein": 1.6, "carbs": 20, "fat": 0.1, "sodium": 55, "sugar": 4.2, "fiber": 3},
            "white potato": {"calories": 77, "protein": 2.1, "carbs": 17, "fat": 0.1, "sodium": 6, "sugar": 0.8, "fiber": 2.1},
            "corn": {"calories": 86, "protein": 3.3, "carbs": 19, "fat": 1.2, "sodium": 15, "sugar": 3, "fiber": 2.4},
            
            # Vegetables
            "broccoli": {"calories": 34, "protein": 2.8, "carbs": 7, "fat": 0.4, "sodium": 64, "sugar": 1.4, "fiber": 2.4},
            "spinach": {"calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4, "sodium": 79, "sugar": 0.4, "fiber": 2.2},
            "kale": {"calories": 49, "protein": 4.3, "carbs": 9, "fat": 0.9, "sodium": 90, "sugar": 0.9, "fiber": 3.6},
            "carrots": {"calories": 41, "protein": 0.9, "carbs": 10, "fat": 0.2, "sodium": 69, "sugar": 4.7, "fiber": 2.8},
            "tomato": {"calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2, "sodium": 5, "sugar": 2.6, "fiber": 1.2},
            "cucumber": {"calories": 16, "protein": 0.7, "carbs": 3.6, "fat": 0.1, "sodium": 2, "sugar": 1.7, "fiber": 0.5},
            "lettuce": {"calories": 15, "protein": 1.2, "carbs": 3, "fat": 0.3, "sodium": 23, "sugar": 0.5, "fiber": 0.6},
            "bell pepper": {"calories": 31, "protein": 1, "carbs": 6, "fat": 0.3, "sodium": 2, "sugar": 3.2, "fiber": 2.2},
            "onion": {"calories": 40, "protein": 1.1, "carbs": 9, "fat": 0.1, "sodium": 4, "sugar": 4.2, "fiber": 1.7},
            "garlic": {"calories": 149, "protein": 6.4, "carbs": 33, "fat": 0.5, "sodium": 17, "sugar": 1, "fiber": 2.1},
            "peas": {"calories": 81, "protein": 5.4, "carbs": 14, "fat": 0.4, "sodium": 5, "sugar": 5.7, "fiber": 2.8},
            "beans": {"calories": 127, "protein": 8.7, "carbs": 23, "fat": 0.4, "sodium": 6, "sugar": 3.5, "fiber": 6.4},
            "salad": {"calories": 15, "protein": 1.2, "carbs": 3, "fat": 0.3, "sodium": 23, "sugar": 0.5, "fiber": 0.6},
            
            # Fruits
            "apple": {"calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2, "sodium": 1, "sugar": 10, "fiber": 2.4},
            "banana": {"calories": 89, "protein": 1.1, "carbs": 23, "fat": 0.3, "sodium": 1, "sugar": 12, "fiber": 2.6},
            "orange": {"calories": 47, "protein": 0.9, "carbs": 12, "fat": 0.3, "sodium": 0, "sugar": 9.4, "fiber": 2.4},
            "strawberry": {"calories": 32, "protein": 0.8, "carbs": 8, "fat": 0.3, "sodium": 2, "sugar": 4.9, "fiber": 2},
            "blueberry": {"calories": 57, "protein": 0.7, "carbs": 14, "fat": 0.3, "sodium": 1, "sugar": 10, "fiber": 2.4},
            "watermelon": {"calories": 30, "protein": 0.6, "carbs": 8, "fat": 0.2, "sodium": 1, "sugar": 6, "fiber": 0.4},
            "grape": {"calories": 67, "protein": 0.7, "carbs": 17, "fat": 0.2, "sodium": 2, "sugar": 16, "fiber": 0.9},
            "mango": {"calories": 60, "protein": 0.8, "carbs": 15, "fat": 0.4, "sodium": 11, "sugar": 13.7, "fiber": 1.6},
            "pineapple": {"calories": 50, "protein": 0.5, "carbs": 13, "fat": 0.1, "sodium": 1, "sugar": 9.9, "fiber": 1.4},
            "peach": {"calories": 39, "protein": 0.9, "carbs": 10, "fat": 0.3, "sodium": 0, "sugar": 8.4, "fiber": 1.5},
            "pear": {"calories": 57, "protein": 0.4, "carbs": 15, "fat": 0.1, "sodium": 1, "sugar": 9.8, "fiber": 3.1},
            "avocado": {"calories": 160, "protein": 2, "carbs": 9, "fat": 15, "sodium": 7, "sugar": 0.7, "fiber": 7},
            
            # Dairy
            "milk": {"calories": 61, "protein": 3.2, "carbs": 4.8, "fat": 3.3, "sodium": 44, "sugar": 4.8, "fiber": 0},
            "skim milk": {"calories": 35, "protein": 3.6, "carbs": 5, "fat": 0.1, "sodium": 50, "sugar": 5, "fiber": 0},
            "cheese": {"calories": 402, "protein": 25, "carbs": 1.3, "fat": 33, "sodium": 621, "sugar": 0, "fiber": 0},
            "cheddar cheese": {"calories": 403, "protein": 23, "carbs": 3.6, "fat": 33, "sodium": 620, "sugar": 0.7, "fiber": 0},
            "butter": {"calories": 717, "protein": 0.9, "carbs": 0.1, "fat": 81, "sodium": 11, "sugar": 0, "fiber": 0},
            "yogurt": {"calories": 59, "protein": 10, "carbs": 3.3, "fat": 0.4, "sodium": 41, "sugar": 0.7, "fiber": 0},
            
            # Oils & Fats
            "olive oil": {"calories": 884, "protein": 0, "carbs": 0, "fat": 100, "sodium": 0, "sugar": 0, "fiber": 0},
            "coconut oil": {"calories": 892, "protein": 0, "carbs": 0, "fat": 99.1, "sodium": 0, "sugar": 0, "fiber": 0},
            "peanut butter": {"calories": 588, "protein": 25, "carbs": 20, "fat": 50, "sodium": 421, "sugar": 5.9, "fiber": 6},
            
            # Nuts & Seeds
            "almonds": {"calories": 579, "protein": 21, "carbs": 22, "fat": 50, "sodium": 1, "sugar": 4.4, "fiber": 12.5},
            "walnuts": {"calories": 654, "protein": 9, "carbs": 14, "fat": 65, "sodium": 2, "sugar": 2.6, "fiber": 6.7},
            "peanuts": {"calories": 567, "protein": 26, "carbs": 16, "fat": 49, "sodium": 7, "sugar": 4.7, "fiber": 8.6},
            "sunflower seeds": {"calories": 584, "protein": 20, "carbs": 20, "fat": 51, "sodium": 9, "sugar": 2.6, "fiber": 8.6},
            
            # Processed Foods (common)
            "pizza": {"calories": 285, "protein": 12, "carbs": 36, "fat": 10, "sodium": 640, "sugar": 4, "fiber": 2},
            "burger": {"calories": 354, "protein": 16, "carbs": 32, "fat": 17, "sodium": 580, "sugar": 6, "fiber": 1.5},
            "chicken nuggets": {"calories": 320, "protein": 17, "carbs": 24, "fat": 17, "sodium": 560, "sugar": 2, "fiber": 0.5},
            "french fries": {"calories": 365, "protein": 3.4, "carbs": 48, "fat": 17, "sodium": 246, "sugar": 0.3, "fiber": 4},
            "donut": {"calories": 452, "protein": 4.5, "carbs": 51, "fat": 25, "sodium": 210, "sugar": 33, "fiber": 0.7},
            "chocolate": {"calories": 546, "protein": 5.3, "carbs": 57, "fat": 31, "sodium": 11, "sugar": 50, "fiber": 7.2},
            
            # Beverages (per serving approximation)
            "coca cola": {"calories": 42, "protein": 0, "carbs": 11, "fat": 0, "sodium": 11, "sugar": 10.6, "fiber": 0},
            "orange juice": {"calories": 45, "protein": 0.7, "carbs": 11, "fat": 0.25, "sodium": 1, "sugar": 9.3, "fiber": 0.2},
            "coffee": {"calories": 2, "protein": 0.3, "carbs": 0, "fat": 0, "sodium": 5, "sugar": 0, "fiber": 0},
            "tea": {"calories": 1, "protein": 0, "carbs": 0.3, "fat": 0, "sodium": 1, "sugar": 0, "fiber": 0},
            "beer": {"calories": 43, "protein": 0.5, "carbs": 3.6, "fat": 0, "sodium": 10, "sugar": 0, "fiber": 0},
            "wine": {"calories": 82, "protein": 0.1, "carbs": 2.6, "fat": 0, "sodium": 4, "sugar": 0.6, "fiber": 0},
            
            # Additional Proteins
            "cod": {"calories": 82, "protein": 18, "carbs": 0, "fat": 0.7, "sodium": 54, "sugar": 0, "fiber": 0},
            "halibut": {"calories": 111, "protein": 21, "carbs": 0, "fat": 2.3, "sodium": 79, "sugar": 0, "fiber": 0},
            "mackerel": {"calories": 305, "protein": 25, "carbs": 0, "fat": 22, "sodium": 71, "sugar": 0, "fiber": 0},
            "crab": {"calories": 82, "protein": 18, "carbs": 0, "fat": 1.1, "sodium": 265, "sugar": 0, "fiber": 0},
            "lobster": {"calories": 89, "protein": 19, "carbs": 0.5, "fat": 0.9, "sodium": 288, "sugar": 0, "fiber": 0},
            "lamb chops": {"calories": 294, "protein": 25, "carbs": 0, "fat": 21, "sodium": 76, "sugar": 0, "fiber": 0},
            "veal": {"calories": 172, "protein": 29, "carbs": 0, "fat": 5.8, "sodium": 93, "sugar": 0, "fiber": 0},
            "duck": {"calories": 337, "protein": 16, "carbs": 0, "fat": 30, "sodium": 75, "sugar": 0, "fiber": 0},
            
            # Additional Grains
            "barley": {"calories": 123, "protein": 2.3, "carbs": 28, "fat": 0.4, "sodium": 7, "sugar": 0.8, "fiber": 3.8},
            "rye": {"calories": 338, "protein": 10, "carbs": 70, "fat": 1.6, "sodium": 2, "sugar": 1.5, "fiber": 15.1},
            "couscous": {"calories": 112, "protein": 3.8, "carbs": 23, "fat": 0.3, "sodium": 8, "sugar": 0.3, "fiber": 1.5},
            "buckwheat": {"calories": 343, "protein": 13, "carbs": 71, "fat": 3.4, "sodium": 1, "sugar": 1.7, "fiber": 10},
            "millet": {"calories": 378, "protein": 11, "carbs": 72, "fat": 4.2, "sodium": 5, "sugar": 3, "fiber": 8.5},
            "farro": {"calories": 335, "protein": 14, "carbs": 68, "fat": 2.4, "sodium": 6, "sugar": 0, "fiber": 10},
            
            # Additional Vegetables
            "cauliflower": {"calories": 25, "protein": 1.9, "carbs": 5, "fat": 0.3, "sodium": 30, "sugar": 1.9, "fiber": 2},
            "cabbage": {"calories": 25, "protein": 1.3, "carbs": 6, "fat": 0.1, "sodium": 16, "sugar": 3.2, "fiber": 2.3},
            "brussels sprouts": {"calories": 43, "protein": 3.4, "carbs": 8, "fat": 0.4, "sodium": 25, "sugar": 2.2, "fiber": 2.4},
            "zucchini": {"calories": 21, "protein": 1.5, "carbs": 3.5, "fat": 0.4, "sodium": 10, "sugar": 1.2, "fiber": 1},
            "eggplant": {"calories": 25, "protein": 1, "carbs": 6, "fat": 0.2, "sodium": 2, "sugar": 3.5, "fiber": 3},
            "asparagus": {"calories": 27, "protein": 2.2, "carbs": 5, "fat": 0.1, "sodium": 2, "sugar": 1.9, "fiber": 2.1},
            "green beans": {"calories": 31, "protein": 1.8, "carbs": 7, "fat": 0.2, "sodium": 2, "sugar": 1.6, "fiber": 3.4},
            "artichoke": {"calories": 47, "protein": 3.3, "carbs": 10, "fat": 0.1, "sodium": 66, "sugar": 0.7, "fiber": 5},
            "radish": {"calories": 16, "protein": 0.7, "carbs": 3.4, "fat": 0.1, "sodium": 39, "sugar": 1.9, "fiber": 1.6},
            "celery": {"calories": 16, "protein": 0.7, "carbs": 3.7, "fat": 0.2, "sodium": 80, "sugar": 1.6, "fiber": 1.6},
            "beet": {"calories": 43, "protein": 1.6, "carbs": 10, "fat": 0.2, "sodium": 78, "sugar": 7, "fiber": 2.8},
            
            # Additional Fruits
            "kiwi": {"calories": 61, "protein": 1.1, "carbs": 15, "fat": 0.5, "sodium": 3, "sugar": 6.2, "fiber": 3},
            "papaya": {"calories": 43, "protein": 0.5, "carbs": 11, "fat": 0.3, "sodium": 8, "sugar": 7.9, "fiber": 1.8},
            "coconut": {"calories": 354, "protein": 3.3, "carbs": 9, "fat": 33, "sodium": 20, "sugar": 9, "fiber": 9},
            "lemon": {"calories": 29, "protein": 1.1, "carbs": 9, "fat": 0.3, "sodium": 1, "sugar": 2.5, "fiber": 2.8},
            "lime": {"calories": 30, "protein": 0.7, "carbs": 11, "fat": 0.2, "sodium": 2, "sugar": 1.7, "fiber": 2.8},
            "raspberry": {"calories": 52, "protein": 1.2, "carbs": 12, "fat": 0.7, "sodium": 1, "sugar": 4.4, "fiber": 6.5},
            "blackberry": {"calories": 43, "protein": 1.4, "carbs": 10, "fat": 0.5, "sodium": 2, "sugar": 4.9, "fiber": 5.3},
            "cranberry": {"calories": 46, "protein": 0.4, "carbs": 12, "fat": 0.1, "sodium": 1, "sugar": 4, "fiber": 3.6},
            "grapefruit": {"calories": 42, "protein": 0.8, "carbs": 11, "fat": 0.1, "sodium": 0, "sugar": 7, "fiber": 1.6},
            "pomegranate": {"calories": 83, "protein": 1.7, "carbs": 19, "fat": 1.2, "sodium": 3, "sugar": 13.7, "fiber": 4},
            
            # Additional Dairy
            "mozzarella": {"calories": 280, "protein": 28, "carbs": 3.1, "fat": 17, "sodium": 506, "sugar": 0.7, "fiber": 0},
            "feta cheese": {"calories": 264, "protein": 14, "carbs": 4.1, "fat": 21, "sodium": 1116, "sugar": 4.1, "fiber": 0},
            "ricotta cheese": {"calories": 174, "protein": 11, "carbs": 3.1, "fat": 13, "sodium": 207, "sugar": 0.3, "fiber": 0},
            "sour cream": {"calories": 193, "protein": 3.6, "carbs": 3.8, "fat": 19, "sodium": 50, "sugar": 4, "fiber": 0},
            "whipped cream": {"calories": 340, "protein": 2.2, "carbs": 2.6, "fat": 36, "sodium": 41, "sugar": 2.6, "fiber": 0},
            
            # Additional Nuts
            "cashews": {"calories": 553, "protein": 18, "carbs": 30, "fat": 44, "sodium": 12, "sugar": 5.9, "fiber": 3.3},
            "macadamia": {"calories": 718, "protein": 7.9, "carbs": 14, "fat": 76, "sodium": 5, "sugar": 4.6, "fiber": 8.6},
            "pecans": {"calories": 691, "protein": 9, "carbs": 14, "fat": 71, "sodium": 0, "sugar": 3.9, "fiber": 8.7},
            "brazil nuts": {"calories": 656, "protein": 14, "carbs": 12, "fat": 66, "sodium": 3, "sugar": 2.3, "fiber": 6.3},
            "sesame seeds": {"calories": 565, "protein": 17, "carbs": 23, "fat": 50, "sodium": 11, "sugar": 0.3, "fiber": 11.8},
            "pumpkin seeds": {"calories": 446, "protein": 19, "carbs": 4, "fat": 40, "sodium": 4, "sugar": 1.1, "fiber": 1.7},
            
            # Seafood variants
            "clams": {"calories": 74, "protein": 13, "carbs": 2.6, "fat": 1, "sodium": 127, "sugar": 0, "fiber": 0},
            "mussels": {"calories": 172, "protein": 24, "carbs": 7.4, "fat": 4.5, "sodium": 286, "sugar": 0, "fiber": 0},
            "oysters": {"calories": 68, "protein": 7, "carbs": 4, "fat": 2, "sodium": 180, "sugar": 0, "fiber": 0},
            "squid": {"calories": 92, "protein": 16, "carbs": 3.1, "fat": 1.4, "sodium": 44, "sugar": 0, "fiber": 0},
            
            # Additional processed/snacks
            "pretzel": {"calories": 380, "protein": 9.2, "carbs": 80, "fat": 3.5, "sodium": 1050, "sugar": 3, "fiber": 2.5},
            "popcorn": {"calories": 386, "protein": 12, "carbs": 77, "fat": 4.3, "sodium": 98, "sugar": 1.3, "fiber": 15},
            "crackers": {"calories": 402, "protein": 8.5, "carbs": 77, "fat": 8.8, "sodium": 760, "sugar": 2, "fiber": 2},
            "cookies": {"calories": 492, "protein": 6, "carbs": 66, "fat": 23, "sodium": 400, "sugar": 38, "fiber": 0.5},
            "granola": {"calories": 471, "protein": 13, "carbs": 61, "fat": 20, "sodium": 8, "sugar": 19, "fiber": 6},
        }
    
    def analyze_text_meal(self, meal_description: str, meal_type: str = "meal") -> Optional[Dict]:
        """
        Analyze meal from text description using OpenAI
        
        Args:
            meal_description: Text description of the meal
            meal_type: Type of meal (breakfast, lunch, dinner, snack)
            
        Returns:
            Dictionary with meal info and nutrition data
        """
        try:
            # Sanitize user input before sending to OpenAI
            meal_description = sanitize_user_input(meal_description, max_length=500)
            meal_type = sanitize_user_input(meal_type, max_length=50)
            
            prompt = f"""Analyze the following meal description and provide nutritional information.
            
Meal: {meal_description}
Meal Type: {meal_type}

Please provide the response in JSON format with the following structure:
{{
    "meal_name": "name of the meal",
    "description": "brief description",
    "meal_type": "{meal_type}",
    "servings": 1,
    "nutrition": {{
        "calories": estimated calories,
        "protein": grams,
        "carbs": grams,
        "fat": grams,
        "sodium": mg,
        "sugar": grams,
        "fiber": grams
    }},
    "ingredients": ["ingredient1", "ingredient2", ...],
    "healthiness_score": 0-100,
    "health_notes": "brief health notes"
}}

Provide realistic estimates based on typical portion sizes."""
            
            response = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a nutrition expert. Analyze meals and provide accurate nutritional information in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )
            
            # Parse response
            try:
                analysis = json.loads(response.choices[0].message.content)
                return analysis
            except json.JSONDecodeError:
                # If JSON parsing fails, extract JSON from response
                content = response.choices[0].message.content
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    analysis = json.loads(content[start_idx:end_idx])
                    return analysis
                return None
        
        except RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            st.error("Too many requests. Please wait a moment and try again.")
            return None
        except APIConnectionError as e:
            logger.error(f"OpenAI connection error: {e}")
            st.error("Connection error with AI service. Please check your internet connection.")
            return None
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            st.error(f"AI service error: {get_user_friendly_error(e)}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            st.error("Failed to parse nutrition data. Please try again.")
            return None
        except Exception as e:
            logger.error(f"Unexpected error analyzing meal: {type(e).__name__}: {e}")
            st.error(f"Error analyzing meal: {get_user_friendly_error(e)}")
            return None
    
    def analyze_food_image(self, image_data: bytes) -> Optional[Dict]:
        """
        Analyze food from image using OpenAI Vision (GPT-4V)
        
        Args:
            image_data: Image bytes
            
        Returns:
            Dictionary with detected foods and nutrition info
        """
        try:
            # Convert image to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            prompt = """Analyze this food image and identify the main food items and their approximate quantities.
            
Please provide the response in JSON format:
{
    "detected_foods": [
        {
            "name": "food name",
            "quantity": "estimated amount",
            "nutrition": {
                "calories": estimated,
                "protein": grams,
                "carbs": grams,
                "fat": grams,
                "sodium": mg,
                "sugar": grams,
                "fiber": grams
            }
        }
    ],
    "meal_type": "breakfast/lunch/dinner/snack",
    "total_nutrition": {
        "calories": total,
        "protein": total,
        "carbs": total,
        "fat": total,
        "sodium": total,
        "sugar": total,
        "fiber": total
    },
    "confidence": 0-100,
    "notes": "any relevant notes"
}"""
            
            response = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.5,
                max_tokens=800
            )
            
            try:
                analysis = json.loads(response.choices[0].message.content)
                return analysis
            except json.JSONDecodeError:
                content = response.choices[0].message.content
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    analysis = json.loads(content[start_idx:end_idx])
                    return analysis
                return None
        
        except Exception as e:
            st.error(f"Error analyzing image: {str(e)}")
            return None
    
    def get_nutrition_for_food(self, food_name: str, quantity: float = 1) -> Optional[Dict]:
        """
        Get nutrition info for a specific food item
        
        Args:
            food_name: Name of the food
            quantity: Quantity multiplier
            
        Returns:
            Nutrition dictionary
        """
        food_name_lower = food_name.lower()
        
        # Check local database first
        for db_food, nutrition in self.food_database.items():
            if db_food in food_name_lower or food_name_lower in db_food:
                return {k: v * quantity for k, v in nutrition.items()}
        
        # If not found, ask OpenAI
        try:
            response = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a nutrition expert. Provide accurate nutrition information."},
                    {"role": "user", "content": f"What is the nutritional information for 100g of {food_name}? Provide as JSON: {{\"calories\": number, \"protein\": number, \"carbs\": number, \"fat\": number, \"sodium\": number, \"sugar\": number, \"fiber\": number}}"}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            try:
                nutrition = json.loads(response.choices[0].message.content)
                return {k: v * quantity for k, v in nutrition.items()}
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse nutrition JSON for {food_name}: {e}")
                return None
        
        except Exception as e:
            return None
    
    def suggest_healthier_alternative(self, meal_name: str) -> Optional[str]:
        """
        Suggest a healthier alternative for a meal
        
        Args:
            meal_name: Name of the meal
            
        Returns:
            Suggestion text
        """
        try:
            response = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a nutrition expert providing helpful meal alternatives."},
                    {"role": "user", "content": f"What would be a healthier alternative to {meal_name}? Keep it brief and practical."}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return None
    
    def get_nutrition_facts(self, nutrition_data: Dict) -> str:
        """
        Format nutrition data as readable nutrition facts
        
        Args:
            nutrition_data: Nutrition dictionary
            
        Returns:
            Formatted nutrition facts string
        """
        facts = f"""
        📊 NUTRITION FACTS
        ─────────────────
        Calories: {nutrition_data.get('calories', 0):.0f} kcal
        Protein: {nutrition_data.get('protein', 0):.1f}g
        Carbs: {nutrition_data.get('carbs', 0):.1f}g
        Fat: {nutrition_data.get('fat', 0):.1f}g
        Fiber: {nutrition_data.get('fiber', 0):.1f}g
        Sodium: {nutrition_data.get('sodium', 0):.0f}mg
        Sugar: {nutrition_data.get('sugar', 0):.1f}g
        """
        return facts.strip()
    
    def get_nutrition_facts_html(self, nutrition_data: Dict) -> str:
        """
        Format nutrition data as an HTML card with modern styling
        
        Args:
            nutrition_data: Nutrition dictionary
            
        Returns:
            Formatted HTML nutrition facts card
        """
        calories = nutrition_data.get('calories', 0)
        protein = nutrition_data.get('protein', 0)
        carbs = nutrition_data.get('carbs', 0)
        fat = nutrition_data.get('fat', 0)
        fiber = nutrition_data.get('fiber', 0)
        sodium = nutrition_data.get('sodium', 0)
        sugar = nutrition_data.get('sugar', 0)
        
        html = f"""<div style="background: linear-gradient(135deg, #10A19D15 0%, #52C4B825 100%); border: 2px solid #10A19D; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(16, 161, 157, 0.15);">
<div style="font-size: 14px; font-weight: bold; color: #52C4B8; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 0.5px;">📊 Nutrition Facts</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px;">
<div style="background: linear-gradient(135deg, #FF6B1620 0%, #FF6B1640 100%); border-radius: 8px; padding: 12px; border-left: 3px solid #FF6B16;">
<div style="font-size: 11px; color: #a0a0a0; text-transform: uppercase; font-weight: 600; margin-bottom: 4px;">🔥 Calories</div>
<div style="font-size: 18px; font-weight: bold; color: #e0f2f1;">{calories:.0f} kcal</div>
</div>
<div style="background: linear-gradient(135deg, #51CF6620 0%, #80C34240 100%); border-radius: 8px; padding: 12px; border-left: 3px solid #51CF66;">
<div style="font-size: 11px; color: #a0a0a0; text-transform: uppercase; font-weight: 600; margin-bottom: 4px;">💪 Protein</div>
<div style="font-size: 18px; font-weight: bold; color: #e0f2f1;">{protein:.1f}g</div>
</div>
<div style="background: linear-gradient(135deg, #3B82F620 0%, #60A5FA40 100%); border-radius: 8px; padding: 12px; border-left: 3px solid #3B82F6;">
<div style="font-size: 11px; color: #a0a0a0; text-transform: uppercase; font-weight: 600; margin-bottom: 4px;">🍚 Carbs</div>
<div style="font-size: 18px; font-weight: bold; color: #e0f2f1;">{carbs:.1f}g</div>
</div>
<div style="background: linear-gradient(135deg, #FFA50020 0%, #FFB84D40 100%); border-radius: 8px; padding: 12px; border-left: 3px solid #FFA500;">
<div style="font-size: 11px; color: #a0a0a0; text-transform: uppercase; font-weight: 600; margin-bottom: 4px;">🫒 Fat</div>
<div style="font-size: 18px; font-weight: bold; color: #e0f2f1;">{fat:.1f}g</div>
</div>
<div style="background: linear-gradient(135deg, #845EF720 0%, #BE80FF40 100%); border-radius: 8px; padding: 12px; border-left: 3px solid #845EF7;">
<div style="font-size: 11px; color: #a0a0a0; text-transform: uppercase; font-weight: 600; margin-bottom: 4px;">🌾 Fiber</div>
<div style="font-size: 18px; font-weight: bold; color: #e0f2f1;">{fiber:.1f}g</div>
</div>
<div style="background: linear-gradient(135deg, #FF6B6B20 0%, #FF8A8A40 100%); border-radius: 8px; padding: 12px; border-left: 3px solid #FF6B6B;">
<div style="font-size: 11px; color: #a0a0a0; text-transform: uppercase; font-weight: 600; margin-bottom: 4px;">🧂 Sodium</div>
<div style="font-size: 18px; font-weight: bold; color: #e0f2f1;">{sodium:.0f}mg</div>
</div>
</div>
<div style="background: linear-gradient(135deg, #FFD43B20 0%, #FFC94D40 100%); border-radius: 8px; padding: 12px; border-left: 3px solid #FFD43B;">
<div style="font-size: 11px; color: #a0a0a0; text-transform: uppercase; font-weight: 600; margin-bottom: 4px;">🍬 Sugar</div>
<div style="font-size: 18px; font-weight: bold; color: #e0f2f1;">{sugar:.1f}g</div>
</div>
</div>"""
        return html
