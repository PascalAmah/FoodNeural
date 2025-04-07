import os
from flask import jsonify
from app import create_app

app = create_app()

@app.route('/', methods=['GET', 'HEAD'])
def root():
    return jsonify({"message": "Welcome to the Food Neural API"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)