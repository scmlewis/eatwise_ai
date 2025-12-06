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

# Test data: diverse meals from different cuisines, countries, and sources
TEST_MEALS = [
    # Western / American
    {
        "description": "Grilled chicken breast with brown rice and steamed broccoli",
        "meal_type": "lunch",
        "origin": "American",
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
        "origin": "American",
        "expected_ranges": {
            "calories": (300, 400),
            "protein": (12, 18),
            "carbs": (35, 50),
            "fat": (8, 15),
        }
    },
    
    # Asian - Japan
    {
        "description": "Salmon sushi (6 pieces) with soy sauce",
        "meal_type": "lunch",
        "origin": "Japanese",
        "expected_ranges": {
            "calories": (200, 300),
            "protein": (15, 25),
            "carbs": (20, 35),
            "fat": (8, 15),
        }
    },
    {
        "description": "Miso soup with tofu, seaweed, and green onions",
        "meal_type": "breakfast",
        "origin": "Japanese",
        "expected_ranges": {
            "calories": (80, 150),
            "protein": (5, 12),
            "carbs": (8, 18),
            "fat": (2, 8),
        }
    },
    
    # Asian - China
    {
        "description": "Kung Pao chicken with cashews and vegetables over white rice",
        "meal_type": "lunch",
        "origin": "Chinese",
        "expected_ranges": {
            "calories": (450, 600),
            "protein": (25, 35),
            "carbs": (45, 65),
            "fat": (12, 25),
        }
    },
    {
        "description": "Mapo tofu with rice and bok choy",
        "meal_type": "dinner",
        "origin": "Chinese",
        "expected_ranges": {
            "calories": (350, 450),
            "protein": (15, 25),
            "carbs": (40, 55),
            "fat": (10, 20),
        }
    },
    
    # Asian - Thailand
    {
        "description": "Thai green curry with shrimp, coconut milk, and jasmine rice",
        "meal_type": "lunch",
        "origin": "Thai",
        "expected_ranges": {
            "calories": (400, 550),
            "protein": (20, 30),
            "carbs": (40, 60),
            "fat": (15, 25),
        }
    },
    {
        "description": "Pad Thai with shrimp, peanuts, and lime",
        "meal_type": "lunch",
        "origin": "Thai",
        "expected_ranges": {
            "calories": (400, 550),
            "protein": (18, 28),
            "carbs": (45, 65),
            "fat": (12, 22),
        }
    },
    
    # Asian - India
    {
        "description": "Chicken tikka masala with basmati rice and naan bread",
        "meal_type": "dinner",
        "origin": "Indian",
        "expected_ranges": {
            "calories": (500, 700),
            "protein": (25, 35),
            "carbs": (50, 75),
            "fat": (15, 28),
        }
    },
    {
        "description": "Chana masala (chickpea curry) with brown rice and cucumber raita",
        "meal_type": "lunch",
        "origin": "Indian",
        "expected_ranges": {
            "calories": (350, 450),
            "protein": (12, 18),
            "carbs": (50, 70),
            "fat": (8, 15),
        }
    },
    
    # Mediterranean / Greek
    {
        "description": "Greek salad with feta cheese, olives, tomatoes, and olive oil dressing",
        "meal_type": "lunch",
        "origin": "Greek",
        "expected_ranges": {
            "calories": (250, 350),
            "protein": (8, 15),
            "carbs": (15, 25),
            "fat": (18, 28),
        }
    },
    {
        "description": "Grilled fish (sea bass) with lemon, olive oil, and Greek vegetables",
        "meal_type": "dinner",
        "origin": "Greek",
        "expected_ranges": {
            "calories": (300, 400),
            "protein": (35, 45),
            "carbs": (5, 15),
            "fat": (10, 18),
        }
    },
    
    # Mediterranean / Italian
    {
        "description": "Pasta carbonara with guanciale and parmesan cheese",
        "meal_type": "lunch",
        "origin": "Italian",
        "expected_ranges": {
            "calories": (500, 700),
            "protein": (18, 26),
            "carbs": (50, 70),
            "fat": (20, 32),
        }
    },
    {
        "description": "Margherita pizza with fresh mozzarella, basil, and tomatoes",
        "meal_type": "lunch",
        "origin": "Italian",
        "expected_ranges": {
            "calories": (400, 550),
            "protein": (12, 20),
            "carbs": (45, 65),
            "fat": (15, 25),
        }
    },
    
    # Middle Eastern
    {
        "description": "Falafel wrap with hummus, tahini, lettuce, and tomato",
        "meal_type": "lunch",
        "origin": "Middle Eastern",
        "expected_ranges": {
            "calories": (350, 450),
            "protein": (10, 16),
            "carbs": (40, 55),
            "fat": (12, 22),
        }
    },
    {
        "description": "Kebab with lamb, grilled vegetables, and tzatziki sauce",
        "meal_type": "dinner",
        "origin": "Middle Eastern",
        "expected_ranges": {
            "calories": (450, 600),
            "protein": (30, 40),
            "carbs": (20, 35),
            "fat": (18, 28),
        }
    },
    
    # Latin American / Mexican
    {
        "description": "Ceviche with shrimp, lime juice, cilantro, and avocado",
        "meal_type": "lunch",
        "origin": "Peruvian/Mexican",
        "expected_ranges": {
            "calories": (250, 350),
            "protein": (25, 35),
            "carbs": (15, 25),
            "fat": (10, 18),
        }
    },
    {
        "description": "Burrito with ground beef, black beans, rice, cheese, and salsa",
        "meal_type": "lunch",
        "origin": "Mexican",
        "expected_ranges": {
            "calories": (500, 700),
            "protein": (20, 30),
            "carbs": (55, 75),
            "fat": (15, 28),
        }
    },
    {
        "description": "Chiles rellenos with cheese and tomato sauce",
        "meal_type": "dinner",
        "origin": "Mexican",
        "expected_ranges": {
            "calories": (400, 550),
            "protein": (12, 20),
            "carbs": (35, 50),
            "fat": (20, 32),
        }
    },
    
    # African
    {
        "description": "Jollof rice with chicken and tomato-pepper sauce",
        "meal_type": "lunch",
        "origin": "West African",
        "expected_ranges": {
            "calories": (400, 550),
            "protein": (22, 32),
            "carbs": (45, 65),
            "fat": (10, 20),
        }
    },
    {
        "description": "Tagine with lamb, apricots, and almonds served with couscous",
        "meal_type": "dinner",
        "origin": "Moroccan",
        "expected_ranges": {
            "calories": (450, 600),
            "protein": (28, 38),
            "carbs": (45, 60),
            "fat": (15, 25),
        }
    },
    
    # Vegetarian / Vegan (from multiple origins)
    {
        "description": "Apple with peanut butter",
        "meal_type": "snack",
        "origin": "Vegan",
        "expected_ranges": {
            "calories": (200, 300),
            "protein": (4, 8),
            "carbs": (30, 40),
            "fat": (8, 12),
        }
    },
    {
        "description": "Buddha bowl with quinoa, chickpeas, roasted vegetables, and tahini dressing",
        "meal_type": "lunch",
        "origin": "Vegan",
        "expected_ranges": {
            "calories": (400, 550),
            "protein": (15, 25),
            "carbs": (50, 70),
            "fat": (12, 22),
        }
    },
    {
        "description": "Vegetable stir-fry with tofu, broccoli, snap peas, and ginger-soy sauce over brown rice",
        "meal_type": "lunch",
        "origin": "Vegetarian Asian-Fusion",
        "expected_ranges": {
            "calories": (350, 450),
            "protein": (15, 25),
            "carbs": (40, 60),
            "fat": (8, 16),
        }
    },
    
    # Fast Food / Casual
    {
        "description": "Hamburger with lettuce, tomato, onion, and french fries",
        "meal_type": "lunch",
        "origin": "Fast Food",
        "expected_ranges": {
            "calories": (550, 750),
            "protein": (15, 25),
            "carbs": (55, 75),
            "fat": (20, 35),
        }
    },
    {
        "description": "Chicken sandwich with coleslaw and pickles",
        "meal_type": "lunch",
        "origin": "Casual American",
        "expected_ranges": {
            "calories": (400, 550),
            "protein": (20, 30),
            "carbs": (40, 60),
            "fat": (15, 28),
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
    """Test meal nutrition analysis on diverse cuisines"""
    print("\n" + "="*70)
    print("NUTRITION ANALYSIS VALIDATION - DIVERSE CUISINES TEST")
    print("="*70 + "\n")
    print(f"Testing {len(TEST_MEALS)} meals across multiple cuisines and countries...")
    
    results = {
        "total": len(TEST_MEALS),
        "passed": 0,
        "warnings": 0,
        "failed": 0,
        "by_cuisine": {}
    }
    
    failed_details = []
    
    for i, meal in enumerate(TEST_MEALS, 1):
        description = meal['description']
        meal_type = meal['meal_type']
        origin = meal.get('origin', 'Unknown')
        
        # Track by cuisine
        if origin not in results["by_cuisine"]:
            results["by_cuisine"][origin] = {"total": 0, "passed": 0}
        results["by_cuisine"][origin]["total"] += 1
        
        print(f"\n[Test {i}/{len(TEST_MEALS)}] [{origin}] {description}")
        print(f"  Type: {meal_type}")
        
        try:
            analysis = analyzer.analyze_text_meal(description, meal_type)
            
            if not analysis:
                print(f"  [FAILED] No analysis returned")
                results["failed"] += 1
                failed_details.append((i, origin, description, "No analysis returned"))
                continue
            
            nutrition = analysis.get("nutrition", {})
            print(f"  [OK] Analysis received")
            
            # Validate nutrition values
            is_valid, issues = validate_nutrition_values(nutrition, meal['expected_ranges'])
            
            # Display nutrition breakdown
            print(f"  [NUTRITION]")
            print(f"     Calories: {nutrition.get('calories', 0):.0f} cal")
            print(f"     Protein: {nutrition.get('protein', 0):.1f}g | Carbs: {nutrition.get('carbs', 0):.1f}g | Fat: {nutrition.get('fat', 0):.1f}g")
            
            healthiness = analysis.get("healthiness_score", 0)
            health_notes = analysis.get("health_notes", "N/A")
            print(f"  [SCORE] Healthiness: {healthiness}/100")
            if health_notes and health_notes != "N/A":
                notes_short = (health_notes[:60] + "...") if len(health_notes) > 60 else health_notes
                print(f"  [NOTES] {notes_short}")
            
            if issues:
                print(f"  [ISSUES] {len(issues)} warning(s):")
                for issue in issues[:2]:  # Show first 2 issues
                    print(issue)
                results["warnings"] += 1
                print(f"  [RESULT] PASSED with warnings")
            else:
                results["passed"] += 1
                results["by_cuisine"][origin]["passed"] += 1
                print(f"  [RESULT] PASSED validation")
                
        except KeyboardInterrupt:
            print(f"  [INTERRUPTED] Test interrupted by user")
            break
        except Exception as e:
            print(f"  [ERROR] {str(e)[:100]}")
            results["failed"] += 1
            failed_details.append((i, origin, description, str(e)[:60]))
    
    # Summary by cuisine
    print("\n" + "="*70)
    print("RESULTS BY CUISINE")
    print("="*70)
    for cuisine in sorted(results["by_cuisine"].keys()):
        stats = results["by_cuisine"][cuisine]
        pass_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        status = "[OK]" if pass_rate == 100 else "[PARTIAL]" if pass_rate > 0 else "[FAILED]"
        print(f"  {status} {cuisine:25} {stats['passed']}/{stats['total']} passed ({pass_rate:.0f}%)")
    
    # Overall summary
    print("\n" + "="*70)
    print("TEST SUMMARY - OVERALL")
    print("="*70)
    print(f"Total Cuisines Tested:   {len(results['by_cuisine'])}")
    print(f"Total Meals Analyzed:    {results['total']}")
    print(f"Passed:                  {results['passed']} [OK]")
    print(f"Passed with Warnings:    {results['warnings']} [WARN]")
    print(f"Failed:                  {results['failed']} [FAIL]")
    
    if results['total'] > 0:
        pass_rate = (results['passed'] / results['total'] * 100)
        print(f"\nOverall Pass Rate:       {pass_rate:.1f}%")
    
    if failed_details:
        print(f"\n[FAILURES] ({len(failed_details)}):")
        for idx, cuisine, desc, reason in failed_details:
            desc_short = (desc[:45] + "...") if len(desc) > 45 else desc
            print(f"   [{idx}] [{cuisine}] {desc_short}")
            print(f"       {reason}")
    
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
    # Set encoding for emoji support on Windows
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("\n[NUTRITION VALIDATION TEST SUITE]\n")
    
    try:
        # Run tests
        test_result = test_nutrition_analysis()
        calc_result = test_percentage_calculation()
        
        # Exit with success if all tests passed
        sys.exit(test_result or calc_result)
        
    except Exception as e:
        print(f"\n[ERROR] Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
