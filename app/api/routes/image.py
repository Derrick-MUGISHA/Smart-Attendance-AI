from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/image", tags=["Image"])

@router.get("/pipeline")
async def image_pipeline():
    return {
        "status": "running",
        "environment": settings.ENVIRONMENT
    }