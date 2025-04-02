# from flask import Flask
# from flask_cors import CORS
# from app.config import Config

# def create_app():
#     app = Flask(__name__)
#     CORS(app)
    
#     # Load config
#     app.config.from_object(Config)
    
#     # Register blueprints
#     from app.routes.api import api_bp
#     app.register_blueprint(api_bp, url_prefix='/api')
    
#     return app

from flask import Flask
from flask_cors import CORS
from app.config import Config

def create_app():
    app = Flask(__name__)
    
    # More specific CORS configuration
    CORS(app, resources={r"/api/*": {"origins": "https://food-neural.vercel.app"}}, supports_credentials=True)
    
    # Load config
    app.config.from_object(Config)
    
    # Register blueprints
    from app.routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app