from flask import Blueprint, jsonify, request
from app.services.food_data_service import FoodDataService
from app.services.recommendation_service import RecommendationService
from app.services.ai_recommendation_service import AIRecommendationService
from typing import Dict
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Initialize blueprint and services
api_bp = Blueprint('api', __name__, url_prefix='/api')
food_service = FoodDataService()
recommendation_service = RecommendationService()
ai_recommendation_service = AIRecommendationService()

def _get_impact_preferences() -> Dict[str, float]:
    """Get impact preference weights from request parameters"""
    return {
        'carbon': float(request.args.get('carbon_weight', 0.3)),
        'water': float(request.args.get('water_weight', 0.2)),
        'energy': float(request.args.get('energy_weight', 0.1)),
        'waste': float(request.args.get('waste_weight', 0.1)),
        'deforestation': float(request.args.get('deforestation_weight', 0.3))
    }

@api_bp.route("/", methods=["GET"])
def home():
    """Root API endpoint"""
    return jsonify({"message": "API is running!"}), 200

@api_bp.route('/impact/<food_name>', methods=['GET'])
def get_food_impact(food_name):
    """Get environmental impact data for a food item"""
    impact_data = food_service.get_food_impact(food_name)
    if not impact_data:
        return jsonify({'error': f'Food item "{food_name}" not found'}), 404
    return jsonify(impact_data)

@api_bp.route('/recommendations/<food_name>', methods=['GET'])
def get_recommendations(food_name):
    """Get food recommendations with AI and fallback to ML"""
    try:
        use_ai = request.args.get('use_ai', 'true').lower() == 'true'
        limit = int(request.args.get('limit', 3))
        preferences = _get_impact_preferences()

        logger.info(f"Getting recommendations for {food_name} (AI: {use_ai})")

        # Get food impact data first
        impact_data = food_service.get_food_impact(food_name)
        if not impact_data:
            logger.warning(f"Food item not found: {food_name}")
            return jsonify({'error': f'Food item "{food_name}" not found'}), 404

        recommendations = None
        source = "ml"  # Default to ML recommendations

        # Try Gemini recommendations first if requested
        if use_ai:
            try:
                recommendations = ai_recommendation_service.get_ai_recommendations(
                    food_name,
                    impact_data,
                    limit
                )
                if recommendations and recommendations.get('alternatives'):
                    source = "ai"
                    logger.info(f"Using AI recommendations for {food_name}")
                    return jsonify({
                        'food': food_name,
                        'source': source,
                        'alternatives': recommendations['alternatives']
                    })
            except Exception as e:
                logger.error(f"AI recommendation failed: {e}")
                # Continue to ML recommendations instead of returning empty response

        # Use ML recommendations
        ml_recommendations = recommendation_service.get_recommendations(
            food_name,
            impact_preferences=preferences,
            limit=limit
        )
        
        if not ml_recommendations:
            return jsonify({'error': 'No recommendations available'}), 404

        return jsonify({
            'food': food_name,
            'source': source,
            'preferences': preferences,
            'alternatives': ml_recommendations
        })

    except ValueError as e:
        return jsonify({
            'error': 'Invalid parameter value',
            'details': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@api_bp.route('/search', methods=['GET'])
def search_foods():
    """Search for food items"""
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
        
    # Get all foods and filter by query
    all_foods = food_service.get_all_foods()
    matches = [food for food in all_foods if query in food.lower()]
    return jsonify(matches)

# @api_bp.route('/compare', methods=['GET'])
# def compare_foods():
#     """Compare environmental impact of two foods"""
#     food1 = request.args.get('food1')
#     food2 = request.args.get('food2')
    
#     if not food1 or not food2:
#         return jsonify({'error': 'Please provide both food items'}), 400
        
#     comparison = recommendation_service.get_impact_comparison(food1, food2)
#     if not comparison:
#         return jsonify({'error': 'One or both foods not found'}), 404
        
#     return jsonify(comparison)

@api_bp.errorhandler(Exception)
def handle_error(error):
    """Global error handler for API routes"""
    return jsonify({
        'error': str(error),
        'type': error.__class__.__name__
    }), 500
