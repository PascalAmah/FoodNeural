# import os
# import uvicorn
# from app.main import app

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))
#     uvicorn.run(app, host="0.0.0.0", port=port)


from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)