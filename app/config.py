from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str
    ENVIRONMENT: str = "development"
    SECRET_KEY: str
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_ADMIN_IDS: List[int] = []
    ENABLE_WHITELIST: bool = True

    # File Management
    UPLOAD_DIR: str = "uploads/attendance"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".pdf"]

    # OCR
    OCR_PRIMARY_ENGINE: str = "google_vision"
    OCR_FALLBACK_ENGINE: str = "tesseract"
    GOOGLE_CREDENTIALS_PATH: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GMAIL_CREDENTIALS_PATH: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()