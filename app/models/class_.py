from sqlalchemy import UUID, String, ForeignKey, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .student import Student

class Class(Base):
    __tablename__ = "classes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=True) # fundamental, frontend, backend
    level: Mapped[str] = mapped_column(String(50), nullable=True) # standard, advanced
    instructor_name: Mapped[str] = mapped_column(String(255), nullable=True)
    schedule: Mapped[dict] = mapped_column(JSON, nullable=True) # JSONB in Postgres
    drive_folder_id: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    students: Mapped[List["Student"]] = relationship(back_populates="class_")
