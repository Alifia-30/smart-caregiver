from fastapi import FastAPI
from src.app.routers import auth_google, health, elderly
from src.app.routers import auth as auth_router
from src.app.routers import dashboard
from src.app.routers import viewer
from src.app.routers import notification
from src.app.routers import schedule
from src.app.routers import recommendation
from src.app.routers import internal_jobs
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
app.include_router(notification.router, prefix="/notifications")
app.include_router(schedule.router)
app.include_router(recommendation.router)
app.include_router(internal_jobs.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Smart Caregiver API",
        "docs": "/docs"
    }

@app.get("/health-check")
async def health_check():
    return {"status": "healthy"}
