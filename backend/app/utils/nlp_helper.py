import spacy
import random

class NLPHelper:
    def __init__(self):
        # Load NLP model
        self.nlp = spacy.load("en_core_web_sm")
        self._initialize_food_categories()
    
    def _initialize_food_categories(self):
        """Initialize food categories and alternatives"""
        self.categories = {
            "dairy": {
                "keywords": ["milk", "cheese", "yogurt", "cream"],
                "alternatives": [
                    {"name": "Oat Milk", "explanation": "Oat milk uses 80% less land and 60% less energy than dairy milk."},
                    {"name": "Almond Milk", "explanation": "Almond milk produces 50% fewer carbon emissions than dairy milk."},
                    {"name": "Soy Milk", "explanation": "Soy milk has the highest protein content of plant-based milks."}
                ]
            },
            "meat": {
                "keywords": ["beef", "chicken", "pork", "lamb"],
                "alternatives": [
                    {"name": "Tofu", "explanation": "Tofu produces 1/20th the carbon emissions of beef."},
                    {"name": "Lentils", "explanation": "Lentils are rich in protein and have minimal environmental impact."},
                    {"name": "Seitan", "explanation": "Seitan has a meat-like texture with much lower environmental footprint."}
                ]
            },
            "fruit": {
                "keywords": ["apple", "banana", "orange", "berry"],
                "alternatives": [
                    {"name": "Local Seasonal Fruits", "explanation": "Local fruits have lower transportation emissions."},
                    {"name": "Berries", "explanation": "Berries typically use less water than tropical fruits."},
                    {"name": "Apples", "explanation": "Apples can be stored for months, reducing food waste."}
                ]
            }
        }

    def process_text(self, text):
        """Process text using spaCy NLP model"""
        doc = self.nlp(text)
        return [token.lemma_ for token in doc if not token.is_stop]

    def get_food_category(self, food_name):
        """Identify food category based on text analysis"""
        food_name_lower = food_name.lower()
        processed_words = self.process_text(food_name)

        for category, data in self.categories.items():
            if any(keyword in food_name_lower for keyword in data["keywords"]):
                return category
        return "other"

    def get_sustainable_alternatives(self, food_name, limit=3):
        """Get sustainable alternatives for a food item"""
        category = self.get_food_category(food_name)
        
        if category in self.categories:
            alternatives = self.categories[category]["alternatives"]
        else:
            # Combine all alternatives for unknown categories
            alternatives = []
            for cat_data in self.categories.values():
                alternatives.extend(cat_data["alternatives"])
            random.shuffle(alternatives)

        return alternatives[:limit]