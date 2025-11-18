"""Nutrition Analysis Module for EatWise"""
import json
from typing import Dict, List, Tuple, Optional
from openai import AzureOpenAI
import streamlit as st
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT
import base64
from io import BytesIO


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
        """Load common food nutrition data"""
        return {
            "rice": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3, "sodium": 2, "sugar": 0, "fiber": 0.4},
            "chicken breast": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6, "sodium": 74, "sugar": 0, "fiber": 0},
            "egg": {"calories": 78, "protein": 6.3, "carbs": 0.6, "fat": 5.3, "sodium": 70, "sugar": 0.4, "fiber": 0},
            "apple": {"calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2, "sodium": 1, "sugar": 10, "fiber": 2.4},
            "bread": {"calories": 80, "protein": 3, "carbs": 14, "fat": 1, "sodium": 140, "sugar": 2, "fiber": 2},
            "milk": {"calories": 61, "protein": 3.2, "carbs": 4.8, "fat": 3.3, "sodium": 44, "sugar": 4.8, "fiber": 0},
            "salad": {"calories": 15, "protein": 1.2, "carbs": 3, "fat": 0.3, "sodium": 23, "sugar": 0.5, "fiber": 0.6},
            "pasta": {"calories": 131, "protein": 5, "carbs": 25, "fat": 1.1, "sodium": 1, "sugar": 1, "fiber": 1.5},
            "salmon": {"calories": 280, "protein": 25, "carbs": 0, "fat": 20, "sodium": 75, "sugar": 0, "fiber": 0},
            "broccoli": {"calories": 34, "protein": 2.8, "carbs": 7, "fat": 0.4, "sodium": 64, "sugar": 1.4, "fiber": 2.4},
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
        
        except Exception as e:
            st.error(f"Error analyzing meal: {str(e)}")
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
            except:
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
