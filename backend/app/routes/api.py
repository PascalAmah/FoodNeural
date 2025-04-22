from flask import Blueprint, jsonify, request
from app.services.food_data_service import FoodDataService
from app.services.food_recommendation_service import FoodRecommendationService
import logging
import datetime

# Configure logger
logger = logging.getLogger(__name__)

# Initialize blueprint and services
api_bp = Blueprint('api', __name__)
food_service = FoodDataService()
recommendation_service = FoodRecommendationService()

def get_impact_preferences():
    """Get impact preference weights from query parameters."""
    return {
        "carbon": float(request.args.get('carbon_weight', 0.3)),
        "water": float(request.args.get('water_weight', 0.2)),
        "energy": float(request.args.get('energy_weight', 0.1)),
        "waste": float(request.args.get('waste_weight', 0.1)),
        "deforestation": float(request.args.get('deforestation_weight', 0.3)),
    }

@api_bp.route('/impact/<food_name>')
def get_food_impact(food_name):
    """Get environmental impact data for a food item."""
    impact_data = food_service.get_food_impact(food_name)
    if not impact_data:
        return jsonify({'error': f'Food item "{food_name}" not found'}), 404
    return jsonify(impact_data)

@api_bp.route('/recommendations/<food_name>')
def get_recommendations(food_name):
    """Get food recommendations with combined AI and ML approach."""
    try:
        # Parse query parameters
        use_ai = request.args.get('use_ai', 'true').lower() == 'true'
        limit = min(max(int(request.args.get('limit', 3)), 1), 5)
        preferences = get_impact_preferences()

        # Get food impact data
        impact_data = food_service.get_food_impact(food_name)
        if not impact_data:
            return jsonify({'error': f'Food item "{food_name}" not found'}), 404

        # Get recommendations using the unified service
        logger.info(f"Generating recommendations for {food_name}")
        result = recommendation_service.get_recommendations(
            food_name, 
            impact_preferences=preferences, 
            limit=limit,
            use_ai=use_ai
        )
        
        if not result or not result.get("alternatives"):
            return jsonify({'error': 'No recommendations available'}), 404
        
        return jsonify(result)

    except Exception as e:
        logger.error(f"Recommendation error: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/search')
def search_foods():
    """Search for food items."""
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
    
    all_foods = food_service.get_all_foods()
    matches = [food for food in all_foods if query in food.lower()]
    return jsonify(matches)

@api_bp.route('/food_info/<food_name>')
def get_food_info(food_name):
    """Get detailed food information with nutritional facts."""
    try:
        # Get impact data if available
        impact_data = food_service.get_food_impact(food_name)
        
        # Get food info from recommendation service
        food_info = recommendation_service.get_food_info(food_name, impact_data)
        
        if not food_info:
            return jsonify({'error': f'Food item "{food_name}" not found'}), 404
            
        return jsonify(food_info)
    except Exception as e:
        logger.error(f"Error getting food info: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200


# @api_bp.route('/compare')
# def compare_foods():
#     """Compare environmental impact of two foods."""
#     food1 = request.args.get('food1')
#     food2 = request.args.get('food2')
    
#     if not food1 or not food2:
#         return jsonify({'error': 'Please provide both food items'}), 400

#     comparison = recommendation_service.get_impact_comparison(food1, food2)
#     if not comparison:
#         return jsonify({'error': 'One or both foods not found'}), 404

#     return jsonify(comparison)