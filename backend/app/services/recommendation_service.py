import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.models.food_model import FoodImpactModel
from app.services.food_data_service import FoodDataService

class RecommendationService:
    def __init__(self):
        self.food_model = FoodImpactModel()
        self.food_data_service = FoodDataService()
    
    def get_recommendations(self, food_name, impact_preferences=None, limit=3):
        """Generate sustainable food recommendations"""
        if impact_preferences is None:
            impact_preferences = {'carbon': 0.3, 'water': 0.2, 'energy': 0.1, 'waste': 0.1, 'deforestation': 0.3}
        
        original_impact = self.food_data_service.get_food_impact(food_name)
        if not original_impact:
            return self._fallback_recommendations(food_name, limit)
        
        all_foods = self.food_model.get_all_foods()
        candidates = [f for f in all_foods if f.lower() != food_name.lower()]
        
        scored_candidates = []
        for candidate_name in candidates:
            candidate_impact = self.food_data_service.get_food_impact(candidate_name)
            if not candidate_impact:
                continue
            
            sustainability_score = self._calculate_sustainability_score(original_impact, candidate_impact, impact_preferences)
            similarity_score = self._calculate_similarity(food_name, candidate_name)
            final_score = (sustainability_score * 0.7) + (similarity_score * 0.3)
            
            scored_candidates.append({
                'name': candidate_name,
                'impact': candidate_impact,
                'sustainability_improvement': sustainability_score,
                'similarity': similarity_score,
                'score': final_score
            })
        
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return [{
            'name': candidate['name'],
            'impact': candidate['impact'],
            'sustainability_improvement': round(candidate['sustainability_improvement'] * 100, 1),
            'explanation': self._generate_explanation(food_name, candidate['name'], original_impact, candidate['impact'], impact_preferences)
        } for candidate in scored_candidates[:limit]]
    
    def _calculate_similarity(self, food1, food2):
        """Calculate simple similarity based on food categories"""
        categories = {
            'milk': ['milk', 'dairy', 'cream', 'yogurt', 'cheese'],
            'meat': ['beef', 'chicken', 'pork', 'lamb', 'turkey', 'meat', 'steak', 'burger'],
            'fruit': ['apple', 'banana', 'berry', 'fruit', 'orange', 'kiwi', 'melon'],
            'vegetable': ['vegetable', 'carrot', 'broccoli', 'spinach', 'lettuce', 'kale'],
            'grain': ['wheat', 'rice', 'oat', 'barley', 'grain', 'bread', 'pasta', 'cereal'],
            'legume': ['bean', 'lentil', 'pea', 'chickpea', 'tofu', 'soy', 'legume'],
            'nut': ['almond', 'cashew', 'nut', 'peanut', 'walnut'],
            'beverage': ['drink', 'juice', 'water', 'soda', 'tea', 'coffee']
        }
        food1_lower, food2_lower = food1.lower(), food2.lower()
        score = 0
        for cat, terms in categories.items():
            if any(t in food1_lower for t in terms) and any(t in food2_lower for t in terms):
                score += 1
        return score / len(categories)
    
    def _calculate_sustainability_score(self, original, candidate, preferences):
        """Calculate sustainability improvement score"""
        total_score = 0
        total_weight = sum(preferences.values())
        normalized_weights = {k: v/total_weight for k, v in preferences.items()}
        
        for metric, weight in normalized_weights.items():
            orig_val = original.get(metric, 0)
            cand_val = candidate.get(metric, 0)
            if orig_val > 0:
                improvement = min(1.0, max(0, (orig_val - cand_val) / orig_val))
                total_score += improvement * weight
        return total_score
    
    def _generate_explanation(self, original_name, candidate_name, original_impact, candidate_impact, preferences):
        """Generate recommendation explanation"""
        best_metric, best_improvement = None, 0
        for metric in preferences:
            orig_val = original_impact.get(metric, 0)
            cand_val = candidate_impact.get(metric, 0)
            if orig_val > 0:
                improvement = (orig_val - cand_val) / orig_val
                if improvement > best_improvement:
                    best_improvement = improvement
                    best_metric = metric
        
        if best_metric:
            metric_names = {'carbon': 'carbon footprint', 'water': 'water usage', 'energy': 'energy use', 'waste': 'waste generation', 'deforestation': 'deforestation impact'}
            return f"{candidate_name} reduces {metric_names[best_metric]} by {round(best_improvement * 100)}% compared to {original_name}."
        return f"{candidate_name} is a more sustainable alternative to {original_name}."
    
    def _fallback_recommendations(self, food_name, limit=3):
        """Provide fallback recommendations when no data is available."""
        food_lower = food_name.lower()

        # Initialize comprehensive fallback options
        dairy_alts = [
            {
                "name": "Oat Milk",
                "explanation": "Oat milk reduces water usage by 60% compared to dairy milk.",
                "impact": {"breakdown": {"carbon": 0.5, "water": 150, "energy": 0.4, "waste": 0.05, "deforestation": 0.1}},
                "sustainability_improvement": 80.0,
                "similarity_score": 85.0
            },
            {
                "name": "Soy Milk",
                "explanation": "Soy milk has high protein content and 70% lower carbon footprint than dairy milk.",
                "impact": {"breakdown": {"carbon": 0.4, "water": 130, "energy": 0.3, "waste": 0.04, "deforestation": 3.0}},
                "sustainability_improvement": 70.0,
                "similarity_score": 90.0
            },
            {
                "name": "Almond Milk",
                "explanation": "Almond milk produces 80% less greenhouse gases than dairy milk.",
                "impact": {"breakdown": {"carbon": 0.3, "water": 300, "energy": 0.3, "waste": 0.03, "deforestation": 0.2}},
                "sustainability_improvement": 65.0,
                "similarity_score": 85.0
            }
        ]
        
        meat_alts = [
            {
                "name": "Tofu",
                "explanation": "Tofu has a 96% lower carbon footprint than beef.",
                "impact": {"breakdown": {"carbon": 2.0, "water": 300, "energy": 2.0, "waste": 0.2, "deforestation": 1.0}},
                "sustainability_improvement": 90.0,
                "similarity_score": 75.0
            },
            {
                "name": "Lentils",
                "explanation": "Lentils use 99% less water than beef and have minimal environmental impact.",
                "impact": {"breakdown": {"carbon": 0.9, "water": 180, "energy": 1.5, "waste": 0.1, "deforestation": 0.1}},
                "sustainability_improvement": 95.0,
                "similarity_score": 65.0
            },
            {
                "name": "Beyond Meat",
                "explanation": "Plant-based meat alternatives generate 90% less greenhouse gas emissions than beef.",
                "impact": {"breakdown": {"carbon": 3.5, "water": 350, "energy": 2.5, "waste": 0.3, "deforestation": 0.5}},
                "sustainability_improvement": 85.0,
                "similarity_score": 90.0
            }
        ]
        
        vegetable_alts = [
            {
                "name": "Local Seasonal Vegetables",
                "explanation": "Local seasonal vegetables reduce transportation emissions by up to 90%.",
                "impact": {"breakdown": {"carbon": 0.2, "water": 20, "energy": 0.1, "waste": 0.02, "deforestation": 0.0}},
                "sustainability_improvement": 75.0,
                "similarity_score": 85.0
            },
            {
                "name": "Organic Vegetables",
                "explanation": "Organic farming uses 45% less energy and releases fewer chemicals.",
                "impact": {"breakdown": {"carbon": 0.3, "water": 25, "energy": 0.2, "waste": 0.01, "deforestation": 0.0}},
                "sustainability_improvement": 65.0,
                "similarity_score": 90.0
            }
        ]
        
        grain_alts = [
            {
                "name": "Barley",
                "explanation": "Barley requires 50% less water than rice and has a lower carbon footprint.",
                "impact": {"breakdown": {"carbon": 0.3, "water": 70, "energy": 0.2, "waste": 0.02, "deforestation": 0.1}},
                "sustainability_improvement": 60.0,
                "similarity_score": 80.0
            },
            {
                "name": "Quinoa",
                "explanation": "Quinoa is drought-resistant and has a 30% lower carbon footprint than other grains.",
                "impact": {"breakdown": {"carbon": 0.4, "water": 90, "energy": 0.3, "waste": 0.02, "deforestation": 0.1}},
                "sustainability_improvement": 55.0,
                "similarity_score": 75.0
            }
        ]
        
        default_alts = [
            {
                "name": "Local Produce",
                "explanation": "Local produce reduces transportation emissions by up to 90%.",
                "impact": {"breakdown": {"carbon": 0.3, "water": 40, "energy": 0.2, "waste": 0.1, "deforestation": 0.1}},
                "sustainability_improvement": 70.0,
                "similarity_score": 60.0
            },
            {
                "name": "Seasonal Vegetables",
                "explanation": "Seasonal vegetables require 50% less energy for production.",
                "impact": {"breakdown": {"carbon": 0.2, "water": 30, "energy": 0.1, "waste": 0.05, "deforestation": 0.0}},
                "sustainability_improvement": 80.0,
                "similarity_score": 50.0
            },
            {
                "name": "Plant-Based Alternatives",
                "explanation": "Plant-based foods generally have 10-50x lower carbon footprint than animal products.",
                "impact": {"breakdown": {"carbon": 0.5, "water": 50, "energy": 0.3, "waste": 0.1, "deforestation": 0.2}},
                "sustainability_improvement": 75.0,
                "similarity_score": 55.0
            }
        ]

        # Select appropriate alternatives based on food type
        if any(term in food_lower for term in self.food_categories['milk']):
            recommendations = dairy_alts
        elif any(term in food_lower for term in self.food_categories['meat']):
            recommendations = meat_alts
        elif any(term in food_lower for term in self.food_categories['vegetable']):
            recommendations = vegetable_alts
        elif any(term in food_lower for term in self.food_categories['grain']):
            recommendations = grain_alts
        else:
            recommendations = default_alts

        return recommendations[:limit]


