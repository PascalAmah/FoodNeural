import requests
import logging
from app.config import Config
from app.services.recommendation_service import RecommendationService

class AIRecommendationService:
    def __init__(self):
        """Initialize AI recommendation service with fallback handler"""
        self.logger = logging.getLogger(__name__)
        self.api_key = Config.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("Gemini API key is not configured")
        
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        self.fallback_service = RecommendationService()

    def get_ai_recommendations(self, food_name, impact_data, limit=3):
        """Get AI-powered recommendations with robust fallback"""
        try:
            # Construct prompt
            prompt = (
                f"I have a food item '{food_name}' with the following environmental impacts:\n"
                f"- Carbon footprint: {impact_data['carbon']} kg CO2/kg\n"
                f"- Water usage: {impact_data['water']} L/kg\n"
                f"- Energy usage: {impact_data['energy']} MJ/kg\n"
                f"- Waste: {impact_data['waste']} kg\n"
                f"- Deforestation risk: {impact_data['deforestation']} (0-10 scale)\n\n"
                f"Suggest {limit} sustainable alternative foods that reduce these impacts.\n"
                f"Format: numbered list with 'Food Name - Brief explanation focusing on impact reductions'"
            )

            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 200,
                    "topP": 0.8,
                    "topK": 40
                }
            }
            headers = {"Content-Type": "application/json"}
            params = {"key": self.api_key}

            # Make API call
            response = requests.post(
                self.api_url, 
                json=payload, 
                headers=headers, 
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            alternatives = self._parse_ai_response(result, limit)

            # Use fallback if AI response is insufficient
            if not alternatives:
                self.logger.warning(f"No valid AI recommendations for {food_name}, using fallback")
                return {"alternatives": self.fallback_service._fallback_recommendations(food_name, limit)}

            return {"alternatives": alternatives}

        except requests.exceptions.HTTPError as e:
            self.logger.error(f"Gemini API error: {e.response.status_code} - {e.response.text}")
            return {"alternatives": self.fallback_service._fallback_recommendations(food_name, limit)}
        except Exception as e:
            self.logger.error(f"Error with Gemini API: {e}")
            return {"alternatives": self.fallback_service._fallback_recommendations(food_name, limit)}

    def _parse_ai_response(self, result, limit):
        """Parse and validate AI response"""
        try:
            generated_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            alternatives = []

            for line in generated_text.split("\n"):
                if line.strip() and line[0].isdigit() and ". " in line:
                    try:
                        parts = line.split(". ", 1)[1].split(" - ", 1)
                        if len(parts) == 2:
                            name, explanation = parts
                            if self._validate_alternative(name, explanation):
                                alternatives.append({
                                    "name": name.strip(),
                                    "explanation": explanation.strip(),
                                    # Add default impact metrics for AI suggestions
                                    "impact": {
                                        "breakdown": {
                                            "carbon": 0.5,
                                            "water": 100,
                                            "energy": 0.3,
                                            "waste": 0.1,
                                            "deforestation": 0.2
                                        }
                                    },
                                    "sustainability_improvement": 70.0,
                                    "similarity_score": 60.0
                                })
                    except (IndexError, ValueError):
                        continue

            return alternatives[:limit]

        except (KeyError, IndexError) as e:
            self.logger.error(f"Error parsing AI response: {e}")
            return []

    def _validate_alternative(self, name, explanation):
        """Validate generated alternative"""
        if not name or not explanation:
            return False
        if len(name) > 100 or len(explanation) > 500:
            return False
        return True