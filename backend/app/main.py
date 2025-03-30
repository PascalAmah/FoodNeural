from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.api import router as api_router
from app.config import Config

# Validate configuration
Config.validate_config()

app = FastAPI(title="FoodNeural API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost", "http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the FoodNeural API!",
        "environment": Config.ENV,
        "debug": Config.DEBUG,
    }