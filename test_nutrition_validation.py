#!/usr/bin/env python
"""
Test script to validate nutrition analysis output makes sense.
Tests meal analysis, nutrition calculations, and healthiness scoring.
"""

import json
import sys
from nutrition_analyzer import NutritionAnalyzer
from nutrition_components import get_nutrition_color, calculate_nutrition_percentage
from utils import calculate_nutrition_percentage as utils_calc_percentage

# Initialize analyzer
analyzer = NutritionAnalyzer()

# Test data: common meals with expected ranges
TEST_MEALS = [
    {
        "description": "Grilled chicken breast with brown rice and steamed broccoli",
        "meal_type": "lunch",
        "expected_ranges": {
            "calories": (350, 450),
            "protein": (30, 40),
            "carbs": (40, 55),
            "fat": (5, 15),
        }
    },
    {
        "description": "Two eggs with whole wheat toast and orange juice",
        "meal_type": "breakfast",
        "expected_ranges": {
            "calories": (300, 400),
            "protein": (12, 18),
            "carbs": (35, 50),
            "fat": (8, 15),
        }
    },
    {
        "description": "Apple with peanut butter",
        "meal_type": "snack",
        "expected_ranges": {
            "calories": (200, 300),
            "protein": (4, 8),
            "carbs": (30, 40),
            "fat": (8, 12),
        }
    },
    {
        "description": "Salmon sushi (6 pieces) with soy sauce",
        "meal_type": "lunch",
        "expected_ranges": {
            "calories": (200, 300),
            "protein": (15, 25),
            "carbs": (20, 35),
            "fat": (8, 15),
        }
    },
]

def validate_nutrition_values(nutrition: dict, expected_ranges: dict) -> tuple[bool, list]:
    """
    Validate nutrition values are within expected ranges.
    
    Returns:
        (is_valid, issues) where issues is a list of validation problems
    """
    issues = []
    
    for nutrient, (min_val, max_val) in expected_ranges.items():
        actual = nutrition.get(nutrient, 0)
        
        # Check if value is within reasonable range
        if actual < min_val * 0.7:  # Allow 30% below expected
            issues.append(f"  ⚠️  {nutrient}: {actual} is significantly below expected range ({min_val}-{max_val})")
        elif actual > max_val * 1.5:  # Allow 50% above expected
            issues.append(f"  ⚠️  {nutrient}: {actual} exceeds expected range ({min_val}-{max_val})")
    
    # Check nutritional sanity
    calories = nutrition.get("calories", 0)
    protein = nutrition.get("protein", 0)
    carbs = nutrition.get("carbs", 0)
    fat = nutrition.get("fat", 0)
    
    # Calculate macronutrient calories
    macro_calories = (protein * 4) + (carbs * 4) + (fat * 9)
    calorie_diff_percent = abs(macro_calories - calories) / max(calories, 1) * 100
    
    if calorie_diff_percent > 30:
        issues.append(f"  ⚠️  Macro-calorie mismatch: calculated {macro_calories}cal from macros but reported {calories}cal (diff: {calorie_diff_percent:.1f}%)")
    
    # Check for negative values
    for nutrient, value in nutrition.items():
        if value < 0:
            issues.append(f"  ❌ {nutrient}: negative value {value}")
    
    # Check healthiness score range
    healthiness = nutrition.get("healthiness_score", 0)
    if healthiness < 0 or healthiness > 100:
        issues.append(f"  ❌ Healthiness score {healthiness} outside 0-100 range")
    
    return len(issues) == 0, issues

def test_nutrition_analysis():
    """Test meal nutrition analysis"""
    print("\n" + "="*70)
    print("NUTRITION ANALYSIS VALIDATION TEST")
    print("="*70)
    
    results = {
        "total": len(TEST_MEALS),
        "passed": 0,
        "warnings": 0,
        "failed": 0
    }
    
    for i, meal in enumerate(TEST_MEALS, 1):
        print(f"\n[Test {i}/{len(TEST_MEALS)}] Analyzing: {meal['description']}")
        print(f"  Type: {meal['meal_type']}")
        
        try:
            analysis = analyzer.analyze_text_meal(meal['description'], meal['meal_type'])
            
            if not analysis:
                print(f"  ❌ FAILED: No analysis returned")
                results["failed"] += 1
                continue
            
            nutrition = analysis.get("nutrition", {})
            print(f"  ✓ Analysis received")
            
            # Validate nutrition values
            is_valid, issues = validate_nutrition_values(nutrition, meal['expected_ranges'])
            
            # Display nutrition breakdown
            print(f"\n  Nutrition Values:")
            print(f"    • Calories: {nutrition.get('calories', 0):.0f} cal")
            print(f"    • Protein: {nutrition.get('protein', 0):.1f}g")
            print(f"    • Carbs: {nutrition.get('carbs', 0):.1f}g")
            print(f"    • Fat: {nutrition.get('fat', 0):.1f}g")
            print(f"    • Sodium: {nutrition.get('sodium', 0):.0f}mg")
            print(f"    • Sugar: {nutrition.get('sugar', 0):.1f}g")
            print(f"    • Fiber: {nutrition.get('fiber', 0):.1f}g")
            
            healthiness = analysis.get("healthiness_score", 0)
            print(f"\n  Health Assessment:")
            print(f"    • Healthiness Score: {healthiness}/100")
            print(f"    • Notes: {analysis.get('health_notes', 'N/A')}")
            
            if issues:
                print(f"\n  Issues Found ({len(issues)}):")
                for issue in issues:
                    print(issue)
                results["warnings"] += 1
                print(f"  ⚠️  PASSED with warnings")
            else:
                results["passed"] += 1
                print(f"  ✓ PASSED validation")
                
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            results["failed"] += 1
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total Tests:     {results['total']}")
    print(f"Passed:          {results['passed']} ✓")
    print(f"Warnings:        {results['warnings']} ⚠️")
    print(f"Failed:          {results['failed']} ❌")
    print(f"\nPass Rate:       {(results['passed'] / results['total'] * 100):.1f}%")
    
    # Return exit code based on failures
    return 0 if results['failed'] == 0 else 1

def test_percentage_calculation():
    """Test nutrition percentage calculations"""
    print("\n" + "="*70)
    print("NUTRITION PERCENTAGE CALCULATION TEST")
    print("="*70)
    
    test_cases = [
        (1500, 2000, 75.0, "Below target"),
        (2000, 2000, 100.0, "At target"),
        (2500, 2000, 125.0, "Above target"),
        (0, 2000, 0.0, "Zero consumption"),
    ]
    
    print("\nTesting percentage calculations:")
    all_pass = True
    
    for current, target, expected, desc in test_cases:
        result = calculate_nutrition_percentage(current, target)
        status = "✓" if abs(result - expected) < 0.1 else "❌"
        if abs(result - expected) > 0.1:
            all_pass = False
        print(f"  {status} {desc}: {current}/{target} = {result:.1f}% (expected {expected}%)")
    
    # Test color coding
    print("\nTesting nutrition color coding:")
    color_tests = [
        (50.0, "Yellow - Below target"),
        (90.0, "Green - Good"),
        (100.0, "Green - At target"),
        (150.0, "Red - Over target"),
    ]
    
    for percentage, expected_desc in color_tests:
        primary_color, gradient = get_nutrition_color(percentage)
        print(f"  {percentage:.0f}% → {primary_color} (gradient: {gradient})")
    
    return 0 if all_pass else 1

if __name__ == "__main__":
    print("\n🧪 EatWise Nutrition Validation Test Suite\n")
    
    try:
        # Run tests
        test_result = test_nutrition_analysis()
        calc_result = test_percentage_calculation()
        
        # Exit with success if all tests passed
        sys.exit(test_result or calc_result)
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
