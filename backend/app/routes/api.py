from flask import Blueprint, jsonify, request
from app.services.food_data_service import FoodDataService
from app.services.recommendation_service import RecommendationService
from app.services.ai_recommendation_service import AIRecommendationService
import logging
import datetime

# Configure logger
logger = logging.getLogger(__name__)

# Initialize blueprint and services
api_bp = Blueprint('api', __name__)
food_service = FoodDataService()
recommendation_service = RecommendationService()
ai_recommendation_service = AIRecommendationService()

def get_impact_preferences():
    """Get impact preference weights from query parameters."""
    return {
        "carbon": float(request.args.get('carbon_weight', 0.3)),
        "water": float(request.args.get('water_weight', 0.2)),
        "energy": float(request.args.get('energy_weight', 0.1)),
        "waste": float(request.args.get('waste_weight', 0.1)),
        "deforestation": float(request.args.get('deforestation_weight', 0.3)),
    }

@api_bp.route('/', methods=['GET', 'HEAD'])
def home():
    """Root API endpoint."""
    return jsonify({"message": "API is running!"})

@api_bp.route('/impact/<food_name>')
def get_food_impact(food_name):
    """Get environmental impact data for a food item."""
    impact_data = food_service.get_food_impact(food_name)
    if not impact_data:
        return jsonify({'error': f'Food item "{food_name}" not found'}), 404
    return jsonify(impact_data)

@api_bp.route('/recommendations/<food_name>')
def get_recommendations(food_name):
    """Get food recommendations with AI and fallback to ML."""
    try:
        # Parse query parameters
        use_ai = request.args.get('use_ai', 'true').lower() == 'true'
        limit = min(max(int(request.args.get('limit', 3)), 1), 5)
        preferences = get_impact_preferences()

        # Get food impact data
        impact_data = food_service.get_food_impact(food_name)
        if not impact_data:
            return jsonify({'error': f'Food item "{food_name}" not found'}), 404

        # Try AI recommendations if requested
        if use_ai:
            try:
                logger.info(f"Attempting AI recommendations for {food_name}")
                ai_result = ai_recommendation_service.get_ai_recommendations(
                    food_name, impact_data, limit
                )
                if ai_result and ai_result.get("alternatives"):
                    logger.info(f"Successfully generated AI recommendations for {food_name}")
                    return jsonify({
                        "source": "ai",
                        "alternatives": ai_result["alternatives"]
                    })
                logger.warning(f"No AI recommendations generated for {food_name}")
            except Exception as e:
                logger.error(f"AI recommendation failed: {e}", exc_info=True)

        # Fallback to ML recommendations
        logger.info(f"Using ML recommendations for {food_name}")
        ml_result = recommendation_service.get_recommendations(
            food_name, 
            impact_preferences=preferences, 
            limit=limit
        )
        if not ml_result:
            return jsonify({'error': 'No recommendations available'}), 404

        return jsonify({
            "source": "ml",
            "alternatives": ml_result
        })

    except Exception as e:
        logger.error(f"Recommendation error: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

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

@api_bp.route('/search')
def search_foods():
    """Search for food items."""
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
    
    all_foods = food_service.get_all_foods()
    matches = [food for food in all_foods if query in food.lower()]
    return jsonify(matches)


@api_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200