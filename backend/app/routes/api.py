from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Dict, List, Optional
from app.services.food_data_service import FoodDataService
from app.services.recommendation_service import RecommendationService
from app.services.ai_recommendation_service import AIRecommendationService
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Initialize router and services
router = APIRouter(prefix="/api")
food_service = FoodDataService()
recommendation_service = RecommendationService()
ai_recommendation_service = AIRecommendationService()


def get_impact_preferences(
    carbon_weight: float = Query(0.3),
    water_weight: float = Query(0.2),
    energy_weight: float = Query(0.1),
    waste_weight: float = Query(0.1),
    deforestation_weight: float = Query(0.3),
) -> Dict[str, float]:
    """Get impact preference weights from query parameters."""
    return {
        "carbon": carbon_weight,
        "water": water_weight,
        "energy": energy_weight,
        "waste": waste_weight,
        "deforestation": deforestation_weight,
    }


@router.get("/")
async def home():
    """Root API endpoint."""
    return {"message": "API is running!"}


@router.get("/impact/{food_name}")
async def get_food_impact(food_name: str):
    """Get environmental impact data for a food item."""
    impact_data = food_service.get_food_impact(food_name)
    if not impact_data:
        raise HTTPException(status_code=404, detail=f'Food item "{food_name}" not found')
    return impact_data


@router.get("/recommendations/{food_name}")
async def get_recommendations(
    food_name: str,
    use_ai: bool = Query(True),
    limit: int = Query(3, ge=1, le=5),
    preferences: Dict[str, float] = Depends(get_impact_preferences),
):
    """Get food recommendations with AI and fallback to ML."""
    try:
        # Get food impact data
        impact_data = food_service.get_food_impact(food_name)
        if not impact_data:
            raise HTTPException(
                status_code=404, 
                detail=f'Food item "{food_name}" not found'
            )

        # Try AI recommendations if requested
        if use_ai:
            try:
                logger.info(f"Attempting AI recommendations for {food_name}")
                ai_result = ai_recommendation_service.get_ai_recommendations(
                    food_name, impact_data, limit
                )
                if ai_result and ai_result.get("alternatives"):
                    logger.info(f"Successfully generated AI recommendations for {food_name}")
                    return {
                        "source": "ai",
                        "alternatives": ai_result["alternatives"]
                    }
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
            raise HTTPException(
                status_code=404, 
                detail="No recommendations available"
            )

        return {
            "source": "ml",
            "alternatives": ml_result
        }

    except Exception as e:
        logger.error(f"Recommendation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# @router.get("/compare")
# async def compare_foods(
#     food1: str = Query(..., description="First food item to compare"),
#     food2: str = Query(..., description="Second food item to compare"),
# ):
#     """
#     Compare environmental impact of two foods.
#     """
#     if not food1 or not food2:
#         raise HTTPException(status_code=400, detail="Please provide both food items")

#     comparison = recommendation_service.get_impact_comparison(food1, food2)
#     if not comparison:
#         raise HTTPException(status_code=404, detail="One or both foods not found")

#     return comparison


@router.get("/search")
async def search_foods(q: str = Query("")):
    """Search for food items."""
    if not q:
        return []
    # Get all foods and filter by query
    all_foods = food_service.get_all_foods()
    matches = [food for food in all_foods if q.lower() in food.lower()]
    return matches
