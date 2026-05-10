from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
import uuid

from app.database import get_db
from app.services.file_manager import file_manager
from app.models.attendance_record import AttendanceRecord
from app.models.session import AttendanceSession
from app.config import settings

router = APIRouter(prefix="/attendance", tags=["Attendance"])

@router.post("/upload")
async def upload_attendance(file: UploadFile = File(...), sender_id: int = 0):
    content = await file.read()
    
    # Simple validation
    ext = "." + file.filename.split(".")[-1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")

    metadata = await file_manager.save_upload(content, file.filename, sender_id)
    return {"message": "File uploaded successfully", "metadata": metadata}

@router.get("/today")
async def get_today_attendance(db: Session = Depends(get_db)):
    today = date.today()
    records = db.query(AttendanceRecord).join(AttendanceSession).filter(AttendanceSession.date == today).all()
    return records

@router.get("/history")
async def get_attendance_history(limit: int = 10, db: Session = Depends(get_db)):
    records = db.query(AttendanceRecord).order_by(AttendanceRecord.created_at.desc()).limit(limit).all()
    return records

@router.delete("/{id}")
async def delete_attendance(id: uuid.UUID, db: Session = Depends(get_db)):
    record = db.query(AttendanceRecord).filter(AttendanceRecord.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    db.delete(record)
    db.commit()
    return {"message": "Record deleted successfully"}

@router.get("/loss-of-attendance")
async def check_loss_of_attendance(student_id: uuid.UUID, threshold: int = 3, db: Session = Depends(get_db)):
    """
    Checks if a student has lost attendance (e.g., 3 consecutive absences).
    """
    records = db.query(AttendanceRecord)\
        .filter(AttendanceRecord.student_id == student_id)\
        .order_by(AttendanceRecord.created_at.desc())\
        .limit(threshold).all()
    
    if len(records) < threshold:
        return {"lost": False, "consecutive_absences": 0}
    
    absences = 0
    for r in records:
        if r.is_absent:
            absences += 1
        else:
            break
            
    return {
        "student_id": student_id,
        "lost": absences >= threshold,
        "consecutive_absences": absences
    }

@router.post("/process")
async def process_attendance(session_id: uuid.UUID):
    # Standardized response format
    return {
        "status": "processing",
        "message": "AI processing started using OCR + AI...",
        "data": {
            "session_id": str(session_id)
        },
        "next_action": "waiting_for_review"
    }
