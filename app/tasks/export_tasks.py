from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.services.pdf import generate_attendance_pdf
from app.services.drive import DriveService
from app.config import settings
from app.models.session import AttendanceSession
from app.models.attendance_record import AttendanceRecord
from sqlalchemy import select
# from telegram import Bot # To send message back

@celery_app.task
def export_report_to_drive(session_id: str, telegram_chat_id: int):
    with SessionLocal() as db:
        session = db.get(AttendanceSession, session_id)
        if not session:
            return
            
        # Mocking some data for the report
        records = db.scalars(select(AttendanceRecord).where(AttendanceRecord.session_id == session_id)).all()
        
        session_data = {
            "class_name": "Default Class", # Should come from session.class.name
            "date": session.date.strftime("%Y-%m-%d"),
            "instructor_name": "Instructor",
            "records": records,
            "stats": {
                "total": len(records),
                "present": len([r for r in records if r.status in ['auto_approved', 'approved']]),
                "absent": len([r for r in records if r.status == 'unrecognized']),
                "rate": round(len([r for r in records if r.status in ['auto_approved', 'approved']]) / len(records) * 100 if records else 0, 1)
            }
        }
        
        pdf_bytes = generate_attendance_pdf(session_data)

        drive = DriveService(settings.GOOGLE_CREDENTIALS_PATH)
        reports_folder = drive.get_or_create_folder('Reports')
        # class_folder = drive.get_or_create_folder(session_data['class_name'], reports_folder)

        filename = f"attendance-{session_data['date']}.pdf"
        file_id = drive.upload_bytes(pdf_bytes, filename, reports_folder, 'application/pdf')
        link = drive.get_shareable_link(file_id)

        # In a real implementation, you'd use the bot to send the message
        print(f"✅ Report ready for session {session_id}: {link}")
