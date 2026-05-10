from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/email", tags=["Email"])

@router.get("/pipeline")
async def email_pipeline():
    return {
        "status": "running",
        "environment": settings.ENVIRONMENT
    }