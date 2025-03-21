import unittest
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app.models.food_model import FoodImpactModel

class TestFoodImpactModel(unittest.TestCase):
    def setUp(self):
        """Initialize the model before each test"""
        self.model = FoodImpactModel()
    
    def test_get_food_impact(self):
        """Test getting impact data for a specific food"""
        beef_impact = self.model.get_food_impact("Beef")
        self.assertIsNotNone(beef_impact)
        self.assertEqual(beef_impact["food"], "Beef")
        self.assertEqual(beef_impact["carbon"], 27.0)
        self.assertTrue("environmental_score" in beef_impact)
    
    def test_predict_impact(self):
        """Test impact prediction for given metrics"""
        # Test high impact food (like beef)
        high_impact = self.model.predict_impact(27.0, 15400, 40.0, 2.5, 9.0)
        self.assertEqual(high_impact, "High")
        
        # Test low impact food (like apple)
        low_impact = self.model.predict_impact(0.3, 50, 0.2, 0.02, 0.1)
        self.assertEqual(low_impact, "Low")
    
    def test_get_all_foods(self):
        """Test getting list of all foods"""
        foods = self.model.get_all_foods()
        self.assertIsInstance(foods, list)
        self.assertGreater(len(foods), 0)
        self.assertIn("Beef", foods)
        self.assertIn("Apple", foods)

if __name__ == '__main__':
    unittest.main()