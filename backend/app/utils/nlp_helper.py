import spacy
from app.data.food_alternatives import FOOD_ALTERNATIVES
import re

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
            'fruits': ['apple', 'banana', 'berry', 'fruit', 'orange', 'kiwi', 'melon', 'berries'],
            'nuts': ['almond', 'cashew', 'nut', 'peanut', 'walnut'],
            'beverages': ['drink', 'juice', 'water', 'soda', 'tea', 'coffee']
        }
        
        # Expanded food items for better matching
        self.food_dictionary = {}
        for category, keywords in self.food_categories.items():
            for keyword in keywords:
                self.food_dictionary[keyword] = category
                # Add plural forms
                if not keyword.endswith('s'):
                    self.food_dictionary[f"{keyword}s"] = category
        
        # Map categories to alternatives
        self.category_alternatives = FOOD_ALTERNATIVES

    def get_food_category(self, food_name):
        """Identify food category using text matching instead of NLP similarity"""
        food_name_lower = food_name.lower()
        
        # Try exact matches first (full match)
        if food_name_lower in self.food_dictionary:
            return self.food_dictionary[food_name_lower]
        
        # Try keyword matching (partial match)
        for keyword, category in self.food_dictionary.items():
            if keyword in food_name_lower:
                return category
        
        # Try stemming - removing common suffixes
        stemmed_food = self._basic_stem(food_name_lower)
        for keyword, category in self.food_dictionary.items():
            stemmed_keyword = self._basic_stem(keyword)
            if stemmed_keyword in stemmed_food or stemmed_food in stemmed_keyword:
                return category
        
        # Try lemmatization as a last resort
        tokens = self.process_text(food_name_lower)
        for token in tokens:
            if token in self.food_dictionary:
                return self.food_dictionary[token]
        
        return "default"
    
    def _basic_stem(self, word):
        """Simple stemming to handle common endings"""
        if len(word) < 4:
            return word
            
        # Remove common suffixes
        for suffix in ['ies', 'es', 's', 'ing', 'ed']:
            if word.endswith(suffix):
                return word[:-len(suffix)]
        return word

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