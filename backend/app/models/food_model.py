import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from transformers import pipeline
import os
from typing import Optional
import logging
from transformers import pipeline, logging as transformers_logging

transformers_logging.set_verbosity_error()
logging.getLogger("transformers").setLevel(logging.ERROR)

class FoodImpactModel:
    def __init__(self, data_path=None):
        """Initialize the food impact model with data"""
        self.model_name = "distilbert-base-uncased-finetuned-sst-2-english"
        self.nlp = pipeline(
            "sentiment-analysis",
            model=self.model_name,
            framework="pt",
            device=-1
        )
        try:
            self.sentiment_analyzer = pipeline("sentiment-analysis", model=self.model_name)
        except Exception as e:
            print(f"Warning: Could not initialize sentiment analyzer: {e}")
            self.sentiment_analyzer = None

        # Load food data from CSV
        if not data_path:
            data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'foods.csv')
        
        try:
            self.data = pd.read_csv(data_path)
            print(f"Successfully loaded {len(self.data)} food items from {data_path}")
        except Exception as e:
            print(f"Warning: Could not load data from {data_path}: {e}")
            # Fall back to default data
            self.data = pd.DataFrame([
                {"food": "Almond Milk", "carbon": 1.2, "water": 300, "energy": 0.8, "waste": 0.1, "deforestation": 0.2, "impact": "Medium", "description": "Plant-based milk from almonds"},
                {"food": "Oat Milk", "carbon": 0.5, "water": 150, "energy": 0.4, "waste": 0.05, "deforestation": 0.1, "impact": "Low", "description": "Sustainable oat-based milk"},
                {"food": "Apple", "carbon": 0.3, "water": 50, "energy": 0.2, "waste": 0.02, "deforestation": 0.1, "impact": "Low", "description": "Locally grown fruit"},
                {"food": "Beef", "carbon": 27.0, "water": 15400, "energy": 40.0, "waste": 2.5, "deforestation": 9.0, "impact": "High", "description": "Grass-fed beef"},
                {"food": "Chicken", "carbon": 6.9, "water": 4325, "energy": 15.0, "waste": 0.8, "deforestation": 2.0, "impact": "Medium", "description": "Free-range poultry"},
                {"food": "Soy Milk", "carbon": 0.4, "water": 130, "energy": 0.3, "waste": 0.04, "deforestation": 3.0, "impact": "Medium", "description": "Organic soy milk"},
                {"food": "Rice Milk", "carbon": 0.9, "water": 270, "energy": 0.6, "waste": 0.08, "deforestation": 0.5, "impact": "Low", "description": "Rice-based milk"},
                {"food": "Cow Milk", "carbon": 3.2, "water": 1000, "energy": 5.0, "waste": 0.2, "deforestation": 2.0, "impact": "High", "description": "Conventional dairy milk"}
            ])
        
        self.label_encoder = LabelEncoder()
        self.data["impact_encoded"] = self.label_encoder.fit_transform(self.data["impact"])
        self._train_model()
    
    def _train_model(self):
        """Train the classification model"""
        X = self.data[["carbon", "water", "energy", "waste", "deforestation"]]
        y = self.data["impact_encoded"]
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y)
    
    def get_food_impact(self, food_name, description=None):
        """Get impact data for a specific food with optional description analysis"""
        food = self.data[self.data["food"].str.lower() == food_name.lower()]
        if not food.empty:
            result = food.iloc[0].to_dict()
            if description:
                result.update(self._analyze_description(description))
            result['environmental_score'] = self._calculate_score(result)
            return result
        return None
    
    def predict_impact(self, carbon, water, energy, waste, deforestation):
        """Predict impact category for given metrics"""
        feature_names = ["carbon", "water", "energy", "waste", "deforestation"]
        X_input = pd.DataFrame([[carbon, water, energy, waste, deforestation]], columns=feature_names)
        impact_idx = self.model.predict(X_input)[0]
        return self.label_encoder.inverse_transform([impact_idx])[0]
    
    def get_all_foods(self):
        """Return list of all foods in the dataset"""
        return self.data["food"].tolist()
    
    def _analyze_description(self, description):
        """Analyze food description using NLP"""
        entities = self.nlp(description)
        analysis = {"ingredients": [], "certifications": []}
        for entity in entities:
            if entity['entity'].startswith('B-') or entity['entity'].startswith('I-'):
                if entity['word'] in ["organic", "sustainable", "free-range", "grass-fed"]:
                    analysis["certifications"].append(entity['word'])
                else:
                    analysis["ingredients"].append(entity['word'])
        return analysis
    
    def _calculate_score(self, food_data):
        """Calculate environmental impact score (0-100, lower is worse)"""
        weights = {'carbon': 0.25, 'water': 0.20, 'energy': 0.15, 'waste': 0.15, 'deforestation': 0.25}
        max_values = {'carbon': 27.0, 'water': 15400.0, 'energy': 40.0, 'waste': 2.5, 'deforestation': 9.0}
        
        raw_score = sum(
            (food_data.get(metric, 0) / max_values.get(metric, 1)) * weights.get(metric, 0)
            for metric in weights
        )
        # Invert and normalize to 0-100 (higher score = more sustainable)
        return round(100 - (raw_score * 100), 2)