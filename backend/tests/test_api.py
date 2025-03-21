import unittest
import json
from app import create_app
from app.services.food_data_service import FoodDataService
from app.services.recommendation_service import RecommendationService

class TestAPIRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test client and initialize services"""
        self.app = create_app()
        self.client = self.app.test_client()
        self.food_service = FoodDataService()
        self.recommendation_service = RecommendationService()

    def test_get_food_impact(self):
        """Test getting food impact data"""
        # Test existing food
        response = self.client.get('/api/impact/Beef')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['food'], 'Beef')
        self.assertIn('carbon', data)
        self.assertIn('environmental_score', data)

        # Test non-existent food
        response = self.client.get('/api/impact/NonExistentFood')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_get_recommendations(self):
        """Test getting food recommendations"""
        response = self.client.get('/api/recommendations/Beef')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['food'], 'Beef')
        self.assertIn('alternatives', data)
        self.assertIsInstance(data['alternatives'], list)

    def test_search_foods(self):
        """Test food search functionality"""
        # Test with valid query
        response = self.client.get('/api/search?q=milk')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertTrue(all('milk' in food.lower() for food in data))

        # Test with empty query
        response = self.client.get('/api/search?q=')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])

        # Test without query parameter
        response = self.client.get('/api/search')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])

if __name__ == '__main__':
    unittest.main()