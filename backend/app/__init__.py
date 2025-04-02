from flask import Flask
from flask_cors import CORS
from app.routes.api import api_bp

def create_app():
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "https://food-neural.vercel.app",
                "http://localhost:5173"
            ],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    app.register_blueprint(api_bp, url_prefix='/api')
    return app