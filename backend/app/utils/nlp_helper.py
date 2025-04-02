import spacy
from app.data.food_alternatives import FOOD_ALTERNATIVES

class NLPHelper:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self._initialize_food_categories()
    
    def _initialize_food_categories(self):
        """Initialize food categories with keywords and mappings"""
        self.food_categories = {
            'dairy': ['milk', 'dairy', 'cream', 'yogurt', 'cheese', 'butter'],
            'meat': ['beef', 'chicken', 'pork', 'lamb', 'turkey', 'meat', 'steak', 'burger'],
            'vegetables': ['vegetable', 'carrot', 'broccoli', 'spinach', 'lettuce', 'kale'],
            'grains': ['wheat', 'rice', 'oat', 'barley', 'grain', 'bread', 'pasta', 'cereal'],
            'legumes': ['bean', 'lentil', 'pea', 'chickpea', 'tofu', 'soy', 'legume'],
            'fruits': ['apple', 'banana', 'berry', 'fruit', 'orange', 'kiwi', 'melon'],
            'nuts': ['almond', 'cashew', 'nut', 'peanut', 'walnut'],
            'beverages': ['drink', 'juice', 'water', 'soda', 'tea', 'coffee']
        }
        
        # Map categories to alternatives
        self.category_alternatives = FOOD_ALTERNATIVES

    def get_food_category(self, food_name):
        """Identify food category using NLP and keyword matching"""
        food_tokens = self.process_text(food_name.lower())
        
        # Try exact category match first
        for category, keywords in self.food_categories.items():
            if any(keyword in food_name.lower() for keyword in keywords):
                return category
        
        # Use NLP for more complex matching
        doc = self.nlp(food_name.lower())
        for token in doc:
            for category, keywords in self.food_categories.items():
                if any(self.nlp(keyword).similarity(token) > 0.7 for keyword in keywords):
                    return category
        
        return "default"

    def process_text(self, text):
        """Process text using spaCy NLP model"""
        doc = self.nlp(text)
        return [token.lemma_ for token in doc if not token.is_stop]

    def get_sustainable_alternatives(self, food_name, limit=3):
        """Get sustainable alternatives based on food category"""
        category = self.get_food_category(food_name)
        
        # Get alternatives from the matched category
        alternatives = self.category_alternatives.get(category, [])
        
        # If no alternatives found, use default
        if not alternatives:
            alternatives = self.category_alternatives.get('default', [])
        
        return alternatives[:limit]