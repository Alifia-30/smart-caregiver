from fastapi import FastAPI
from src.app.routers import auth_google, health, elderly
from src.app.routers import auth as auth_router
from src.app.routers import dashboard
from src.app.routers import viewer
from dotenv import load_dotenv

# Load .env file
load_dotenv()

app = FastAPI(
    title="Smart Caregiver API",
    description="Backend API for Smart Caregiver Application",
    version="1.0.0"
)

# Register routers
app.include_router(auth_router.router)
app.include_router(auth_google.router)
app.include_router(elderly.router)
app.include_router(health.router)
app.include_router(dashboard.router)
app.include_router(viewer.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Smart Caregiver API",
        "docs": "/docs"
    }

@app.get("/health-check")
async def health_check():
    return {"status": "healthy"}
