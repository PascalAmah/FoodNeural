import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.models.food_model import FoodImpactModel
from app.services.food_data_service import FoodDataService
from app.data.food_alternatives import FOOD_ALTERNATIVES

class RecommendationService:
    def __init__(self):
        self.food_model = FoodImpactModel()
        self.food_data_service = FoodDataService()
        self.alternatives = FOOD_ALTERNATIVES
        
        # Move categories to class level
        self.food_categories = {
            'milk': ['milk', 'dairy', 'cream', 'yogurt', 'cheese'],
            'meat': ['beef', 'chicken', 'pork', 'lamb', 'turkey', 'meat', 'steak', 'burger'],
            'fruit': ['apple', 'banana', 'berry', 'fruit', 'orange', 'kiwi', 'melon'],
            'vegetable': ['vegetable', 'carrot', 'broccoli', 'spinach', 'lettuce', 'kale'],
            'grain': ['wheat', 'rice', 'oat', 'barley', 'grain', 'bread', 'pasta', 'cereal'],
            'legume': ['bean', 'lentil', 'pea', 'chickpea', 'tofu', 'soy', 'legume'],
            'nut': ['almond', 'cashew', 'nut', 'peanut', 'walnut'],
            'beverage': ['drink', 'juice', 'water', 'soda', 'tea', 'coffee']
        }
    
    def get_recommendations(self, food_name, impact_preferences=None, limit=3):
        """Generate sustainable food recommendations"""
        if impact_preferences is None:
            impact_preferences = {'carbon': 0.3, 'water': 0.2, 'energy': 0.1, 'waste': 0.1, 'deforestation': 0.3}
        
        original_impact = self.food_data_service.get_food_impact(food_name)
        if not original_impact:
            return self._fallback_recommendations(food_name, limit)
        
        # Get recommendations from multiple sources
        api_recommendations = self._get_api_recommendations(food_name, original_impact, impact_preferences, limit)
        fallback_recommendations = self._get_category_recommendations(food_name, limit)
        
        # Combine and sort all recommendations
        all_recommendations = api_recommendations + fallback_recommendations
        
        # Remove duplicates based on name
        seen = set()
        unique_recommendations = []
        for rec in all_recommendations:
            if rec['name'].lower() not in seen:
                seen.add(rec['name'].lower())
                unique_recommendations.append(rec)
        
        # Sort by sustainability improvement
        unique_recommendations.sort(key=lambda x: x.get('sustainability_improvement', 0), reverse=True)
        
        return unique_recommendations[:limit]

    def _get_api_recommendations(self, food_name, original_impact, impact_preferences, limit):
        """Get recommendations from API data"""
        all_foods = self.food_model.get_all_foods()
        candidates = [f for f in all_foods if f.lower() != food_name.lower()]
        
        scored_candidates = []
        for candidate_name in candidates:
            candidate_impact = self.food_data_service.get_food_impact(candidate_name)
            if not candidate_impact:
                continue
            
            sustainability_score = self._calculate_sustainability_score(
                original_impact, 
                candidate_impact, 
                impact_preferences
            )
            similarity_score = self._calculate_similarity(food_name, candidate_name)
            final_score = (sustainability_score * 0.7) + (similarity_score * 0.3)
            
            scored_candidates.append({
                'name': candidate_name,
                'impact': candidate_impact,
                'sustainability_improvement': round(sustainability_score * 100, 1),
                'similarity_score': round(similarity_score * 100, 1),
                'explanation': self._generate_explanation(
                    food_name,
                    candidate_name,
                    original_impact,
                    candidate_impact,
                    impact_preferences
                )
            })
        
        scored_candidates.sort(key=lambda x: x['sustainability_improvement'], reverse=True)
        return scored_candidates[:limit]

    def _get_category_recommendations(self, food_name, limit):
        """Get recommendations from predefined alternatives"""
        food_lower = food_name.lower()
        
        # Get recommendations from multiple relevant categories
        recommendations = []
        
        # Check each category for relevance
        for category, terms in self.food_categories.items():
            if any(term in food_lower for term in terms):
                if category == 'milk':
                    recommendations.extend(self.alternatives.get('dairy', []))
                elif category == 'meat':
                    recommendations.extend(self.alternatives.get('meat', []))
                elif category == 'vegetable':
                    recommendations.extend(self.alternatives.get('vegetables', []))
                elif category == 'grain':
                    recommendations.extend(self.alternatives.get('grains', []))
        
        # Always include some defaults if we don't have enough recommendations
        if len(recommendations) < limit:
            recommendations.extend(self.alternatives.get('default', []))
        
        return recommendations

    def _fallback_recommendations(self, food_name, limit=3):
        """Provide fallback recommendations when no data is available"""
        return self._get_category_recommendations(food_name, limit)[:limit]

    def _calculate_similarity(self, food1, food2):
        """Calculate simple similarity based on food categories"""
        food1_lower, food2_lower = food1.lower(), food2.lower()
        score = 0
        for cat, terms in self.food_categories.items():  # Use self.food_categories here
            if any(t in food1_lower for t in terms) and any(t in food2_lower for t in terms):
                score += 1
        return score / len(self.food_categories)
    
    def _calculate_sustainability_score(self, original, candidate, preferences):
        """Calculate sustainability improvement score"""
        try:
            total_score = 0
            total_weight = sum(preferences.values())
            normalized_weights = {k: v/total_weight for k, v in preferences.items()}
            
            # Get breakdown metrics or fallback to root level
            orig_metrics = original.get('breakdown', original)
            cand_metrics = candidate.get('breakdown', candidate)
            
            for metric, weight in normalized_weights.items():
                orig_val = float(orig_metrics.get(metric, 0))
                cand_val = float(cand_metrics.get(metric, 0))
                
                if orig_val > 0:
                    # Calculate relative improvement (reduction in impact)
                    improvement = min(1.0, max(0, (orig_val - cand_val) / orig_val))
                    total_score += improvement * weight
            
            return total_score

        except Exception as e:
            logging.error(f"Error calculating sustainability score: {e}")
            return 0.0
    
    def _generate_explanation(self, original_name, candidate_name, original_impact, candidate_impact, preferences):
        """Generate recommendation explanation"""
        try:
            best_metric, best_improvement = None, 0
            
            # Get breakdown metrics or fallback to root level
            orig_metrics = original_impact.get('breakdown', original_impact)
            cand_metrics = candidate_impact.get('breakdown', candidate_impact)
            
            for metric in preferences:
                orig_val = float(orig_metrics.get(metric, 0))
                cand_val = float(cand_metrics.get(metric, 0))
                
                if orig_val > 0:
                    improvement = (orig_val - cand_val) / orig_val
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_metric = metric
            
            if best_metric:
                metric_names = {
                    'carbon': 'carbon footprint',
                    'water': 'water usage',
                    'energy': 'energy use',
                    'waste': 'waste generation',
                    'deforestation': 'deforestation impact'
                }
                return f"{candidate_name} reduces {metric_names[best_metric]} by {round(best_improvement * 100)}% compared to {original_name}."
            
            return f"{candidate_name} is a more sustainable alternative to {original_name}."

        except Exception as e:
            logging.error(f"Error generating explanation: {e}")
            return f"{candidate_name} is a more sustainable alternative to {original_name}."
