import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Config:
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = FLASK_ENV == 'development'
    
    # API URLs
    USDA_API_URL = "https://api.nal.usda.gov/fdc/v1"
    OPEN_FOOD_FACTS_URL = "https://world.openfoodfacts.org"
    FAO_DATA_URL = "https://www.fao.org/platforms/gleam/data/en/"

    # API Keys
    USDA_API_KEY = os.getenv("USDA_API_KEY", "default_usda_key")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # CORS settings
    CORS_HEADERS = 'Content-Type'
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

    # Cache settings
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300

    @classmethod
    def validate_config(cls):
        """Validate required configuration variables"""
        if cls.FLASK_ENV == "production":
            required_keys = ["USDA_API_KEY", "GEMINI_API_KEY", "SECRET_KEY"]
            missing_keys = [key for key in required_keys if not getattr(cls, key)]
            if missing_keys:
                raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")