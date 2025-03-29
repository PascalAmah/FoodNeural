import requests
import random
import json
import os
from app.models.food_model import FoodImpactModel
from app.config import Config

class FoodDataService:
    def __init__(self):
        """Initialize with food impact model"""
        self.model = FoodImpactModel()
        self.foods = self._load_food_data()
        self.impact_cache = {}  
    
    def _load_food_data(self):
        """Load food data from JSON file"""
        try:
            file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'foods.json')
            with open(file_path, 'r') as f:
                data = json.load(f)
                return [food for category in data.values() for food in category]
        except Exception as e:
            print(f"Error loading food data: {e}")
            return []
    
    def get_food_impact(self, food_name, description=None):
        """Get impact data for a food item"""
        cache_key = food_name.lower()
        if cache_key in self.impact_cache:
            return self.impact_cache[cache_key]
        
        impact_data = None
        # Try each data source in sequence
        for fetch_func in [
            lambda: self.model.get_food_impact(food_name, description),
            lambda: self.fetch_from_open_food_facts(food_name),
            lambda: self.fetch_from_usda(food_name)
        ]:
            impact_data = fetch_func()
            if impact_data:
                self.impact_cache[cache_key] = impact_data
                return impact_data
        
        return None
    
    def fetch_from_open_food_facts(self, food_name):
        """Fetch data from Open Food Facts API"""
        try:
            # Use search endpoint with better parameters
            search_url = (
                f"{Config.OPEN_FOOD_FACTS_URL}/cgi/search.pl?"
                f"search_terms={food_name}&json=1&page_size=1&sort_by=popularity"
            )
            response = requests.get(search_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if "products" in data and data["products"]:
                    product = data["products"][0]
                    
                    # Extract real values where possible, fallback to estimates
                    return {
                        "food": product.get("product_name", food_name),
                        "score": self._calculate_environmental_score(product),
                        "breakdown": {
                            "carbon": float(product.get("carbon-footprint_100g", 0)) or random.uniform(0.1, 2.0),
                            "water": float(product.get("water-footprint_100g", 0)) or random.uniform(50, 500),
                            "energy": float(product.get("energy_100g", 0)) / 100 or random.uniform(0.5, 3.0),
                            "waste": random.uniform(0.1, 1.0),
                            "deforestation": self._calculate_deforestation_risk(product)
                        },
                        "ingredients": [
                            ing.strip() 
                            for ing in product.get("ingredients_text", "").split(',')
                            if ing.strip()
                        ],
                        "certifications": product.get("labels", "").split(','),
                        "nutrition": {
                            "protein": product.get("proteins_100g", 0),
                            "fat": product.get("fat_100g", 0),
                            "carbs": product.get("carbohydrates_100g", 0),
                            "fiber": product.get("fiber_100g", 0),
                        }
                    }
            return None
            
        except Exception as e:
            print(f"Error fetching from Open Food Facts: {e}")
            return None
    
    def fetch_from_usda(self, food_name):
        """Fetch data from USDA database"""
        try:
            url = (
                f"{Config.USDA_API_URL}/foods/search?"
                f"query={food_name}&pageSize=1&api_key={Config.USDA_API_KEY}"
            )
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if "foods" in data and data["foods"]:
                    food = data["foods"][0]
                    nutrients = {n['nutrientName']: n['value'] for n in food.get('foodNutrients', [])}
                    
                    return {
                        "food": food.get("description", food_name),
                        "score": self._calculate_environmental_score_usda(food),
                        "breakdown": {
                            "carbon": random.uniform(0.1, 2.5),
                            "water": random.uniform(100, 500),
                            "energy": random.uniform(1, 5),
                            "waste": random.uniform(0.05, 1),
                            "deforestation": self._estimate_deforestation_risk(food_name, food)
                        },
                        "ingredients": [
                            ing.strip() 
                            for ing in food.get("ingredients", "").split(',')
                            if ing.strip()
                        ],
                        "nutrition": {
                            "protein": nutrients.get("Protein", 0),
                            "fat": nutrients.get("Total lipid (fat)", 0),
                            "carbs": nutrients.get("Carbohydrate, by difference", 0),
                            "fiber": nutrients.get("Fiber, total dietary", 0),
                        }
                    }
            return None
            
        except Exception as e:
            print(f"Error fetching from USDA: {e}")
            return None
    
    def fetch_from_barcode(self, barcode):
        """Fetch data from Open Food Facts using a barcode"""
        try:
            response = requests.get(f"{Config.OPEN_FOOD_FACTS_URL}/product/{barcode}.json", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "product" in data:
                    product = data["product"]
                    deforestation_risk = self._calculate_deforestation_risk(product)
                    return {
                        "food": product.get("product_name", "Unknown"),
                        "carbon": product.get("carbon-footprint_100g", random.uniform(0.1, 2.0)),
                        "water": random.uniform(50, 500),
                        "energy": product.get("energy_100g", random.uniform(0.5, 3.0)) / 100,
                        "waste": random.uniform(0.1, 1.0),
                        "deforestation": deforestation_risk,
                        "description": product.get("ingredients_text", "")
                    }
            return None
        except Exception as e:
            print(f"Error fetching barcode data: {e}")
            return None
    
    def _calculate_deforestation_risk(self, product):
        """Calculate deforestation risk based on ingredients and categories"""
        # Expanded list of high-risk items with weighted scores (0-10 scale contribution)
        high_risk_items = {
            # Severe impact (score contribution: 3-4)
            "palm oil": 4, "palm kernel": 4, "palm fat": 4,  # Palm oil derivatives
            "soy": 3, "soya": 3, "soybean": 3,              # Soy products
            "beef": 4, "cattle": 4,                          # Beef production
            # Moderate to high impact (score contribution: 2-3)
            "cocoa": 3, "chocolate": 3,                      # Cocoa farming
            "coffee": 2,                                     # Coffee plantations
            "rubber": 3,                                     # Rubber plantations
            "timber": 3, "wood pulp": 3,                     # Timber-related
            # Moderate impact (score contribution: 1-2)
            "sugar": 2, "sugarcane": 2,                      # Sugarcane farming
            "banana": 1, "plantain": 1,                      # Banana plantations
            "avocado": 2,                                    # Avocado farming
            "corn": 1, "maize": 1,                           # Corn expansion
            "rice": 1,                                       # Rice paddies (some regions)
            "leather": 2                                     # Linked to cattle ranching
        }
        
        ingredients = product.get("ingredients_text", "").lower()
        categories = product.get("categories", "").lower()
        origin = product.get("origins", "").lower()
        
        risk_score = 0
        
        # Check for high-risk items in ingredients or categories
        for item, score in high_risk_items.items():
            if item in ingredients or item in categories:
                risk_score += score
        
        # Bonus risk for known high-deforestation regions (if origin data exists)
        high_risk_regions = ["brazil", "indonesia", "malaysia", "congo", "argentina"]
        if origin and any(region in origin for region in high_risk_regions):
            risk_score += 2  # Additional risk for sourcing from deforestation hotspots
        
        # Cap the score at 10
        return min(risk_score, 10)
    
    def _estimate_deforestation_risk(self, food_name, food_data):
        """Estimate deforestation risk for USDA data"""
        food_name_lower = food_name.lower()
        description = food_data.get("description", "").lower()
        
        # Expanded high-risk items with risk ranges
        high_risk_items = {
            # Severe impact (7-10)
            "beef": (7.0, 10.0), "steak": (7.0, 10.0), "hamburger": (7.0, 10.0), "cattle": (7.0, 10.0),
            "palm oil": (8.0, 10.0), "palm": (8.0, 10.0),
            "soy": (5.0, 8.0), "soya": (5.0, 8.0), "soybean": (5.0, 8.0), "tofu": (4.0, 7.0),
            # Moderate to high impact (4-7)
            "cocoa": (4.0, 7.0), "chocolate": (4.0, 7.0),
            "coffee": (3.0, 6.0),
            "rubber": (4.0, 7.0),
            "timber": (4.0, 7.0), "wood": (4.0, 7.0),
            "sugar": (3.0, 6.0), "sugarcane": (3.0, 6.0),
            "avocado": (3.0, 6.0),
            # Moderate impact (2-5)
            "pork": (2.0, 5.0), "bacon": (2.0, 5.0), "ham": (2.0, 5.0),
            "chicken": (2.0, 4.0), "poultry": (2.0, 4.0),
            "banana": (2.0, 4.0), "plantain": (2.0, 4.0),
            "corn": (1.0, 3.0), "maize": (1.0, 3.0),
            "rice": (1.0, 3.0),
            "leather": (3.0, 6.0)
        }
        
        # Check for high-risk items
        for item, risk_range in high_risk_items.items():
            if item in food_name_lower or item in description:
                return random.uniform(risk_range[0], risk_range[1])
        
        # Fallback: Check for generic terms that might indicate risk
        if any(term in food_name_lower or term in description for term in ["meat", "dairy", "processed"]):
            return random.uniform(2.0, 4.0)
        elif any(term in food_name_lower or term in description for term in ["fruit", "vegetable", "grain"]):
            return random.uniform(0.0, 2.0)
        
        # Default low risk
        return random.uniform(0.0, 3.0)
    
    def get_all_foods(self):
        """Get list of all available foods"""
        try:
            # Get foods from model and local data
            all_foods = sorted(set(self.model.get_all_foods() + self.foods))
            return all_foods
        except Exception as e:
            print(f"Error getting all foods: {e}")
            return self.foods

    def _calculate_environmental_score(self, product):
        """Calculate environmental score from Open Food Facts data"""
        score = 0
        if product.get("ecoscore_grade"):
            # Convert A-E grade to numeric score
            grade_scores = {"a": 9, "b": 7, "c": 5, "d": 3, "e": 1}
            score = grade_scores.get(product["ecoscore_grade"].lower(), 5)
        return score

    def _calculate_environmental_score_usda(self, food_data):
        """Calculate environmental score from USDA data"""
        # Base score starts at 5 (neutral)
        score = 5.0
        
        # Adjust score based on food category
        description = food_data.get('description', '').lower()
        
        # Higher impact foods
        if any(term in description for term in ['beef', 'lamb', 'pork']):
            score -= 2
        elif any(term in description for term in ['chicken', 'turkey', 'fish']):
            score -= 1
        # Lower impact foods
        elif any(term in description for term in ['vegetable', 'fruit', 'grain', 'legume']):
            score += 2
        elif any(term in description for term in ['nut', 'seed']):
            score += 1
            
        # Ensure score stays within 0-10 range
        return max(0, min(10, score))