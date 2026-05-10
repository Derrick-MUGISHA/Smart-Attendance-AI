from fastapi import FastAPI

from app.api.routes import (
    health_router,
    telegram_router,
    image_router,
    email_router,
    root_router,
)
from app.api.routes.attendance import router as attendance_router

app = FastAPI(
    title="Smart Attendance AI Powered",
    description="AI-powered attendance automation API",
    version="0.1.0"
)

app.include_router(root_router)
app.include_router(health_router)
app.include_router(telegram_router)
app.include_router(image_router)
app.include_router(email_router)
app.include_router(attendance_router)