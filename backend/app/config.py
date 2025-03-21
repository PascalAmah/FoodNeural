import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API URLs
    USDA_API_URL = "https://api.nal.usda.gov/fdc/v1"
    OPEN_FOOD_FACTS_URL = "https://world.openfoodfacts.org/api/v0/product/"
    FAO_DATA_URL = "https://www.fao.org/platforms/gleam/data/en/"

    USDA_API_KEY = os.getenv('USDA_API_KEY', 'default_usda_key')
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    # HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '')
    
    # Environment settings
    ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = ENV == 'development'
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration variables"""
        if cls.ENV == 'production':
            required_keys = ['USDA_API_KEY', 'GEMINI_API_KEY']
            missing_keys = [key for key in required_keys if not getattr(cls, key)]
            if missing_keys:
                raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")