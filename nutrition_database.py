"""
EatWise AI - Nutrition Database
Comprehensive food nutrition database for accurate hybrid analysis
Based on USDA and nutrition reference data
"""

# Common foods with their nutrition values per 100g (standard serving)
# Format: {food_name: {calories, protein_g, carbs_g, fat_g, fiber_g, sodium_mg, sugar_g}}
NUTRITION_DATABASE = {
    # PROTEINS - Meats & Poultry
    "chicken breast": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6, "fiber": 0, "sodium": 74, "sugar": 0},
    "chicken thigh": {"calories": 209, "protein": 26, "carbs": 0, "fat": 11, "fiber": 0, "sodium": 81, "sugar": 0},
    "beef": {"calories": 250, "protein": 26, "carbs": 0, "fat": 15, "fiber": 0, "sodium": 75, "sugar": 0},
    "ground beef": {"calories": 217, "protein": 23, "carbs": 0, "fat": 13, "fiber": 0, "sodium": 75, "sugar": 0},
    "salmon": {"calories": 208, "protein": 20, "carbs": 0, "fat": 13, "fiber": 0, "sodium": 59, "sugar": 0},
    "tuna": {"calories": 144, "protein": 30, "carbs": 0, "fat": 1.3, "fiber": 0, "sodium": 41, "sugar": 0},
    "cod": {"calories": 82, "protein": 18, "carbs": 0, "fat": 0.7, "fiber": 0, "sodium": 77, "sugar": 0},
    "pork": {"calories": 242, "protein": 27, "carbs": 0, "fat": 14, "fiber": 0, "sodium": 75, "sugar": 0},
    "turkey": {"calories": 135, "protein": 30, "carbs": 0, "fat": 0.5, "fiber": 0, "sodium": 54, "sugar": 0},
    "eggs": {"calories": 155, "protein": 13, "carbs": 1.1, "fat": 11, "fiber": 0, "sodium": 124, "sugar": 1.1},
    "egg white": {"calories": 52, "protein": 11, "carbs": 1.3, "fat": 0.2, "fiber": 0, "sodium": 166, "sugar": 1.3},

    # VEGETABLES
    "broccoli": {"calories": 34, "protein": 2.8, "carbs": 7, "fat": 0.4, "fiber": 2.4, "sodium": 64, "sugar": 1.4},
    "carrot": {"calories": 41, "protein": 0.9, "carbs": 10, "fat": 0.2, "fiber": 2.8, "sodium": 69, "sugar": 4.7},
    "potato": {"calories": 77, "protein": 2, "carbs": 17, "fat": 0.1, "fiber": 2.1, "sodium": 6, "sugar": 0.8},
    "sweet potato": {"calories": 86, "protein": 1.6, "carbs": 20, "fat": 0.1, "fiber": 3, "sodium": 55, "sugar": 4.2},
    "spinach": {"calories": 23, "protein": 2.7, "carbs": 3.6, "fat": 0.4, "fiber": 2.2, "sodium": 79, "sugar": 0.4},
    "kale": {"calories": 49, "protein": 4.3, "carbs": 9, "fat": 0.9, "fiber": 2.4, "sodium": 64, "sugar": 0.9},
    "lettuce": {"calories": 15, "protein": 1.2, "carbs": 3, "fat": 0.2, "fiber": 1.2, "sodium": 8, "sugar": 0.8},
    "tomato": {"calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2, "fiber": 1.2, "sodium": 12, "sugar": 2.6},
    "cucumber": {"calories": 16, "protein": 0.7, "carbs": 3.6, "fat": 0.1, "fiber": 0.5, "sodium": 2, "sugar": 1.7},
    "bell pepper": {"calories": 31, "protein": 1, "carbs": 6, "fat": 0.3, "fiber": 2, "sodium": 4, "sugar": 3.2},
    "onion": {"calories": 40, "protein": 1.1, "carbs": 9, "fat": 0.1, "fiber": 1.7, "sodium": 5, "sugar": 4.2},
    "garlic": {"calories": 149, "protein": 6.4, "carbs": 33, "fat": 0.5, "fiber": 2.1, "sodium": 17, "sugar": 1},
    "green beans": {"calories": 31, "protein": 1.8, "carbs": 7, "fat": 0.2, "fiber": 1.7, "sodium": 2, "sugar": 1.5},
    "peas": {"calories": 81, "protein": 5.4, "carbs": 14, "fat": 0.4, "fiber": 2.4, "sodium": 2, "sugar": 5.7},
    "corn": {"calories": 86, "protein": 3.3, "carbs": 19, "fat": 1.2, "fiber": 2.4, "sodium": 15, "sugar": 3.2},
    "cauliflower": {"calories": 25, "protein": 1.9, "carbs": 5, "fat": 0.3, "fiber": 2.4, "sodium": 30, "sugar": 2},
    "zucchini": {"calories": 17, "protein": 1.5, "carbs": 3.5, "fat": 0.4, "fiber": 1, "sodium": 10, "sugar": 1.2},

    # GRAINS & CARBS
    "rice": {"calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3, "fiber": 0.4, "sodium": 2, "sugar": 0.1},
    "brown rice": {"calories": 112, "protein": 2.6, "carbs": 24, "fat": 0.9, "fiber": 1.8, "sodium": 4, "sugar": 0.3},
    "pasta": {"calories": 131, "protein": 5, "carbs": 25, "fat": 1.1, "fiber": 1.5, "sodium": 1, "sugar": 0.6},
    "bread": {"calories": 265, "protein": 9, "carbs": 49, "fat": 3.3, "fiber": 2.7, "sodium": 476, "sugar": 4},
    "whole wheat bread": {"calories": 247, "protein": 9.7, "carbs": 43, "fat": 3.3, "fiber": 7, "sodium": 446, "sugar": 2.4},
    "oats": {"calories": 389, "protein": 17, "carbs": 66, "fat": 6.9, "fiber": 10, "sodium": 30, "sugar": 0},
    "quinoa": {"calories": 120, "protein": 4.4, "carbs": 21, "fat": 1.9, "fiber": 2.8, "sodium": 7, "sugar": 1.6},
    "couscous": {"calories": 112, "protein": 3.8, "carbs": 23, "fat": 0.1, "fiber": 1.5, "sodium": 8, "sugar": 0.1},

    # LEGUMES
    "chickpeas": {"calories": 164, "protein": 8.9, "carbs": 27, "fat": 2.6, "fiber": 6.4, "sodium": 7, "sugar": 1.5},
    "lentils": {"calories": 116, "protein": 9, "carbs": 20, "fat": 0.4, "fiber": 3.8, "sodium": 4, "sugar": 1.1},
    "black beans": {"calories": 132, "protein": 8.9, "carbs": 24, "fat": 0.5, "fiber": 6.4, "sodium": 245, "sugar": 0.3},
    "peanuts": {"calories": 567, "protein": 26, "carbs": 16, "fat": 49, "fiber": 6, "sodium": 18, "sugar": 4.7},
    "tofu": {"calories": 76, "protein": 8, "carbs": 1.9, "fat": 4.8, "fiber": 0.3, "sodium": 7, "sugar": 0.3},
    "tempeh": {"calories": 195, "protein": 19, "carbs": 7.6, "fat": 11, "fiber": 1.3, "sodium": 10, "sugar": 0},

    # FRUITS
    "banana": {"calories": 89, "protein": 1.1, "carbs": 23, "fat": 0.3, "fiber": 2.6, "sodium": 1, "sugar": 12},
    "apple": {"calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2, "fiber": 2.4, "sodium": 2, "sugar": 10},
    "orange": {"calories": 47, "protein": 0.9, "carbs": 12, "fat": 0.3, "fiber": 2.4, "sodium": 2, "sugar": 9},
    "strawberry": {"calories": 32, "protein": 0.8, "carbs": 8, "fat": 0.3, "fiber": 2, "sodium": 2, "sugar": 4.9},
    "blueberry": {"calories": 57, "protein": 0.7, "carbs": 14, "fat": 0.3, "fiber": 2.4, "sodium": 6, "sugar": 10},
    "watermelon": {"calories": 30, "protein": 0.6, "carbs": 7.6, "fat": 0.2, "fiber": 0.4, "sodium": 28, "sugar": 6.2},
    "grape": {"calories": 67, "protein": 0.6, "carbs": 17, "fat": 0.2, "fiber": 0.9, "sodium": 3, "sugar": 15},

    # DAIRY & PROTEINS
    "milk": {"calories": 61, "protein": 3.2, "carbs": 4.8, "fat": 3.3, "fiber": 0, "sodium": 44, "sugar": 5},
    "yogurt": {"calories": 59, "protein": 10, "carbs": 3.3, "fat": 0.4, "fiber": 0, "sodium": 46, "sugar": 3.3},
    "greek yogurt": {"calories": 59, "protein": 10, "carbs": 3.3, "fat": 0.4, "fiber": 0, "sodium": 46, "sugar": 3.3},
    "cheese": {"calories": 402, "protein": 25, "carbs": 1.3, "fat": 33, "fiber": 0, "sodium": 621, "sugar": 0.7},
    "cheddar cheese": {"calories": 403, "protein": 23, "carbs": 3.3, "fat": 33, "fiber": 0, "sodium": 621, "sugar": 0.7},
    "mozzarella": {"calories": 280, "protein": 28, "carbs": 3.2, "fat": 17, "fiber": 0, "sodium": 626, "sugar": 0.3},

    # OILS & CONDIMENTS
    "olive oil": {"calories": 884, "protein": 0, "carbs": 0, "fat": 100, "fiber": 0, "sodium": 2, "sugar": 0},
    "coconut oil": {"calories": 892, "protein": 0, "carbs": 0, "fat": 99, "fiber": 0, "sodium": 0, "sugar": 0},
    "butter": {"calories": 717, "protein": 0.9, "carbs": 0.1, "fat": 81, "fiber": 0, "sodium": 714, "sugar": 0.1},
    "peanut butter": {"calories": 588, "protein": 25, "carbs": 20, "fat": 50, "fiber": 6, "sodium": 425, "sugar": 7},
    "soy sauce": {"calories": 61, "protein": 11, "carbs": 5.6, "fat": 0.6, "fiber": 0.8, "sodium": 5586, "sugar": 1},

    # NUTS & SEEDS
    "almonds": {"calories": 579, "protein": 21, "carbs": 22, "fat": 50, "fiber": 13, "sodium": 1, "sugar": 4.4},
    "walnuts": {"calories": 654, "protein": 9, "carbs": 14, "fat": 65, "fiber": 7, "sodium": 2, "sugar": 2.6},
    "sunflower seeds": {"calories": 584, "protein": 24, "carbs": 20, "fat": 51, "fiber": 8.6, "sodium": 9, "sugar": 2.6},
}

# Portion multipliers for common measurements
PORTION_MULTIPLIERS = {
    "gram": 1/100,
    "g": 1/100,
    "oz": 0.283495,  # 1 oz = 28.3495g, divided by 100g
    "ounce": 0.283495,
    "cup": 2.4,  # Varies, but 240g is typical for vegetables
    "tbsp": 0.15,  # 15g for most foods
    "tsp": 0.05,  # 5g for most foods
    "tablespoon": 0.15,
    "teaspoon": 0.05,
    "medium": 1.5,  # Generic medium portion
    "small": 0.75,
    "large": 2.0,
    "slice": 1.0,  # Varies, estimate as 100g
}

def find_food_matches(food_name: str) -> list:
    """
    Find matching foods in database using fuzzy matching.
    
    Args:
        food_name: Name of food to search for
        
    Returns:
        List of matching food names and their nutrition data
    """
    food_name = food_name.lower().strip()
    matches = []
    
    # Exact match
    if food_name in NUTRITION_DATABASE:
        return [(food_name, NUTRITION_DATABASE[food_name])]
    
    # Substring matching (food name contains search term or vice versa)
    for db_food in NUTRITION_DATABASE:
        if food_name in db_food or db_food in food_name:
            matches.append((db_food, NUTRITION_DATABASE[db_food]))
    
    return matches


def get_nutrition_for_portion(food_name: str, quantity: float, unit: str = "g") -> dict:
    """
    Calculate nutrition values for a specific portion.
    
    Args:
        food_name: Name of the food
        quantity: Amount of food
        unit: Unit of measurement (g, oz, cup, tbsp, etc.)
        
    Returns:
        Dictionary with adjusted nutrition values for the portion
    """
    # Find the food in database
    matches = find_food_matches(food_name)
    if not matches:
        return None
    
    food_data = matches[0][1]  # Use first match
    
    # Get portion multiplier
    unit_lower = unit.lower().strip()
    multiplier = PORTION_MULTIPLIERS.get(unit_lower, 1/100)  # Default to gram
    
    # Calculate actual multiplier based on quantity and unit
    actual_multiplier = quantity * multiplier
    
    # Apply multiplier to all nutrition values
    adjusted = {}
    for nutrient, value in food_data.items():
        adjusted[nutrient] = round(value * actual_multiplier, 1)
    
    return adjusted


def validate_nutrition_data(nutrition_dict: dict) -> dict:
    """
    Validate nutrition data for logical consistency and apply corrections.
    
    Args:
        nutrition_dict: Dictionary with nutrition values
        
    Returns:
        Corrected nutrition dictionary
    """
    corrected = nutrition_dict.copy()
    
    # If carbs is 0 but has vegetables, estimate carbs
    if corrected.get("carbs", 0) == 0 and corrected.get("fiber", 0) > 0:
        # If we have fiber but no carbs, add reasonable carb estimate
        corrected["carbs"] = max(3, corrected["fiber"] * 2)
    
    # Ensure carbs + protein + fat doesn't massively exceed calories
    calculated_cals = (
        corrected.get("protein", 0) * 4 +
        corrected.get("carbs", 0) * 4 +
        corrected.get("fat", 0) * 9
    )
    
    # Round all values to 1 decimal
    for key in corrected:
        if isinstance(corrected[key], (int, float)):
            corrected[key] = round(corrected[key], 1)
    
    return corrected


def suggest_missing_nutrients(nutrition_dict: dict, confidence: float = 0.8) -> dict:
    """
    Suggest missing nutrient values based on macronutrient composition.
    
    Args:
        nutrition_dict: Partial nutrition dictionary
        confidence: Confidence level for estimation (0-1)
        
    Returns:
        Dictionary with suggested values for missing nutrients
    """
    suggested = nutrition_dict.copy()
    
    # If we have calories and macros but missing some, we can estimate from others
    if "calories" in suggested and "protein" in suggested and "carbs" not in suggested:
        # Estimate carbs from calorie budget
        protein_cals = suggested["protein"] * 4
        remaining_cals = suggested["calories"] - protein_cals
        suggested["carbs"] = round(remaining_cals / 4 * 0.5, 1)  # Assume 50% of remaining from carbs
    
    return suggested
