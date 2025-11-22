"""Restaurant Menu Analyzer Module for EatWise"""
import json
from typing import Dict, List, Optional
from openai import AzureOpenAI
import streamlit as st
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT


class RestaurantMenuAnalyzer:
    """Analyzes restaurant menus and provides healthiest options based on user profile"""
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version="2023-05-15",
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
    
    def analyze_menu(
        self,
        menu_text: str,
        user_profile: Dict,
        daily_nutrition: Dict,
        daily_targets: Dict
    ) -> Optional[Dict]:
        """
        Analyze restaurant menu and provide personalized recommendations
        
        Args:
            menu_text: Full restaurant menu text (pasted by user)
            user_profile: User health profile (age, conditions, preferences, goals)
            daily_nutrition: User's nutrition so far today
            daily_targets: Daily nutrition targets
            
        Returns:
            Dictionary with menu analysis and recommendations
        """
        try:
            health_conditions = user_profile.get("health_conditions", [])
            dietary_preferences = user_profile.get("dietary_preferences", [])
            health_goal = user_profile.get("health_goal", "general_health")
            age_group = user_profile.get("age_group", "26-35")
            
            # Calculate remaining nutrition budget for today
            remaining_nutrition = {
                nutrient: daily_targets.get(nutrient, 0) - daily_nutrition.get(nutrient, 0)
                for nutrient in daily_targets.keys()
            }
            
            prompt = f"""Analyze this restaurant menu and provide personalized recommendations for this user.

RESTAURANT MENU:
{menu_text}

USER PROFILE:
- Age Group: {age_group}
- Health Goal: {health_goal}
- Health Conditions: {', '.join(health_conditions) if health_conditions else 'None'}
- Dietary Preferences: {', '.join(dietary_preferences) if dietary_preferences else 'No restrictions'}

TODAY'S NUTRITION SO FAR:
- Calories: {daily_nutrition.get('calories', 0):.0f} / {daily_targets.get('calories', 2000)}
- Protein: {daily_nutrition.get('protein', 0):.1f}g / {daily_targets.get('protein', 50)}g
- Carbs: {daily_nutrition.get('carbs', 0):.1f}g / {daily_targets.get('carbs', 300)}g
- Fat: {daily_nutrition.get('fat', 0):.1f}g / {daily_targets.get('fat', 65)}g
- Sodium: {daily_nutrition.get('sodium', 0):.0f}mg / {daily_targets.get('sodium', 2300)}mg
- Sugar: {daily_nutrition.get('sugar', 0):.1f}g / {daily_targets.get('sugar', 50)}g
- Fiber: {daily_nutrition.get('fiber', 0):.1f}g / {daily_targets.get('fiber', 25)}g

REMAINING NUTRITION BUDGET:
- Calories: {remaining_nutrition.get('calories', 0):.0f}
- Protein: {remaining_nutrition.get('protein', 0):.1f}g
- Carbs: {remaining_nutrition.get('carbs', 0):.1f}g
- Sodium: {remaining_nutrition.get('sodium', 0):.0f}mg

Please provide analysis in JSON format:
{{
    "restaurant_analysis": "brief assessment of menu healthiness",
    "best_options": [
        {{
            "menu_item": "name of dish",
            "reason": "why this is good for the user",
            "estimated_nutrition": {{
                "calories": number,
                "protein": number,
                "carbs": number,
                "fat": number,
                "sodium": number,
                "sugar": number,
                "fiber": number
            }},
            "alignment": "how well this fits their remaining budget",
            "modifications": "suggestions to make it healthier (if any)",
            "badge": "label like 'Best for Protein' or 'Lowest Calorie' or 'Best for Budget'"
        }}
    ],
    "items_to_avoid": [
        {{
            "menu_item": "name of dish",
            "reason": "why this may not be ideal",
            "concern": "specific nutrition concern (high sodium, high sugar, etc)"
        }}
    ],
    "special_recommendations": {{
        "best_for_calories": {{"item": "...", "calories": 0}},
        "best_for_protein": {{"item": "...", "protein": 0}},
        "best_for_fiber": {{"item": "...", "fiber": 0}},
        "best_for_health_conditions": {{"item": "...", "reason": "..."}}
    }},
    "pairing_suggestions": "suggestions for combining items to make a complete meal",
    "sides_recommendations": "healthiest side options",
    "drinks_recommendations": "healthiest drink choices",
    "general_tips": "tips specific to this restaurant/cuisine type"
}}

Be specific and reference actual items from the menu. Provide realistic nutrition estimates."""
            
            response = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a nutrition expert analyzing restaurant menus. Provide personalized, health-conscious recommendations in JSON format. Be specific with menu items and realistic with nutrition estimates."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            response_text = response.choices[0].message.content
            
            # Parse JSON response
            try:
                # Find JSON in response (it might be wrapped in markdown code blocks)
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    analysis = json.loads(json_str)
                    return analysis
                else:
                    return None
            except json.JSONDecodeError:
                return None
                
        except Exception as e:
            st.error(f"Error analyzing menu: {str(e)}")
            return None
    
    def get_cuisine_tips(self, cuisine_type: str) -> str:
        """
        Get specific nutrition tips for a particular cuisine
        
        Args:
            cuisine_type: Type of cuisine (Italian, Japanese, Mexican, etc)
            
        Returns:
            Nutrition tips for the cuisine
        """
        try:
            prompt = f"""Provide 3-4 brief, practical nutrition tips for eating healthy at {cuisine_type} restaurants.
            
Focus on:
- Which dishes tend to be healthier
- Common hidden calories or sodium
- How to modify dishes to be healthier
- What to watch out for

Keep it concise and actionable."""
            
            response = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a nutrition expert. Provide practical, specific tips."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Unable to fetch cuisine tips: {str(e)}"
    
    def compare_menu_items(
        self,
        item1: str,
        item2: str,
        user_goals: Dict
    ) -> Optional[Dict]:
        """
        Compare two menu items side-by-side
        
        Args:
            item1: First menu item description
            item2: Second menu item description
            user_goals: User's health goals and restrictions
            
        Returns:
            Comparison with winner and reasoning
        """
        try:
            health_goal = user_goals.get("health_goal", "general_health")
            health_conditions = user_goals.get("health_conditions", [])
            
            prompt = f"""Compare these two menu items for someone with these goals:
- Health Goal: {health_goal}
- Health Conditions: {', '.join(health_conditions) if health_conditions else 'None'}

ITEM 1: {item1}
ITEM 2: {item2}

Provide comparison in JSON format:
{{
    "item1": {{
        "name": "...",
        "estimated_nutrition": {{"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "sodium": 0}},
        "pros": ["...", "..."],
        "cons": ["...", "..."]
    }},
    "item2": {{
        "name": "...",
        "estimated_nutrition": {{"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "sodium": 0}},
        "pros": ["...", "..."],
        "cons": ["...", "..."]
    }},
    "winner": "item name",
    "reason": "why this item is better for this user",
    "winner_badge": "reason in one phrase (e.g., 'More Protein', 'Lower Calorie', 'Better Fiber')"
}}"""
            
            response = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a nutrition expert. Compare menu items objectively based on user goals."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            response_text = response.choices[0].message.content
            
            # Parse JSON response
            try:
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response_text[start_idx:end_idx]
                    comparison = json.loads(json_str)
                    return comparison
                else:
                    return None
            except json.JSONDecodeError:
                return None
                
        except Exception as e:
            st.error(f"Error comparing items: {str(e)}")
            return None
