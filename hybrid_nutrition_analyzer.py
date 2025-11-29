"""
EatWise AI - Hybrid Nutrition Analyzer
Uses LLM for ingredient detection + Database for accurate nutrition values
Can be used standalone or alongside existing NutritionAnalyzer
"""

import json
import re
from typing import Dict, Optional, List
from nutrition_database import find_food_matches, get_nutrition_for_portion, validate_nutrition_data


class HybridNutritionAnalyzer:
    """
    Hybrid nutrition analysis: LLM for detection, database for accuracy
    This is a complementary module - doesn't replace existing nutrition_analyzer.py
    """
    
    def __init__(self):
        """Initialize hybrid analyzer with database"""
        pass
    
    def parse_ingredients_from_llm_response(self, llm_response: str) -> List[Dict]:
        """
        Parse ingredient list from LLM response.
        Expects format like: food item (quantity, unit, preparation)
        
        Args:
            llm_response: Raw text from LLM
            
        Returns:
            List of ingredient dictionaries
        """
        items = []
        
        try:
            # Try to extract JSON if present
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                data = json.loads(json_match.group())
                if "items" in data:
                    return data["items"]
        except:
            pass
        
        # Fallback: parse text format
        # Pattern: food_name (qty unit)
        pattern = r'(.+?)\s*\((\d+(?:\.\d+)?)\s*([a-z]+)\)'
        matches = re.findall(pattern, llm_response, re.IGNORECASE)
        
        for match in matches:
            items.append({
                "name": match[0].strip(),
                "quantity": float(match[1]),
                "unit": match[2].lower(),
                "preparation": "cooked"
            })
        
        return items
    
    def calculate_meal_nutrition(self, ingredients: List[Dict]) -> Dict:
        """
        Calculate total nutrition for a meal using hybrid approach.
        Uses database first, estimates for unknowns.
        
        Args:
            ingredients: List of food items with quantity/unit
            
        Returns:
            Dictionary with total nutrition values
        """
        total = {
            "calories": 0.0,
            "protein": 0.0,
            "carbs": 0.0,
            "fat": 0.0,
            "fiber": 0.0,
            "sodium": 0.0,
            "sugar": 0.0
        }
        
        for ingredient in ingredients:
            food_name = ingredient.get("name", "").lower().strip()
            quantity = ingredient.get("quantity", 100)
            unit = ingredient.get("unit", "g")
            
            # Try database lookup
            nutrition = get_nutrition_for_portion(food_name, quantity, unit)
            
            if nutrition:
                # Found in database
                for key in total:
                    total[key] += nutrition.get(key, 0)
            else:
                # Estimate if not found
                estimated = self._estimate_nutrition(food_name, quantity, unit)
                for key in total:
                    total[key] += estimated.get(key, 0)
        
        # Validate totals
        total = validate_nutrition_data(total)
        
        # Round to 1 decimal
        for key in total:
            total[key] = round(total[key], 1)
        
        return total
    
    def _estimate_nutrition(self, food_name: str, quantity: float, unit: str) -> Dict:
        """
        Estimate nutrition for unknown foods using heuristics.
        
        Args:
            food_name: Name of the food
            quantity: Amount
            unit: Unit of measurement
            
        Returns:
            Estimated nutrition dictionary
        """
        # Base estimates per 100g by category
        estimates = {
            "meat": {"calories": 200, "protein": 26, "carbs": 0, "fat": 10, "fiber": 0, "sodium": 80, "sugar": 0},
            "fish": {"calories": 150, "protein": 20, "carbs": 0, "fat": 7, "fiber": 0, "sodium": 50, "sugar": 0},
            "vegetable": {"calories": 40, "protein": 2, "carbs": 8, "fat": 0.3, "fiber": 2, "sodium": 30, "sugar": 2},
            "fruit": {"calories": 60, "protein": 0.7, "carbs": 15, "fat": 0.2, "fiber": 2, "sodium": 5, "sugar": 10},
            "grain": {"calories": 130, "protein": 4, "carbs": 28, "fat": 1, "fiber": 2, "sodium": 5, "sugar": 0.5},
            "legume": {"calories": 140, "protein": 8, "carbs": 25, "fat": 1, "fiber": 6, "sodium": 10, "sugar": 1},
            "dairy": {"calories": 150, "protein": 8, "carbs": 5, "fat": 8, "fiber": 0, "sodium": 200, "sugar": 4},
            "oil": {"calories": 884, "protein": 0, "carbs": 0, "fat": 100, "fiber": 0, "sodium": 0, "sugar": 0},
        }
        
        # Categorize food
        category = "vegetable"  # default
        food_lower = food_name.lower()
        
        if any(x in food_lower for x in ["chicken", "beef", "pork", "meat", "turkey", "lamb"]):
            category = "meat"
        elif any(x in food_lower for x in ["fish", "salmon", "tuna", "cod", "shrimp"]):
            category = "fish"
        elif any(x in food_lower for x in ["apple", "banana", "orange", "fruit", "berry"]):
            category = "fruit"
        elif any(x in food_lower for x in ["rice", "bread", "pasta", "grain", "oat"]):
            category = "grain"
        elif any(x in food_lower for x in ["bean", "lentil", "chickpea", "legume"]):
            category = "legume"
        elif any(x in food_lower for x in ["cheese", "milk", "yogurt", "dairy"]):
            category = "dairy"
        elif any(x in food_lower for x in ["oil", "fat", "butter"]):
            category = "oil"
        
        base = estimates[category].copy()
        
        # Convert to grams using portion multipliers
        from nutrition_database import PORTION_MULTIPLIERS
        multiplier = PORTION_MULTIPLIERS.get(unit.lower().strip(), 1/100)
        grams = quantity * multiplier * 100
        portion_mult = grams / 100
        
        # Apply portion size
        result = {}
        for nutrient, value in base.items():
            result[nutrient] = round(value * portion_mult, 1)
        
        return result
    
    def get_nutrition_summary_text(self, nutrition: Dict) -> str:
        """
        Format nutrition data as readable text.
        
        Args:
            nutrition: Dictionary with nutrition values
            
        Returns:
            Formatted markdown text
        """
        return f"""**Nutrition Facts**:
- **Calories**: {int(nutrition['calories'])} cal
- **Protein**: {nutrition['protein']}g
- **Carbs**: {nutrition['carbs']}g
- **Fat**: {nutrition['fat']}g
- **Fiber**: {nutrition['fiber']}g
- **Sodium**: {int(nutrition['sodium'])}mg
- **Sugar**: {nutrition['sugar']}g"""
    
    def is_food_in_database(self, food_name: str) -> bool:
        """
        Check if a food exists in the database.
        
        Args:
            food_name: Name of food to check
            
        Returns:
            True if food is in database
        """
        matches = find_food_matches(food_name)
        return len(matches) > 0
    
    def get_database_coverage(self, ingredients: List[Dict]) -> Dict:
        """
        Check which ingredients are in the database vs estimated.
        
        Args:
            ingredients: List of food items
            
        Returns:
            Dictionary with coverage statistics
        """
        in_db = 0
        estimated = 0
        
        for ingredient in ingredients:
            food_name = ingredient.get("name", "").lower()
            if self.is_food_in_database(food_name):
                in_db += 1
            else:
                estimated += 1
        
        total = in_db + estimated
        coverage = (in_db / total * 100) if total > 0 else 0
        
        return {
            "in_database": in_db,
            "estimated": estimated,
            "total": total,
            "coverage_percentage": round(coverage, 1)
        }
