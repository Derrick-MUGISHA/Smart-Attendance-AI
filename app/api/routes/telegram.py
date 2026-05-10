from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/telegram", tags=["Telegram"])

@router.get("/pipeline")
async def telegram_pipeline():
    return {
        "status": "running",
        "environment": settings.ENVIRONMENT
    }