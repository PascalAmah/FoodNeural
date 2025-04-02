import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.models.food_model import FoodImpactModel
from app.services.food_data_service import FoodDataService
from app.utils.nlp_helper import NLPHelper
import logging

class RecommendationService:
    def __init__(self):
        self.food_model = FoodImpactModel()
        self.food_data_service = FoodDataService()
        self.nlp_helper = NLPHelper()
        
    def get_recommendations(self, food_name, impact_preferences=None, limit=3):
        """Generate sustainable food recommendations"""
        if impact_preferences is None:
            impact_preferences = {
                'carbon': 0.3,
                'water': 0.2,
                'energy': 0.1,
                'waste': 0.1,
                'deforestation': 0.3
            }
        
        try:
            original_impact = self.food_data_service.get_food_impact(food_name)
            if not original_impact:
                return self._fallback_recommendations(food_name, limit)

            # Get both API and category-based recommendations
            api_recs = self._get_api_recommendations(food_name, original_impact, impact_preferences, limit)
            category_recs = self._get_category_recommendations(food_name, limit)

            # Combine and deduplicate recommendations
            all_recs = self._combine_recommendations(api_recs, category_recs, limit)
            
            return all_recs

        except Exception as e:
            logging.error(f"Error getting recommendations: {e}")
            return self._fallback_recommendations(food_name, limit)

    def _combine_recommendations(self, api_recs, category_recs, limit):
        """Combine and deduplicate recommendations"""
        seen = set()
        combined = []

        for rec in api_recs + category_recs:
            name_lower = rec['name'].lower()
            if name_lower not in seen:
                seen.add(name_lower)
                combined.append(rec)

        # Sort by sustainability improvement
        combined.sort(key=lambda x: x.get('sustainability_improvement', 0), reverse=True)
        return combined[:limit]

    def _get_category_recommendations(self, food_name, limit):
        """Get recommendations from predefined categories"""
        try:
            alternatives = self.nlp_helper.get_sustainable_alternatives(food_name, limit)
            return [self._format_recommendation(alt) for alt in alternatives]
        except Exception as e:
            logging.error(f"Error in category recommendations: {e}")
            return []

    def _format_recommendation(self, alternative):
        """Format recommendation with consistent structure"""
        return {
            'name': alternative['name'],
            'impact': {
                'breakdown': {
                    metric: float(values)
                    for metric, values in alternative['impact']['breakdown'].items()
                }
            },
            'sustainability_improvement': float(alternative.get('sustainability_improvement', 50)),
            'similarity_score': float(alternative.get('similarity_score', 50)),
            'explanation': alternative['explanation']
        }

    def _fallback_recommendations(self, food_name, limit=3):
        """Provide fallback recommendations when no data is available"""
        return self._get_category_recommendations(food_name, limit)[:limit]

    def _calculate_similarity(self, food1, food2):
        """Calculate simple similarity based on food categories"""
        food1_lower, food2_lower = food1.lower(), food2.lower()
        score = 0
        for cat, terms in self.food_categories.items():
            if any(t in food1_lower for t in terms) and any(t in food2_lower for t in terms):
                score += 1
        return score / len(self.food_categories)
    
    def _calculate_sustainability_score(self, original, candidate, preferences):
        """Calculate sustainability improvement score"""
        try:
            total_score = 0
            total_weight = sum(preferences.values())
            normalized_weights = {k: v/total_weight for k, v in preferences.items()}
            
            orig_metrics = original.get('breakdown', original)
            cand_metrics = candidate.get('breakdown', candidate)
            
            for metric, weight in normalized_weights.items():
                orig_val = float(orig_metrics.get(metric, 0))
                cand_val = float(cand_metrics.get(metric, 0))
                
                if orig_val > 0:
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
