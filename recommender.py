"""Recommendation Engine for EatWise"""
from typing import Dict, List, Optional
from openai import AzureOpenAI
import json
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT, AGE_GROUP_TARGETS, HEALTH_CONDITION_TARGETS
import streamlit as st


class RecommendationEngine:
    """Provides personalized meal recommendations"""
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version="2023-05-15",
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
    
    def get_personalized_recommendations(
        self,
        user_profile: Dict,
        recent_meals: List[Dict],
        daily_nutrition: Dict,
        targets: Dict
    ) -> List[Dict]:
        """
        Get personalized meal recommendations based on user profile and eating habits
        
        Args:
            user_profile: User health profile data
            recent_meals: List of recent meals logged
            daily_nutrition: Today's nutrition summary
            targets: Daily nutrition targets
            
        Returns:
            List of meal recommendations
        """
        try:
            # Build context for recommendations
            health_conditions = user_profile.get("health_conditions", [])
            age_group = user_profile.get("age_group", "26-35 (Adult)")
            dietary_preferences = user_profile.get("dietary_preferences", [])
            
            # Calculate nutrition gaps
            nutrition_gaps = self._calculate_gaps(daily_nutrition, targets)
            
            prompt = f"""Based on the user profile and recent eating habits, provide 5 healthy meal recommendations for the next meal.

User Profile:
- Age Group: {age_group}
- Health Conditions: {', '.join(health_conditions) if health_conditions else 'None'}
- Dietary Preferences: {', '.join(dietary_preferences) if dietary_preferences else 'No restrictions'}

Today's Nutrition Summary:
- Calories: {daily_nutrition.get('calories', 0):.0f} / {targets.get('calories', 2000)}
- Protein: {daily_nutrition.get('protein', 0):.1f}g / {targets.get('protein', 50)}g
- Carbs: {daily_nutrition.get('carbs', 0):.1f}g / {targets.get('carbs', 300)}g
- Sodium: {daily_nutrition.get('sodium', 0):.0f}mg / {targets.get('sodium', 2300)}mg

Nutrition Gaps to Fill:
{json.dumps(nutrition_gaps, indent=2)}

Please provide recommendations in JSON format:
[{{
    "meal_name": "name",
    "description": "brief description",
    "meal_type": "breakfast/lunch/dinner/snack",
    "estimated_nutrition": {{
        "calories": number,
        "protein": number,
        "carbs": number,
        "fat": number,
        "sodium": number,
        "sugar": number,
        "fiber": number
    }},
    "why_recommended": "explanation of why this meal is good for the user",
    "health_benefits": ["benefit1", "benefit2"],
    "preparation_time": "minutes"
}}]

Focus on:
1. Filling the user's nutrition gaps
2. Considering their health conditions
3. Respecting dietary preferences
4. Making practical, tasty suggestions
"""
            
            response = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a professional nutritionist providing personalized meal recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1200
            )
            
            try:
                recommendations = json.loads(response.choices[0].message.content)
                return recommendations
            except json.JSONDecodeError:
                content = response.choices[0].message.content
                start_idx = content.find('[')
                end_idx = content.rfind(']') + 1
                if start_idx != -1 and end_idx > start_idx:
                    recommendations = json.loads(content[start_idx:end_idx])
                    return recommendations
                return []
        
        except Exception as e:
            st.error(f"Error getting recommendations: {str(e)}")
            return []
    
    def get_weekly_meal_plan(
        self,
        user_profile: Dict,
        targets: Dict,
        dietary_restrictions: List[str] = None
    ) -> Dict[str, List[Dict]]:
        """
        Generate a personalized weekly meal plan
        
        Args:
            user_profile: User health profile
            targets: Daily nutrition targets
            dietary_restrictions: List of dietary restrictions
            
        Returns:
            Dictionary with daily meal plans
        """
        try:
            health_conditions = user_profile.get("health_conditions", [])
            age_group = user_profile.get("age_group", "26-35 (Adult)")
            
            prompt = f"""Create a personalized 7-day meal plan for a health-conscious professional.

User Profile:
- Age Group: {age_group}
- Health Conditions: {', '.join(health_conditions) if health_conditions else 'None'}
- Daily Calorie Target: {targets.get('calories', 2000)}
- Dietary Restrictions: {', '.join(dietary_restrictions) if dietary_restrictions else 'None'}

For each day, suggest:
- 1 Breakfast
- 1 Lunch
- 1 Dinner
- 1 Snack

Provide in JSON format:
{{
    "Monday": [
        {{"meal_name": "...", "meal_type": "breakfast", "calories": ..., "description": "..."}},
        ...
    ],
    ...
    "Sunday": [...]
}}

Ensure:
1. Variety across the week
2. Balanced nutrition
3. Practical and quick meals (respecting busy professionals)
4. Local and accessible ingredients
5. Consideration of health conditions
"""
            
            response = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a professional nutritionist creating balanced meal plans."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            try:
                meal_plan = json.loads(response.choices[0].message.content)
                return meal_plan
            except json.JSONDecodeError:
                content = response.choices[0].message.content
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    meal_plan = json.loads(content[start_idx:end_idx])
                    return meal_plan
                return {}
        
        except Exception as e:
            st.error(f"Error generating meal plan: {str(e)}")
            return {}
    
    def get_nutrition_trivia(self) -> str:
        """
        Get interesting nutrition trivia for user engagement (static tips - no API calls)
        
        Returns:
            Trivia string
        """
        import random
        
        nutrition_tips = [
            "💡 Drinking water before meals can help you eat less and stay fuller longer!",
            "🥗 Eating colorful vegetables ensures you get a variety of nutrients and antioxidants.",
            "🍎 An apple a day keeps the doctor away - they're rich in fiber and vitamin C!",
            "💪 Protein helps build and repair muscles. Include it in every meal!",
            "🧂 Most people consume too much sodium. Try to keep it under 2,300mg daily.",
            "🍌 Bananas are packed with potassium, which helps regulate heart health.",
            "🥑 Avocados contain healthy fats that support brain and heart health.",
            "🧠 Omega-3 fatty acids found in fish and nuts boost brain function.",
            "🌽 Whole grains provide sustained energy and are better than refined carbs.",
            "🥕 Beta-carotene in orange vegetables promotes eye health and immunity.",
            "🍇 Berries are antioxidant powerhouses that protect against cell damage.",
            "🥛 Calcium in dairy products strengthens bones - aim for 3 servings daily.",
            "🥒 Fermented foods like yogurt contain probiotics for gut health.",
            "🥜 Nuts and seeds are nutrient-dense snacks with healthy fats and protein.",
            "🌶️ Spicy foods can boost metabolism and contain beneficial compounds.",
            "🍵 Green tea is rich in antioxidants and can support metabolism.",
            "🥦 Cruciferous vegetables like broccoli have cancer-fighting compounds.",
            "🍯 Natural sweeteners like honey contain trace minerals and antioxidants.",
            "🥝 Kiwis are loaded with vitamin C and bromelain for digestion.",
            "🫐 Blueberries are called 'superfoods' for their exceptional antioxidant content.",
            "🧄 Garlic has natural antimicrobial and anti-inflammatory properties.",
            "🥕 Eat the rainbow! Different colors provide different nutrients.",
            "⏰ Eating at consistent times helps regulate your metabolism and appetite.",
            "🚶 Light walks after meals help stabilize blood sugar levels.",
            "💧 Most people mistake thirst for hunger - drink water first!",
            "🍽️ Eating slowly allows time for fullness signals to reach your brain.",
            "🥤 Sugary drinks are a major source of empty calories - choose water instead!",
            "🌾 Fiber helps with digestion and keeps you feeling full longer.",
            "🍓 Fresh fruits have more nutrients than canned or dried versions.",
            "⚖️ Balance your plate: 50% vegetables, 25% protein, 25% carbs.",
        ]
        
        return random.choice(nutrition_tips)
    
    def get_health_insights(
        self,
        meals_data: List[Dict],
        user_profile: Dict,
        nutrition_history: Dict
    ) -> Dict[str, str]:
        """
        Generate health insights and patterns from eating history
        
        Args:
            meals_data: List of meals
            user_profile: User profile
            nutrition_history: Historical nutrition data
            
        Returns:
            Dictionary with various insights
        """
        try:
            prompt = f"""Analyze the user's eating patterns and provide health insights.

Eating History Summary:
{json.dumps({
    "recent_meals": [m.get('meal_name', 'Unknown') for m in meals_data[-10:]],
    "nutrition_patterns": nutrition_history
}, indent=2)}

Health Profile:
{json.dumps(user_profile, indent=2)}

Provide insights in JSON format:
{{
    "overall_assessment": "brief overall assessment",
    "strengths": ["positive pattern 1", "positive pattern 2"],
    "areas_for_improvement": ["area 1", "area 2"],
    "specific_recommendations": ["recommendation 1", "recommendation 2"],
    "red_flags": ["flag 1 if any"],
    "motivational_message": "encouraging message"
}}

Be supportive and practical in your suggestions."""
            
            response = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a supportive nutrition coach analyzing eating patterns."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=800
            )
            
            try:
                insights = json.loads(response.choices[0].message.content)
                return insights
            except json.JSONDecodeError:
                content = response.choices[0].message.content
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    insights = json.loads(content[start_idx:end_idx])
                    return insights
                return {}
        
        except Exception as e:
            st.error(f"Error generating insights: {str(e)}")
            return {}
    
    def _calculate_gaps(self, current: Dict, targets: Dict) -> Dict:
        """Calculate nutrition gaps between current intake and targets"""
        gaps = {}
        for nutrient, target_value in targets.items():
            current_value = current.get(nutrient, 0)
            gap = target_value - current_value
            gaps[nutrient] = {
                "target": target_value,
                "current": current_value,
                "gap": gap,
                "percentage": (current_value / target_value * 100) if target_value > 0 else 0
            }
        return gaps
