from app import create_app
import os

if __name__ == "__main__":
    if not os.getenv('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'production'
    
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))