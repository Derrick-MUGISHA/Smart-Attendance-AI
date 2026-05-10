from sqlalchemy import UUID, String, ForeignKey, DateTime, Text, Integer, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import uuid
from datetime import datetime

class OCRJob(Base):
    __tablename__ = "ocr_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("attendance_sessions.id"), nullable=True)
    raw_image_drive_id: Mapped[str] = mapped_column(String(255), nullable=True)
    processed_image_drive_id: Mapped[str] = mapped_column(String(255), nullable=True)
    raw_ocr_text: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="queued")
    engine: Mapped[str] = mapped_column(String(50), nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    error: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
