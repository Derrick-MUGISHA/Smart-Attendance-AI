from sqlalchemy import UUID, String, ForeignKey, DateTime, Float, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import uuid
from datetime import datetime

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("attendance_sessions.id"), nullable=True)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("students.id"), nullable=True)
    ocr_raw_name: Mapped[str] = mapped_column(String(255), nullable=False)
    matched_name: Mapped[str] = mapped_column(String(255), nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=True)
    is_absent: Mapped[bool] = mapped_column(default=False)
    absence_reason: Mapped[str] = mapped_column(String(511), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    reviewed_by: Mapped[str] = mapped_column(String(255), nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
