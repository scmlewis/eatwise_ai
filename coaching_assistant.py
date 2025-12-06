"""Personalized Nutrition Coaching Assistant Module for EatWise"""
import json
from typing import Dict, List, Optional, Tuple
from openai import AzureOpenAI
import streamlit as st
from config import AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT
from datetime import datetime, timedelta


class CoachingAssistant:
    """AI-powered nutrition coach that provides personalized guidance and insights"""
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version="2023-05-15",
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
    
    def get_meal_guidance(
        self,
        meal_name: str,
        meal_nutrition: Dict,
        daily_nutrition: Dict,
        daily_targets: Dict,
        user_profile: Dict,
        recent_meals: List[Dict] = None
    ) -> str:
        """
        Provide real-time coaching guidance on a meal
        
        Args:
            meal_name: Name of the meal
            meal_nutrition: Nutritional info of the meal
            daily_nutrition: User's daily nutrition so far
            daily_targets: User's daily targets
            user_profile: User health profile
            recent_meals: Recent meals for context
            
        Returns:
            Coaching guidance text
        """
        try:
            health_conditions = user_profile.get("health_conditions", [])
            age_group = user_profile.get("age_group", "26-35")
            health_goal = user_profile.get("health_goal", "general_health")
            height_cm = user_profile.get("height_cm")
            weight_kg = user_profile.get("weight_kg")
            
            # Calculate BMI if available
            bmi_info = ""
            if height_cm and weight_kg:
                try:
                    height_m = height_cm / 100
                    bmi = weight_kg / (height_m ** 2)
                    bmi_info = f"\n- Height: {height_cm}cm, Weight: {weight_kg}kg, BMI: {bmi:.1f}"
                except:
                    pass
            
            # Calculate how this meal affects daily totals
            projected_daily = {
                k: daily_nutrition.get(k, 0) + meal_nutrition.get(k, 0)
                for k in daily_targets.keys()
            }
            
            prompt = f"""As a supportive nutrition coach, provide personalized guidance for this meal choice.

MEAL BEING EVALUATED:
- Name: {meal_name}
- Calories: {meal_nutrition.get('calories', 0):.0f}
- Protein: {meal_nutrition.get('protein', 0):.1f}g
- Carbs: {meal_nutrition.get('carbs', 0):.1f}g
- Fat: {meal_nutrition.get('fat', 0):.1f}g
- Sodium: {meal_nutrition.get('sodium', 0):.0f}mg
- Sugar: {meal_nutrition.get('sugar', 0):.1f}g
- Fiber: {meal_nutrition.get('fiber', 0):.1f}g

USER CONTEXT:
- Age Group: {age_group}
- Health Goal: {health_goal}
- Health Conditions: {', '.join(health_conditions) if health_conditions else 'None'}{bmi_info}

TODAY'S NUTRITION SO FAR:
- Calories: {daily_nutrition.get('calories', 0):.0f} / {daily_targets.get('calories', 2000)}
- Protein: {daily_nutrition.get('protein', 0):.1f}g / {daily_targets.get('protein', 50)}g
- Carbs: {daily_nutrition.get('carbs', 0):.1f}g / {daily_targets.get('carbs', 300)}g

PROJECTED DAILY TOTALS (if user eats this meal):
- Calories: {projected_daily.get('calories', 0):.0f} / {daily_targets.get('calories', 2000)}
- Protein: {projected_daily.get('protein', 0):.1f}g / {daily_targets.get('protein', 50)}g
- Carbs: {projected_daily.get('carbs', 0):.1f}g / {daily_targets.get('carbs', 300)}g

Provide:
1. Quick assessment (1-2 sentences) - Is this a good choice right now?
2. Specific positives about this meal
3. Any concerns based on their profile/goals
4. Suggestion for how to make it better (if applicable)
5. What they should eat next to balance their day

Be encouraging, specific, and practical. Keep total response under 200 words."""
            
            response = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are an enthusiastic and supportive nutrition coach. Provide practical, personalized guidance without being judgmental. Always be encouraging."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Coaching unavailable: {str(e)}"
    
    def analyze_eating_patterns(
        self,
        meals: List[Dict],
        daily_nutrition: Dict,
        daily_targets: Dict,
        user_profile: Dict,
        days: int = 7
    ) -> Dict[str, any]:
        """
        Analyze eating patterns and provide insights
        
        Args:
            meals: List of meals logged
            daily_nutrition: Today's nutrition
            daily_targets: Daily targets
            user_profile: User profile
            days: Number of days to analyze
            
        Returns:
            Dictionary with patterns and insights
        """
        try:
            health_conditions = user_profile.get("health_conditions", [])
            
            # Prepare meal summary
            meal_summary = []
            for meal in meals[-20:]:  # Last 20 meals
                meal_summary.append({
                    "name": meal.get("meal_name"),
                    "type": meal.get("meal_type"),
                    "calories": meal.get("nutrition", {}).get("calories", 0)
                })
            
            prompt = f"""Analyze this user's eating patterns and provide personalized insights.

MEAL HISTORY (Last meals logged):
{json.dumps(meal_summary, indent=2)}

USER PROFILE:
- Health Conditions: {', '.join(health_conditions) if health_conditions else 'None'}
- Health Goal: {user_profile.get('health_goal', 'general_health')}

DAILY TARGETS:
{json.dumps(daily_targets, indent=2)}

Provide insights in JSON format:
{{
    "patterns": ["pattern1", "pattern2"],
    "strengths": ["positive habit 1", "positive habit 2"],
    "challenges": ["challenge 1", "challenge 2"],
    "red_flags": ["any concerning patterns"],
    "key_recommendation": "One specific, actionable recommendation",
    "motivational_insight": "Encouraging observation about their progress"
}}

Be specific, data-driven, and positive. Focus on what they're doing well and one area to improve."""
            
            response = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a data-driven nutrition analyst providing positive, specific feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=500
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
            return {"error": str(e)}
    
    def answer_nutrition_question(
        self,
        question: str,
        user_profile: Dict,
        daily_nutrition: Dict = None,
        daily_targets: Dict = None
    ) -> str:
        """
        Answer nutrition questions personalized to the user
        
        Args:
            question: User's question about nutrition
            user_profile: User profile for context
            daily_nutrition: Optional current nutrition data
            daily_targets: Optional nutrition targets
            
        Returns:
            Answer text
        """
        try:
            health_conditions = user_profile.get("health_conditions", [])
            age_group = user_profile.get("age_group", "26-35")
            
            context = f"""User Context:
- Age Group: {age_group}
- Health Conditions: {', '.join(health_conditions) if health_conditions else 'None'}
- Health Goal: {user_profile.get('health_goal', 'general_health')}"""
            
            if daily_nutrition and daily_targets:
                context += f"""

Current Day's Nutrition:
- Calories: {daily_nutrition.get('calories', 0):.0f} / {daily_targets.get('calories', 2000)}
- Protein: {daily_nutrition.get('protein', 0):.1f}g / {daily_targets.get('protein', 50)}g
- Carbs: {daily_nutrition.get('carbs', 0):.1f}g / {daily_targets.get('carbs', 300)}g"""
            
            prompt = f"""{context}

User Question: {question}

Provide a helpful, personalized answer that:
1. Is relevant to their specific situation
2. Is accurate and evidence-based
3. Is practical and actionable
4. Is encouraging and supportive
5. References their health conditions/goals if relevant

Keep answer concise (under 150 words) unless the question requires more detail."""
            
            response = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a friendly, knowledgeable nutrition expert providing personalized advice. Be helpful and supportive."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Sorry, I couldn't answer that: {str(e)}"
    
    def get_daily_coaching_tip(self, user_profile: Dict, daily_nutrition: Dict, daily_targets: Dict) -> str:
        """
        Get a personalized daily coaching tip
        
        Args:
            user_profile: User profile
            daily_nutrition: Current daily nutrition
            daily_targets: Daily targets
            
        Returns:
            Coaching tip text
        """
        try:
            health_conditions = user_profile.get("health_conditions", [])
            health_goal = user_profile.get("health_goal", "general_health")
            
            # Determine what's going well and what needs work
            nutrition_status = {}
            for nutrient, target in daily_targets.items():
                current = daily_nutrition.get(nutrient, 0)
                pct = (current / target * 100) if target > 0 else 0
                nutrition_status[nutrient] = {
                    "current": current,
                    "target": target,
                    "percentage": pct,
                    "status": "under" if pct < 80 else ("over" if pct > 120 else "on_target")
                }
            
            prompt = f"""Provide one specific, actionable coaching tip for today.

USER PROFILE:
- Health Goal: {health_goal}
- Health Conditions: {', '.join(health_conditions) if health_conditions else 'None'}

TODAY'S NUTRITION STATUS:
{json.dumps(nutrition_status, indent=2)}

Provide a tip that:
1. Is specific to what they need TODAY
2. Is actionable and can be done in the next few hours
3. Is encouraging
4. References their health conditions/goals
5. Is one sentence or very brief (under 50 words)

Format: Just the tip text, no preamble."""
            
            response = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a supportive nutrition coach giving one specific tip per day. Be encouraging and practical."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            return "Keep logging your meals consistently - you're doing great!"
    
    def get_meal_alternative(
        self,
        meal_name: str,
        reason: str,
        user_profile: Dict,
        daily_nutrition: Dict,
        daily_targets: Dict
    ) -> str:
        """
        Suggest a healthier alternative to a meal
        
        Args:
            meal_name: Current meal
            reason: Why looking for alternative (e.g., "too many calories", "too much sodium")
            user_profile: User profile
            daily_nutrition: Current daily nutrition
            daily_targets: Daily targets
            
        Returns:
            Alternative meal suggestion
        """
        try:
            health_conditions = user_profile.get("health_conditions", [])
            dietary_prefs = user_profile.get("dietary_preferences", [])
            
            prompt = f"""Suggest a healthier alternative meal.

CURRENT MEAL: {meal_name}
REASON FOR CHANGE: {reason}

USER CONSTRAINTS:
- Health Conditions: {', '.join(health_conditions) if health_conditions else 'None'}
- Dietary Preferences: {', '.join(dietary_prefs) if dietary_prefs else 'No restrictions'}

NUTRITION STATUS TODAY:
- Calories: {daily_nutrition.get('calories', 0):.0f} / {daily_targets.get('calories', 2000)}
- Protein: {daily_nutrition.get('protein', 0):.1f}g / {daily_targets.get('protein', 50)}g
- Sodium: {daily_nutrition.get('sodium', 0):.0f}mg / {daily_targets.get('sodium', 2300)}mg

Suggest a meal that:
1. Solves the problem they identified ({reason})
2. Respects their dietary preferences and health conditions
3. Is practical and tasty
4. Provides approximate nutrition (calories, protein)
5. Is brief (2-3 sentences max)"""
            
            response = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a practical nutrition coach suggesting delicious, healthy meal alternatives."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            return f"Unable to suggest alternative: {str(e)}"
    
    def get_conversation_response(
        self,
        conversation_history: List[Dict],
        user_message: str,
        user_profile: Dict,
        daily_nutrition: Dict,
        daily_targets: Dict
    ) -> str:
        """
        Get a response from the coaching assistant in a conversation
        
        Args:
            conversation_history: List of previous messages
            user_message: New user message
            user_profile: User profile
            daily_nutrition: Current daily nutrition
            daily_targets: Daily targets
            
        Returns:
            Assistant response
        """
        try:
            health_conditions = user_profile.get("health_conditions", [])
            health_goal = user_profile.get("health_goal", "general_health")
            age_group = user_profile.get("age_group", "26-35")
            height_cm = user_profile.get("height_cm")
            weight_kg = user_profile.get("weight_kg")
            
            # Calculate BMI if height and weight are available
            bmi_info = ""
            if height_cm and weight_kg:
                try:
                    height_m = height_cm / 100
                    bmi = weight_kg / (height_m ** 2)
                    bmi_info = f"- Height: {height_cm}cm, Weight: {weight_kg}kg, BMI: {bmi:.1f}\n"
                except:
                    pass
            
            # Build system context
            system_prompt = f"""You are a friendly, supportive nutrition coach for an app called EatWise. 
Your role is to:
1. Answer nutrition questions
2. Provide meal guidance and suggestions
3. Celebrate progress and wins
4. Offer practical, actionable advice
5. Be encouraging and non-judgmental

USER PROFILE:
- Age Group: {age_group}
- Health Goal: {health_goal}
- Health Conditions: {', '.join(health_conditions) if health_conditions else 'None'}
{bmi_info}

CURRENT NUTRITION STATUS:
- Calories: {daily_nutrition.get('calories', 0):.0f} / {daily_targets.get('calories', 2000)}
- Protein: {daily_nutrition.get('protein', 0):.1f}g / {daily_targets.get('protein', 50)}g
- Carbs: {daily_nutrition.get('carbs', 0):.1f}g / {daily_targets.get('carbs', 300)}g

Reference this context in your responses when relevant. Keep responses concise (2-4 sentences typically) unless more detail is needed."""
            
            # Build message history for context
            messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in conversation_history[-6:]  # Last 6 messages for context
            ]
            messages.append({"role": "user", "content": user_message})
            
            response = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[{"role": "system", "content": system_prompt}] + messages,
                temperature=0.7,
                max_tokens=400
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
