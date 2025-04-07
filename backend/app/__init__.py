from flask import Flask, jsonify
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
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    @app.route('/', methods=['GET', 'HEAD'])
    def root():
        """Root endpoint returning welcome message"""
        return jsonify({"message": "Welcome to the Food Neural API"})
    
    app.register_blueprint(api_bp, url_prefix='/api')
    return app