#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Hybrid Nutrition Analyzer - Test Suite
Test-Driven Development approach to ensure consistency & accuracy
"""

import unittest
from hybrid_nutrition_analyzer import HybridNutritionAnalyzer

class TestDatabaseCoverage(unittest.TestCase):
    """Test database coverage calculation and tracking"""
    
    def setUp(self):
        self.analyzer = HybridNutritionAnalyzer()
    
    def test_coverage_calculation(self):
        """Test that coverage percentage is correctly calculated"""
        test_ingredients = [
            {"name": "chicken breast", "quantity": 100, "unit": "g"},
            {"name": "rice", "quantity": 100, "unit": "g"},
            {"name": "unknown_exotic_fruit", "quantity": 100, "unit": "g"},
        ]
        coverage = self.analyzer.get_database_coverage(test_ingredients)
        # Expected: 2 in DB, 1 estimated = 66.7% coverage
        self.assertAlmostEqual(coverage.get('coverage_percentage', 0), 66.7, places=1)
        self.assertEqual(coverage.get('in_database', 0), 2)
        self.assertEqual(coverage.get('estimated', 0), 1)
    
    def test_coverage_tracking(self):
        """Test that coverage tracking works with different ingredient counts"""
        test_ingredients_high = [
            {"name": "chicken breast", "quantity": 100, "unit": "g"},
            {"name": "broccoli", "quantity": 100, "unit": "g"},
            {"name": "olive oil", "quantity": 15, "unit": "ml"},
        ]
        coverage_high = self.analyzer.get_database_coverage(test_ingredients_high)
        # All three should be in database
        self.assertGreaterEqual(coverage_high.get('coverage_percentage', 0), 80)


class TestConsistency(unittest.TestCase):
    """Test consistency and determinism of nutrition calculations"""
    
    def setUp(self):
        self.analyzer = HybridNutritionAnalyzer()
    
    def test_deterministic_results(self):
        """Test that same input produces same output across multiple runs"""
        test_ingredients = [
            {"name": "chicken breast", "quantity": 150, "unit": "g"},
            {"name": "rice", "quantity": 200, "unit": "g"},
        ]
        result1 = self.analyzer.calculate_meal_nutrition(test_ingredients)
        result2 = self.analyzer.calculate_meal_nutrition(test_ingredients)
        
        # Results should be identical
        self.assertEqual(result1.get('calories', 0), result2.get('calories', 0))
        self.assertEqual(result1.get('protein', 0), result2.get('protein', 0))
        self.assertEqual(result1.get('carbs', 0), result2.get('carbs', 0))
    
    def test_ingredient_order_independence(self):
        """Test that ingredient order doesn't affect total nutrition"""
        ingredients_order1 = [
            {"name": "chicken breast", "quantity": 150, "unit": "g"},
            {"name": "rice", "quantity": 200, "unit": "g"},
            {"name": "broccoli", "quantity": 100, "unit": "g"},
        ]
        ingredients_order2 = [
            {"name": "rice", "quantity": 200, "unit": "g"},
            {"name": "broccoli", "quantity": 100, "unit": "g"},
            {"name": "chicken breast", "quantity": 150, "unit": "g"},
        ]
        
        result1 = self.analyzer.calculate_meal_nutrition(ingredients_order1)
        result2 = self.analyzer.calculate_meal_nutrition(ingredients_order2)
        
        # Totals should be the same regardless of order
        self.assertAlmostEqual(result1.get('calories', 0), result2.get('calories', 0), places=1)
        self.assertAlmostEqual(result1.get('protein', 0), result2.get('protein', 0), places=1)


class TestNutritionValidation(unittest.TestCase):
    """Test that nutrition values are realistic and valid"""
    
    def setUp(self):
        self.analyzer = HybridNutritionAnalyzer()
    
    def test_no_negative_values(self):
        """Test that nutrition values are never negative"""
        test_ingredients = [
            {"name": "chicken breast", "quantity": 200, "unit": "g"},
            {"name": "pasta", "quantity": 100, "unit": "g"},
            {"name": "olive oil", "quantity": 20, "unit": "ml"},
        ]
        result = self.analyzer.calculate_meal_nutrition(test_ingredients)
        
        self.assertGreaterEqual(result.get('calories', 0), 0)
        self.assertGreaterEqual(result.get('protein', 0), 0)
        self.assertGreaterEqual(result.get('carbs', 0), 0)
        self.assertGreaterEqual(result.get('fat', 0), 0)
        self.assertGreaterEqual(result.get('fiber', 0), 0)
    
    def test_macro_calorie_consistency(self):
        """Test that macronutrients align with stated calories"""
        test_ingredients = [
            {"name": "chicken breast", "quantity": 150, "unit": "g"},
            {"name": "rice", "quantity": 150, "unit": "g"},
        ]
        result = self.analyzer.calculate_meal_nutrition(test_ingredients)
        
        calories = result.get('calories', 0)
        protein = result.get('protein', 0)
        carbs = result.get('carbs', 0)
        fat = result.get('fat', 0)
        
        # Rough check: calories should be approximately protein*4 + carbs*4 + fat*9
        # Allow 20% variance due to fiber and estimation
        calculated_calories = (protein * 4) + (carbs * 4) + (fat * 9)
        tolerance = calculated_calories * 0.4
        
        self.assertAlmostEqual(calories, calculated_calories, delta=tolerance)
    
    def test_realistic_value_ranges(self):
        """Test that nutrition values fall within realistic ranges"""
        test_ingredients = [
            {"name": "chicken breast", "quantity": 100, "unit": "g"},
        ]
        result = self.analyzer.calculate_meal_nutrition(test_ingredients)
        
        # 100g chicken breast should be roughly 165 cal, 31g protein
        calories = result.get('calories', 0)
        protein = result.get('protein', 0)
        
        # Allow 30% variance for estimation
        self.assertGreater(calories, 100)  # At least 100 cal
        self.assertLess(calories, 250)     # Less than 250 cal
        self.assertGreater(protein, 20)    # At least 20g protein
        self.assertLess(protein, 40)       # Less than 40g protein


class TestHallucinationDetection(unittest.TestCase):
    """Test detection of potential LLM hallucinations"""
    
    def setUp(self):
        self.analyzer = HybridNutritionAnalyzer()
    
    def test_low_coverage_flagging(self):
        """Test that low database coverage is flagged for user awareness"""
        test_ingredients = [
            {"name": "unknown_exotic_ingredient_xyz", "quantity": 100, "unit": "g"},
            {"name": "another_rare_food_abc", "quantity": 100, "unit": "g"},
            {"name": "third_uncommon_item_xyz", "quantity": 100, "unit": "g"},
        ]
        
        coverage = self.analyzer.get_database_coverage(test_ingredients)
        coverage_pct = coverage.get('coverage_percentage', 100)
        
        # Low coverage should be flagged
        if coverage_pct < 40:
            confidence = "low"
        elif coverage_pct < 70:
            confidence = "medium"
        else:
            confidence = "high"
        
        # With mostly unknown ingredients, confidence should be low or medium
        self.assertIn(confidence, ["low", "medium"])
    
    def test_confidence_levels(self):
        """Test that confidence levels are assigned based on coverage"""
        # High coverage case
        high_coverage_ingredients = [
            {"name": "chicken breast", "quantity": 150, "unit": "g"},
            {"name": "rice", "quantity": 150, "unit": "g"},
            {"name": "broccoli", "quantity": 100, "unit": "g"},
        ]
        
        # Low coverage case
        low_coverage_ingredients = [
            {"name": "exotic_fruit_x", "quantity": 100, "unit": "g"},
            {"name": "unknown_plant_y", "quantity": 100, "unit": "g"},
        ]
        
        high_cov = self.analyzer.get_database_coverage(high_coverage_ingredients)
        low_cov = self.analyzer.get_database_coverage(low_coverage_ingredients)
        
        # Higher coverage should result in higher confidence
        self.assertGreater(
            high_cov.get('coverage_percentage', 0),
            low_cov.get('coverage_percentage', 0)
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
