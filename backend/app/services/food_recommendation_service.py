import requests
import logging
import re
import concurrent.futures
from functools import lru_cache
import numpy as np
from app.models.food_model import FoodImpactModel
from app.services.food_data_service import FoodDataService
from app.utils.nlp_helper import NLPHelper
from app.config import Config

class FoodRecommendationService:
    """
    Unified service that handles both AI-powered and ML-based food recommendations.
    Combines functionality from the previous RecommendationService and AIRecommendationService.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.food_model = FoodImpactModel()
        self.food_data_service = FoodDataService()
        self.nlp_helper = NLPHelper()
        
        # AI configuration
        self.api_key = Config.GEMINI_API_KEY
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        
        # Food information storage
        self.food_info = None
        
        # Default impact preferences
        self.default_preferences = {
            'carbon': 0.3,
            'water': 0.2,
            'energy': 0.1,
            'waste': 0.1,
            'deforestation': 0.3
        }
        
        # Food categories for matching
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
        
        # Common food descriptions as an immediate fallback
        self.common_foods = {
            "beef": {
                "name": "Beef",
                "type": "Meat",
                "description": "Beef is a widely consumed red meat obtained from cattle. It has a substantial environmental footprint, requiring significant water (15,000+ liters per kg) and land resources, while contributing to greenhouse gas emissions through methane from cattle and deforestation for grazing land.",
                "details": "Beef provides high-quality protein, iron, zinc, and B vitamins, but has a higher environmental impact than most other protein sources.",
                "nutrition": {"protein": 26, "fat": 15, "carbs": 0, "fiber": 0, "calories": 250}
            },
            "chicken": {
                "name": "Chicken",
                "type": "Meat",
                "description": "Chicken is a popular poultry meat with a lower environmental impact than beef. It requires less water (around 4,000 liters per kg), produces fewer greenhouse gas emissions, and uses less land than beef production, making it a more sustainable animal protein option.",
                "details": "Chicken is rich in lean protein and provides essential nutrients like niacin and selenium.",
                "nutrition": {"protein": 27, "fat": 14, "carbs": 0, "fiber": 0, "calories": 239}
            },
            "pork": {
                "name": "Pork",
                "type": "Meat",
                "description": "Pork is meat derived from domestic pigs with a moderate environmental footprint. It has a lower impact than beef but higher than chicken, requiring moderate water usage and land resources while producing less methane but still contributing to greenhouse gas emissions.",
                "details": "Pork is a good source of complete protein and thiamine (vitamin B1).",
                "nutrition": {"protein": 27, "fat": 14, "carbs": 0, "fiber": 0, "calories": 242}
            },
            "milk": {
                "name": "Milk",
                "type": "Dairy",
                "description": "Milk is a nutrient-rich liquid produced by mammals, primarily consumed from cows. Dairy production has moderate environmental impacts, requiring significant water for livestock maintenance and feed production, producing methane emissions, and using land resources for grazing and feed crops.",
                "details": "Milk provides calcium, protein, and various vitamins, particularly vitamin D when fortified.",
                "nutrition": {"protein": 3.4, "fat": 3.6, "carbs": 4.8, "fiber": 0, "calories": 65}
            },
            "tofu": {
                "name": "Tofu",
                "type": "Legume",
                "description": "Tofu is a plant-based protein made from condensed soy milk, formed into solid white blocks. It has a relatively low environmental impact compared to animal proteins, requiring significantly less water, producing fewer greenhouse gas emissions, and using less land than meat production.",
                "details": "Tofu is rich in protein and a good source of iron, calcium, and manganese.",
                "nutrition": {"protein": 8, "fat": 4, "carbs": 2, "fiber": 1, "calories": 76}
            },
            "rice": {
                "name": "Rice",
                "type": "Grain",
                "description": "Rice is a staple grain consumed by over half the world's population. Its environmental impact is moderate, with significant water requirements for flooding rice paddies, methane emissions from flooded fields, but relatively efficient land use compared to animal products.",
                "details": "Rice provides carbohydrates and small amounts of protein, with brown rice offering more fiber and nutrients than white rice.",
                "nutrition": {"protein": 2.7, "fat": 0.3, "carbs": 28, "fiber": 0.4, "calories": 130}
            }
        }

    #########################
    # Main Public Methods
    #########################
    
    def get_recommendations(self, food_name, impact_preferences=None, limit=3, use_ai=True):
        """
        Generate sustainable food recommendations using both AI and ML approaches
        
        Args:
            food_name: Name of the food item to find alternatives for
            impact_preferences: Dictionary of environmental impact weights
            limit: Maximum number of recommendations to return
            use_ai: Whether to attempt AI-powered recommendations first
            
        Returns:
            Dictionary with alternatives and food information
        """
        self.logger.info(f"Getting recommendations for {food_name}")
        
        if impact_preferences is None:
            impact_preferences = self.default_preferences
        
        try:
            # Get impact data for the original food
            original_impact = self.food_data_service.get_food_impact(food_name)
            if not original_impact:
                return self._fallback_recommendations(food_name, limit)

            # Try AI recommendations first if requested and API key is available
            ai_result = None
            if use_ai and self.api_key:
                try:
                    ai_result = self._get_ai_recommendations(food_name, original_impact, limit)
                    # If we have alternatives, return them
                    if ai_result and ai_result.get('alternatives'):
                        self.food_info = ai_result.get('food_info')
                        return {
                            "source": "ai",
                            "food_info": self.food_info,
                            "alternatives": ai_result['alternatives']
                        }
                except Exception as e:
                    self.logger.error(f"AI recommendation error: {e}")
            
            # Fall back to category-based ML recommendations
            category_recs = self._get_category_recommendations(food_name, limit)
            
            # Store food info from AI attempt if available
            if ai_result and ai_result.get('food_info'):
                self.food_info = ai_result['food_info']
            else:
                # Try to get basic food info
                self.food_info = self._get_basic_food_info(food_name)
            
            return {
                "source": "ml",
                "food_info": self.food_info,
                "alternatives": category_recs[:limit]
            }

        except Exception as e:
            self.logger.error(f"Error getting recommendations: {e}")
            return {
                "source": "fallback",
                "food_info": self._get_basic_food_info(food_name),
                "alternatives": self._fallback_recommendations(food_name, limit)
            }
            
    def get_food_info(self, food_name, impact_data=None):
        """
        Get detailed food information with nutritional facts
        
        Args:
            food_name: Name of the food item
            impact_data: Optional impact data for this food
            
        Returns:
            Dictionary with food information
        """
        if food_name.lower() in self.common_foods:
            return self.common_foods[food_name.lower()]
            
        try:
            return self._get_food_type_info(food_name, impact_data or {})
        except Exception as e:
            self.logger.error(f"Error getting food info: {e}")
            return self._create_meaningful_defaults(food_name)

    #########################
    # Recommendation Methods
    #########################
    
    def _get_ai_recommendations(self, food_name, impact_data, limit=3):
        """
        Get AI-powered recommendations using external AI model
        """
        if not self.api_key:
            return None
            
        try:
            # Get basic food info for prompt
            basic_food_info = self._get_basic_food_info(food_name)

            # Extract metrics from breakdown if present
            metrics = impact_data.get('breakdown', impact_data)
            
            # Build prompt for AI recommendations
            prompt = (
                f"Food Item: {food_name}\n"
                f"Food Type: {basic_food_info['type']}\n"
                f"Description: {basic_food_info['description']}\n\n"
                f"Environmental impacts:\n"
                f"- Carbon footprint: {metrics.get('carbon', 0)} kg CO2/kg\n"
                f"- Water usage: {metrics.get('water', 0)} L/kg\n"
                f"- Energy usage: {metrics.get('energy', 0)} MJ/kg\n"
                f"- Waste: {metrics.get('waste', 0)} kg\n"
                f"- Deforestation risk: {metrics.get('deforestation', 0)} (0-10 scale)\n\n"
                f"Suggest {limit} sustainable alternatives to {food_name} that reduce these environmental impacts.\n"
                f"For each alternative, provide a detailed explanation of its environmental benefits.\n"
                f"FORMAT STRICTLY AS: \"Food Name - Explanation\""
            )

            # Configure AI request
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 300,
                    "topP": 0.8,
                    "topK": 40
                }
            }

            # Make API call with timeout
            response = requests.post(
                self.api_url, 
                json=payload, 
                headers={"Content-Type": "application/json"}, 
                params={"key": self.api_key},
                timeout=5
            )
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            alternatives = self._simple_parse_response(result, food_name, limit)
            
            # Process each alternative to ensure standard format and add sustainability scores
            processed_alternatives = []
            for alt in alternatives:
                # Calculate sustainability improvement
                alt_impact = alt.get('impact', {})
                sustainability_score = self._calculate_sustainability_score(
                    impact_data, 
                    alt_impact.get('breakdown', {}), 
                    self.default_preferences
                )
                
                # Generate explanation if not present
                if not alt.get('explanation'):
                    alt['explanation'] = self._generate_explanation(
                        food_name, 
                        alt['name'], 
                        impact_data, 
                        alt_impact, 
                        self.default_preferences
                    )
                
                # Update sustainability score
                alt['sustainability_improvement'] = round(max(
                    alt.get('sustainability_improvement', 0),
                    sustainability_score * 100
                ))
                
                processed_alternatives.append(alt)
                
            # Get detailed food info in parallel
            food_info = None
            if food_name.lower() in self.common_foods:
                food_info = self.common_foods[food_name.lower()]
                food_info["source"] = "Reliable food database"
            else:
                # Get detailed food info in background
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._get_food_type_info, food_name, impact_data)
                    try:
                        food_info = future.result(timeout=2)
                    except Exception as e:
                        self.logger.warning(f"Detailed food info error: {str(e)}")
                        food_info = basic_food_info
                        
            if not processed_alternatives:
                return None
                
            return {
                "food_info": food_info,
                "alternatives": processed_alternatives
            }
            
        except Exception as e:
            self.logger.error(f"Error in AI recommendations: {e}")
            return None
            
    def _get_category_recommendations(self, food_name, limit):
        """Get recommendations from predefined categories"""
        try:
            alternatives = self.nlp_helper.get_sustainable_alternatives(food_name, limit)
            return [self._format_recommendation(alt) for alt in alternatives]
        except Exception as e:
            self.logger.error(f"Error in category recommendations: {e}")
            return []
            
    def _fallback_recommendations(self, food_name, limit=3):
        """Provide fallback recommendations when no data is available"""
        # Try to determine food category and use category-based replacements
        food_category = "default"
        for category, terms in self.food_categories.items():
            if any(term in food_name.lower() for term in terms):
                food_category = category
                break
                
        try:
            alternatives = self.nlp_helper.get_sustainable_alternatives(food_name, limit)
            if alternatives:
                return [self._format_recommendation(alt) for alt in alternatives]
        except Exception:
            pass
            
        # Last resort - return generic alternatives
        return [
            {
                "name": "Local Seasonal Produce",
                "explanation": f"Local seasonal produce has a much lower carbon footprint than {food_name} due to reduced transportation emissions.",
                "impact": {"breakdown": {"carbon": 0.2, "water": 50, "energy": 0.2, "waste": 0.1, "deforestation": 0.1}},
                "sustainability_improvement": 80.0,
                "similarity_score": 50.0
            },
            {
                "name": "Plant-Based Alternative",
                "explanation": f"Plant-based foods generally have lower environmental impacts than animal products, using less water and producing fewer greenhouse gases than {food_name}.",
                "impact": {"breakdown": {"carbon": 0.5, "water": 100, "energy": 0.5, "waste": 0.2, "deforestation": 0.2}},
                "sustainability_improvement": 70.0,
                "similarity_score": 60.0
            }
        ][:limit]

    #########################
    # Utility Methods
    #########################
    
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
            
            return round(total_score * 100) / 100  # Round to 2 decimal places for internal calculations

        except Exception as e:
            self.logger.error(f"Error calculating sustainability score: {e}")
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
            self.logger.error(f"Error generating explanation: {e}")
            return f"{candidate_name} is a more sustainable alternative to {original_name}."
            
    def _simple_parse_response(self, result, original_food, limit):
        """Simplified parsing focused on robustness"""
        try:
            # Extract text from response
            generated_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            alternatives = []

            # Clean up the text - remove any markdown formatting
            clean_text = re.sub(r'[*#_"`]', '', generated_text)
            
            # Split by lines and process
            lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
            
            # Process each non-empty line
            for line in lines:
                # Skip headers or non-recommendation lines
                if not any(c.isalpha() for c in line):
                    continue
                
                # Remove numbering prefixes like "1. " or "- "
                if (line[0].isdigit() and ". " in line[:3]):
                    line = line.split(". ", 1)[1]
                elif line.startswith("- "):
                    line = line[2:]
                
                # Try to extract food name and explanation
                food_name = ""
                explanation = ""
                
                # Check for the recommended separator format
                if " - " in line:
                    parts = line.split(" - ", 1)
                    food_name = parts[0].strip()
                    explanation = parts[1].strip() if len(parts) > 1 else ""
                # Fallback: try alternative separators
                elif ": " in line:
                    parts = line.split(": ", 1)
                    food_name = parts[0].strip()
                    explanation = parts[1].strip()
                else:
                    # Last resort: take first few words as name
                    words = line.split()
                    if len(words) >= 2:
                        food_name = " ".join(words[:2])
                        explanation = " ".join(words[2:])
                    else:
                        food_name = line
                
                # Ensure we have both name and explanation
                if not food_name:
                    continue
                    
                # Create a default explanation if missing
                if not explanation:
                    explanation = f"{food_name} is a more sustainable alternative to {original_food} with lower environmental impact."
                
                # Create a recommendation
                rec = {
                    "name": food_name.strip(),
                    "explanation": explanation.strip(),
                    "impact": {
                        "breakdown": self._extract_simple_metrics(explanation, original_food)
                    },
                    "sustainability_improvement": 70.0,
                    "similarity_score": 60.0
                }
                
                alternatives.append(rec)

            return alternatives[:limit]

        except Exception as e:
            self.logger.error(f"Error parsing AI response: {e}")
            return []
            
    def _extract_simple_metrics(self, explanation, original_food):
        """Extract simple impact metrics from text"""
        # Default impact values
        metrics = {
            "carbon": 0.5,      # Default carbon footprint (kg CO2/kg)
            "water": 100,       # Default water usage (L/kg)
            "energy": 0.3,      # Default energy usage (MJ/kg)
            "waste": 0.1,       # Default waste (kg)
            "deforestation": 0.2 # Default deforestation risk (0-10)
        }
        
        text = explanation.lower()
        
        # Apply simple rules for better metrics
        if original_food.lower() in ['beef', 'lamb', 'pork']:
            # Plant-based alternatives to high-impact meats
            metrics = {
                "carbon": 0.2,
                "water": 50,
                "energy": 0.2,
                "waste": 0.05,
                "deforestation": 0.1
            }
        elif 'plant' in text or 'vegan' in text or 'vegetable' in text:
            # Plant-based foods
            metrics = {
                "carbon": 0.3,
                "water": 70,
                "energy": 0.2,
                "waste": 0.05,
                "deforestation": 0.1
            }
        
        # Look for percentage improvements
        percentages = re.findall(r'(\d+)%', text)
        if percentages:
            # Use highest mentioned percentage as general improvement
            improvement = max(min(int(p), 95) for p in percentages)
            metrics['improvement_score'] = improvement
        else:
            metrics['improvement_score'] = 70  # Default improvement
            
        return metrics 

    #########################
    # Food Information Methods
    #########################
    
    @lru_cache(maxsize=100)
    def _get_basic_food_info(self, food_name):
        """Get quick basic food info for use in prompts"""
        # First check common foods dictionary for immediate results
        food_name_lower = food_name.lower()
        if food_name_lower in self.common_foods:
            return self.common_foods[food_name_lower]
            
        try:
            # Try to get food type from NLP helper (fast)
            category = self.nlp_helper.get_food_category(food_name)
            
            if category and category != "default":
                return {
                    "name": food_name.capitalize(),
                    "type": category.capitalize(),
                    "description": f"{food_name} is a {category} food item.",
                    "source": "Quick categorization"
                }
                
            # If we don't have a category, make a very fast API call
            # with minimal tokens for just the basic info
            if self.api_key:
                try:
                    quick_prompt = f"In one short sentence, what type of food is '{food_name}'?"
                    
                    payload = {
                        "contents": [{"parts": [{"text": quick_prompt}]}],
                        "generationConfig": {
                            "temperature": 0.1,
                            "maxOutputTokens": 50,
                            "topP": 0.8,
                            "topK": 40
                        }
                    }
                    
                    response = requests.post(
                        self.api_url, 
                        json=payload, 
                        headers={"Content-Type": "application/json"}, 
                        params={"key": self.api_key},
                        timeout=3  # Very short timeout
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        description = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                        
                        # Try to extract food type
                        type_match = re.search(r"(is a|belongs to|falls under|categorized as|type of) (\w+\s*\w*)", description.lower())
                        if type_match:
                            food_type = type_match.group(2).strip().capitalize()
                        else:
                            food_type = "Food item"
                            
                        return {
                            "name": food_name.capitalize(),
                            "type": food_type,
                            "description": description,
                            "source": "Quick AI response"
                        }
                except Exception as quick_api_error:
                    self.logger.debug(f"Quick API call failed: {quick_api_error}")
                
            # Fallback
            return {
                "name": food_name.capitalize(),
                "type": "Food item",
                "description": f"{food_name} is a food item.",
                "source": "Basic info only"
            }
        except Exception as e:
            self.logger.error(f"Error in basic food info: {e}")
            return {
                "name": food_name.capitalize(),
                "type": "Food item",
                "description": f"{food_name} is a food item.",
                "source": "Basic info only"
            }
            
    def _get_food_type_info(self, food_name, impact_data):
        """Extract or determine food type information with nutritional facts"""
        try:
            # Check common foods dictionary first for immediate results
            food_name_lower = food_name.lower()
            if food_name_lower in self.common_foods:
                common_food = dict(self.common_foods[food_name_lower])  # Create a copy
                common_food["source"] = "Reliable food database"
                return common_food
            
            # Default info if nothing is found
            food_info = {
                "name": food_name.capitalize(),
                "type": "Unknown food type",
                "description": f"{food_name} is a food item with various environmental impacts.",
                "nutrition": {
                    "protein": 0,
                    "fat": 0,
                    "carbs": 0,
                    "fiber": 0,
                    "calories": 0
                },
                "details": "",
                "source": "AI estimation"
            }
            
            # Extract info from impact_data if available
            if impact_data.get("description"):
                food_info["description"] = impact_data["description"]
            
            if impact_data.get("food_type"):
                food_info["type"] = impact_data["food_type"]
            
            # Extract nutrition from impact_data if available
            if impact_data.get("nutrition"):
                food_info["nutrition"] = impact_data["nutrition"]
            
            # Try to categorize based on food name
            if not food_info.get("type") or food_info["type"] == "Unknown food type":
                category = self.nlp_helper.get_food_category(food_name)
                if category and category != "default":
                    food_info["type"] = category
            
            # Track if we have nutrition data from a reliable source
            has_reliable_nutrition = False
            
            # Try parallel data fetching to speed things up
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                # Start external data lookups in parallel
                off_future = executor.submit(self._fetch_from_open_food_facts_safely, food_name)
                usda_future = executor.submit(self._fetch_from_usda_safely, food_name)
                ai_future = executor.submit(self._get_nutrition_from_ai, food_name, food_info["type"])
                
                # Get results with timeouts
                try:
                    open_food_data = off_future.result(timeout=2)
                except (concurrent.futures.TimeoutError, Exception):
                    open_food_data = None
                    
                try:
                    usda_data = usda_future.result(timeout=2)
                except (concurrent.futures.TimeoutError, Exception):
                    usda_data = None
                
                try:
                    ai_nutrition_data = ai_future.result(timeout=3)
                except (concurrent.futures.TimeoutError, Exception):
                    ai_nutrition_data = None
                
                # Process results in order of reliability
                # 1. First try USDA data (most reliable)
                if usda_data and usda_data.get("nutrition"):
                    food_info["nutrition"] = usda_data["nutrition"]
                    food_info["source"] = "USDA Database"
                    has_reliable_nutrition = True
                    
                    # Get additional details from USDA
                    if usda_data.get("description"):
                        food_info["details"] = f"USDA Description: {usda_data.get('description')}"
                
                # 2. Then try OpenFoodFacts if USDA didn't have data
                elif open_food_data and open_food_data.get("nutrition"):
                    food_info["nutrition"] = open_food_data["nutrition"]
                    food_info["source"] = "Open Food Facts"
                    has_reliable_nutrition = True
                    
                    # Additional info from OpenFoodFacts
                    if open_food_data.get("ingredients_text"):
                        ingredients_text = open_food_data.get("ingredients_text", "")
                        if ingredients_text:
                            food_info["details"] = f"Ingredients: {ingredients_text[:150]}"
                            if len(ingredients_text) > 150:
                                food_info["details"] += "..."
                
                # 3. Use AI nutrition data if we don't have any from databases
                elif ai_nutrition_data and not has_reliable_nutrition:
                    food_info["nutrition"] = ai_nutrition_data
                    if food_info["source"] == "AI estimation":
                        food_info["source"] = "AI nutritional estimation"
            
            # If we still don't have good info or nutrition data is incomplete, generate rich description using AI
            if (food_info["type"] == "Unknown food type" or 
                len(food_info["description"]) < 10 or 
                not food_info["details"] or
                self._is_nutrition_empty(food_info["nutrition"])):
                try:
                    ai_info = self._generate_rich_food_description(food_name, food_info["type"])
                    
                    # Update with AI-generated info
                    if len(food_info["description"]) < len(ai_info["description"]):
                        food_info["description"] = ai_info["description"]
                    
                    if not food_info["details"] and ai_info["details"]:
                        food_info["details"] = ai_info["details"]
                        
                    if food_info["type"] == "Unknown food type" and ai_info["type"] != "Unknown food type":
                        food_info["type"] = ai_info["type"]
                        
                    # Use AI nutrition if we don't have any or it's incomplete
                    if self._is_nutrition_empty(food_info["nutrition"]) and not self._is_nutrition_empty(ai_info["nutrition"]):
                        food_info["nutrition"] = ai_info["nutrition"]
                        if food_info["source"] == "AI estimation":
                            food_info["source"] = "AI nutritional estimation"
                except Exception as ai_error:
                    self.logger.warning(f"Error generating rich description: {ai_error}")
            
            # As a last resort, create nutrition values based on food category
            if self._is_nutrition_empty(food_info["nutrition"]):
                food_info["nutrition"] = self._validate_nutrition_values({}, food_info["type"])
                if food_info["source"] == "AI estimation":
                    food_info["source"] = "Category-based nutrition estimate"
                
            return food_info
        
        except Exception as e:
            self.logger.error(f"Error getting food type info: {e}")
            # Try the common foods dictionary as a last resort
            food_name_lower = food_name.lower()
            if food_name_lower in self.common_foods:
                common_food = dict(self.common_foods[food_name_lower])
                common_food["source"] = "Fallback food database"
                return common_food
                
            # Return improved default values instead of empty data
            return self._create_meaningful_defaults(food_name)
            
    def _create_meaningful_defaults(self, food_name):
        """Create meaningful default food information"""
        # Try to categorize based on name
        try:
            category = self.nlp_helper.get_food_category(food_name)
            
            if category != "default":
                # Use the category-specific defaults
                food_type = category.capitalize()
                # Use _expand_description to get good category-specific description
                description = self._expand_description("", food_name, food_type)
                
                # Create defaults based on food category
                nutrition_defaults = self._validate_nutrition_values({}, food_type)
                
                return {
                    "name": food_name.capitalize(),
                    "type": food_type,
                    "description": description,
                    "details": f"{food_name} is commonly consumed as part of a balanced diet.",
                    "nutrition": nutrition_defaults,
                    "source": "Default information with food category matching"
                }
        except Exception:
            pass
            
        # Generic fallback if all else fails
        return {
            "name": food_name.capitalize(),
            "type": "Food item",
            "description": f"{food_name} is a food item that contributes to your diet. Like many food items, it has an environmental footprint related to its production, processing, and transportation that impacts carbon emissions, water usage, and land use.",
            "details": "No specific details available for this food item.",
            "nutrition": {
                "protein": 5,
                "fat": 5,
                "carbs": 15,
                "fiber": 2,
                "calories": 120
            },
            "source": "Generic food information"
        } 

    #########################
    # Nutrition and Data Methods
    #########################
    
    def _is_nutrition_empty(self, nutrition):
        """Check if nutrition data is effectively empty"""
        if not nutrition:
            return True
            
        # Check if all values are zero or close to zero
        zero_values = 0
        for key in ["protein", "fat", "carbs", "fiber", "calories"]:
            if nutrition.get(key, 0) < 0.1:
                zero_values += 1
                
        # If at least 3 values are zero, consider it empty
        return zero_values >= 3
        
    def _get_nutrition_from_ai(self, food_name, food_type):
        """Get nutrition facts using AI model"""
        if not self.api_key:
            return None
            
        try:
            prompt = (
                f"Provide realistic standard nutritional values per 100g for {food_name} (food type: {food_type}).\n"
                f"Return ONLY numeric values (no units) for:\n"
                f"- Protein (g)\n"
                f"- Fat (g)\n"
                f"- Carbohydrates (g)\n"
                f"- Fiber (g)\n"
                f"- Calories (kcal)\n\n"
                f"Format as JSON with these exact keys: protein, fat, carbs, fiber, calories"
            )
            
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 150,
                    "topP": 0.8,
                    "topK": 40
                }
            }
            
            response = requests.post(
                self.api_url, 
                json=payload, 
                headers={"Content-Type": "application/json"}, 
                params={"key": self.api_key},
                timeout=3  # Short timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                text_result = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                
                # Try to parse if it's valid JSON
                import json
                try:
                    json_start = text_result.find('{')
                    json_end = text_result.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = text_result[json_start:json_end]
                        data = json.loads(json_str)
                        
                        # Extract and clean nutrition values
                        clean_nutrition = {}
                        
                        # Process each nutrition value to handle possible units
                        for key in ["protein", "fat", "carbs", "fiber", "calories"]:
                            value = data.get(key, 0)
                            # Convert to string to handle both numeric and string values
                            value_str = str(value)
                            # Extract numeric part using regex
                            numeric_match = re.search(r'(\d+\.?\d*)', value_str)
                            if numeric_match:
                                clean_nutrition[key] = float(numeric_match.group(1))
                            else:
                                clean_nutrition[key] = 0
                        
                        # Validate nutritional values against standard ranges
                        clean_nutrition = self._validate_nutrition_values(clean_nutrition, food_type)
                        return clean_nutrition
                except (json.JSONDecodeError, ValueError, AttributeError) as e:
                    self.logger.warning(f"Failed to parse AI nutrition JSON: {e}")
                
                # Fallback: Try to extract information using regex
                nutrition_values = {}
                for nutrient in ["protein", "fat", "carbs", "fiber", "calories"]:
                    # Match a number that might be followed by units
                    nutrient_match = re.search(
                        rf'{nutrient}["\s:]+(\d+\.?\d*)(?:[^0-9.]*)',
                        text_result, 
                        re.IGNORECASE
                    )
                    if nutrient_match:
                        try:
                            nutrition_values[nutrient] = float(nutrient_match.group(1))
                        except ValueError:
                            nutrition_values[nutrient] = 0
                    else:
                        nutrition_values[nutrient] = 0
                
                # Validate values
                return self._validate_nutrition_values(nutrition_values, food_type)
        except Exception as e:
            self.logger.error(f"Error getting nutrition from AI: {e}")
            return None
            
    def _fetch_from_open_food_facts_safely(self, food_name):
        """Fetch from Open Food Facts with error handling and timeout"""
        try:
            data_service = self.food_data_service
            return data_service.fetch_from_open_food_facts(food_name)
        except Exception as e:
            self.logger.debug(f"Error fetching from Open Food Facts: {e}")
            return None
    
    def _fetch_from_usda_safely(self, food_name):
        """Fetch from USDA with error handling and timeout"""
        try:
            data_service = self.food_data_service
            return data_service.fetch_from_usda(food_name)
        except Exception as e:
            self.logger.debug(f"Error fetching from USDA: {e}")
            return None
            
    def _generate_rich_food_description(self, food_name, food_type="Unknown food type"):
        """Generate rich food description with nutritional facts using AI"""
        if not self.api_key:
            return self._create_meaningful_defaults(food_name)
            
        try:
            prompt = (
                f"Provide detailed information about '{food_name}' as a food item:\n\n"
                f"1. Write a comprehensive 2-3 line description addressing:\n"
                f"   - What this food item is\n"
                f"   - Its key ingredients or composition\n"
                f"   - Its environmental impact (carbon footprint, water usage, land use)\n\n"
                f"2. Food category/type\n\n"
                f"3. One interesting nutritional or culinary fact\n\n"
                f"4. Standard nutritional content per 100g with ONLY NUMERIC VALUES (no units):\n"
                f"   - Protein (g)\n"
                f"   - Fat (g)\n"
                f"   - Carbohydrates (g)\n"
                f"   - Fiber (g)\n"
                f"   - Calories (kcal)\n\n"
                f"Format as JSON with keys: description, type, details, nutrition (with numeric values only)"
            )
            
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 500,
                    "topP": 0.9,
                    "topK": 40
                }
            }
            
            response = requests.post(
                self.api_url, 
                json=payload, 
                headers={"Content-Type": "application/json"}, 
                params={"key": self.api_key},
                timeout=4  # Shorter timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                text_result = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                
                # Try to parse if it's valid JSON
                import json
                try:
                    json_start = text_result.find('{')
                    json_end = text_result.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = text_result[json_start:json_end]
                        data = json.loads(json_str)
                        
                        # Extract and clean nutrition values
                        nutrition = data.get("nutrition", {})
                        clean_nutrition = {}
                        
                        # Process each nutrition value to handle possible units
                        for key in ["protein", "fat", "carbs", "fiber", "calories"]:
                            value = nutrition.get(key, 0)
                            # Convert to string to handle both numeric and string values
                            value_str = str(value)
                            # Extract numeric part using regex
                            numeric_match = re.search(r'(\d+\.?\d*)', value_str)
                            if numeric_match:
                                clean_nutrition[key] = float(numeric_match.group(1))
                            else:
                                clean_nutrition[key] = 0
                        
                        # Validate nutritional values against standard ranges
                        clean_nutrition = self._validate_nutrition_values(clean_nutrition, food_type)
                        
                        # Extract description and ensure it's 2-3 lines
                        description = data.get("description", "")
                        if len(description.split('.')) < 2:
                            # Too short, expand it
                            description = self._expand_description(description, food_name, food_type)
                        
                        # Validate and extract data
                        return {
                            "name": food_name.capitalize(),
                            "type": data.get("type", food_type).capitalize(),
                            "description": description,
                            "details": data.get("details", ""),
                            "nutrition": clean_nutrition
                        }
                except (json.JSONDecodeError, ValueError, AttributeError) as e:
                    self.logger.warning(f"Failed to parse AI food info JSON: {e}")
                
                # Fallback: Try to extract information using regex
                description_match = re.search(r'description["\s:]+([^"{}]+)', text_result, re.IGNORECASE)
                description = description_match.group(1).strip() if description_match else ""
                
                # Ensure description is long enough
                if description and len(description.split('.')) < 2:
                    description = self._expand_description(description, food_name, food_type)
                
                type_match = re.search(r'type["\s:]+([^",{}]+)', text_result, re.IGNORECASE)
                extracted_type = type_match.group(1).strip() if type_match else food_type
                
                details_match = re.search(r'details["\s:]+([^"{}]+)', text_result, re.IGNORECASE)
                details = details_match.group(1).strip() if details_match else ""
                
                # Try to extract nutrition values - now handle units like g or mg
                nutrition_values = {}
                for nutrient in ["protein", "fat", "carbs", "fiber", "calories"]:
                    # Match a number that might be followed by units
                    nutrient_match = re.search(
                        rf'{nutrient}["\s:]+(\d+\.?\d*)(?:[^0-9.]*)',
                        text_result, 
                        re.IGNORECASE
                    )
                    if nutrient_match:
                        try:
                            nutrition_values[nutrient] = float(nutrient_match.group(1))
                        except ValueError:
                            nutrition_values[nutrient] = 0
                    else:
                        nutrition_values[nutrient] = 0
                
                # Validate nutritional values against standard ranges
                nutrition_values = self._validate_nutrition_values(nutrition_values, extracted_type)
                
                return {
                    "name": food_name.capitalize(),
                    "type": extracted_type.capitalize(),
                    "description": description,
                    "details": details,
                    "nutrition": nutrition_values
                }
                
        except Exception as e:
            self.logger.error(f"Error generating rich food description: {e}")
            
        # Fallback with decent default description
        return self._create_meaningful_defaults(food_name)
        
    def _validate_nutrition_values(self, nutrition, food_type):
        """Validate and adjust nutrition values to realistic ranges"""
        # Default values for different food types
        defaults = {
            "meat": {"protein": 20, "fat": 15, "carbs": 0, "fiber": 0, "calories": 250},
            "dairy": {"protein": 5, "fat": 5, "carbs": 5, "fiber": 0, "calories": 100},
            "vegetables": {"protein": 2, "fat": 0.5, "carbs": 5, "fiber": 2, "calories": 30},
            "fruits": {"protein": 1, "fat": 0.3, "carbs": 15, "fiber": 2, "calories": 60},
            "grains": {"protein": 3, "fat": 1, "carbs": 25, "fiber": 3, "calories": 120},
            "nuts": {"protein": 20, "fat": 50, "carbs": 10, "fiber": 8, "calories": 600},
            "legumes": {"protein": 8, "fat": 1, "carbs": 20, "fiber": 7, "calories": 120},
            "default": {"protein": 5, "fat": 5, "carbs": 15, "fiber": 2, "calories": 120}
        }
        
        # Reasonable ranges
        ranges = {
            "protein": (0, 40),    # g per 100g
            "fat": (0, 80),        # g per 100g
            "carbs": (0, 90),      # g per 100g
            "fiber": (0, 15),      # g per 100g
            "calories": (0, 900)   # kcal per 100g
        }
        
        # Use food type to determine appropriate default values
        food_type_lower = food_type.lower()
        default_values = next(
            (defaults[t] for t in defaults if t in food_type_lower),
            defaults["default"]
        )
        
        # Validate each nutrition value
        validated = {}
        for key, value in nutrition.items():
            min_val, max_val = ranges.get(key, (0, 100))
            
            # If value is 0 or out of reasonable range, use the default
            if value == 0 or value < min_val or value > max_val:
                validated[key] = default_values.get(key, 0)
            else:
                validated[key] = value
                
        return validated
        
    def _expand_description(self, description, food_name, food_type):
        """Expand a short description to include environmental impact"""
        # If description is empty or too short, create a meaningful one
        if not description or len(description) < 20:
            food_type_lower = food_type.lower()
            
            if "meat" in food_type_lower:
                return f"{food_name} is a meat product that typically requires significant resources to produce. Meat production generally has a higher environmental footprint with substantial water usage, land requirements for grazing or feed production, and higher greenhouse gas emissions compared to plant-based alternatives."
                
            elif "dairy" in food_type_lower:
                return f"{food_name} is a dairy product derived from animal milk. Dairy production contributes to greenhouse gas emissions through livestock, requires substantial water for animal care and feed crops, and impacts land use. However, its environmental footprint is generally lower than that of meat products."
                
            elif "vegetable" in food_type_lower:
                return f"{food_name} is a vegetable with a typically low environmental impact. Vegetables generally require less water, produce fewer greenhouse gas emissions, and use less land compared to animal products. They're considered environmentally sustainable food choices that provide essential nutrients."
                
            elif "fruit" in food_type_lower:
                return f"{food_name} is a fruit that generally has a moderate environmental footprint. While fruits require water for irrigation, their carbon emissions and land use impact are relatively low compared to animal products. Local, seasonal fruits typically have the lowest environmental impact."
                
            elif "grain" in food_type_lower:
                return f"{food_name} is a grain product that forms a dietary staple in many cultures. Grains generally have a moderate environmental footprint, requiring land for cultivation but producing relatively low greenhouse gas emissions. They're considered an efficient food source in terms of resources needed per calorie provided."
                
            else:
                return f"{food_name} is a food item in the {food_type} category. Like all foods, it has an environmental footprint related to its production, processing, and distribution. This includes impacts on greenhouse gas emissions, water usage, and land use, though the specific impact varies based on production methods and geographic location."
        
        # If description exists but is too short, add environmental context
        if "environmental" not in description.lower() and "impact" not in description.lower():
            description += f" Like most food items, {food_name} has an environmental footprint related to its production and distribution, affecting water usage, carbon emissions, and land use."
            
        return description 