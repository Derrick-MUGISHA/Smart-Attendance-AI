from sqlalchemy import UUID, String, BigInteger, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import uuid
from datetime import datetime

class UploadSession(Base):
    __tablename__ = "upload_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    folder_path: Mapped[str] = mapped_column(String(511), nullable=False)
    file_count: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(50), default="active") # active, completed, cancelled
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
