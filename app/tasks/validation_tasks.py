from app.tasks.celery_app import celery_app
from app.services.matching import match_all
from app.database import SessionLocal
from app.models.student import Student
from app.models.attendance_record import AttendanceRecord
from app.models.session import AttendanceSession
from app.config import settings
from sqlalchemy import select

from app.services.gmail_service import gmail_service
from app.models.class_ import Class

@celery_app.task
def validate_attendance(session_id: str, ocr_names: list[str]):
    with SessionLocal() as db:
        # Get session metadata to identify the class category/level
        from app.models.upload_session import UploadSession
        upload_session = db.get(UploadSession, session_id)
        
        # Determine class_id from metadata or use default
        class_id = None
        if upload_session and upload_session.metadata_json:
            cat = upload_session.metadata_json.get("course")
            lvl = upload_session.metadata_json.get("level")
            stmt_class = select(Class).where(Class.category == cat, Class.level == lvl)
            class_obj = db.scalars(stmt_class).first()
            if class_obj:
                class_id = class_obj.id

        # Get session and class
        session_obj = db.get(AttendanceSession, session_id)
        if not session_obj and upload_session:
            # Create session_obj if it doesn't exist (using upload_session id)
            session_obj = AttendanceSession(
                id=upload_session.id,
                class_id=class_id,
                date=upload_session.created_at.date(),
                status="pending"
            )
            db.add(session_obj)
            db.commit()
            db.refresh(session_obj)

        if not session_obj:
            return
        
        # Update session class if found
        if class_id:
            session_obj.class_id = class_id
        
        # Get all students in the class
        stmt = select(Student)
        if session_obj.class_id:
            stmt = stmt.where(Student.class_id == session_obj.class_id)
        students = db.scalars(stmt).all()
        student_names = [s.name for s in students]
        
        # Match names
        matches = match_all(ocr_names, student_names)
        
        # Fetch absentee emails
        absentee_emails = gmail_service.get_latest_absentee_emails(days_back=1)
        
        present_student_ids = set()
        for match in matches:
            # Find student_id if matched
            student_id = None
            if match['matched']:
                for s in students:
                    if s.name == match['matched']:
                        student_id = s.id
                        present_student_ids.add(student_id)
                        break
            
            record = AttendanceRecord(
                session_id=session_id,
                student_id=student_id,
                ocr_raw_name=match['ocr_raw'],
                matched_name=match['matched'],
                confidence_score=match['score'],
                status=match['status'],
                is_absent=False
            )
            db.add(record)
        
        # Identify absent students and check against emails
        for student in students:
            if student.id not in present_student_ids:
                # Check if student name or email appears in absentee emails
                absence_reason = "Absent (No communication)"
                
                for email in absentee_emails:
                    if student.name.lower() in email['body'].lower() or \
                       (student.email and student.email.lower() in email['sender'].lower()):
                        absence_reason = f"Absent: {email['subject']} - {email['body'][:100]}..."
                        break
                
                record = AttendanceRecord(
                    session_id=session_id,
                    student_id=student.id,
                    ocr_raw_name="N/A",
                    matched_name=student.name,
                    confidence_score=1.0,
                    status="absent",
                    is_absent=True,
                    absence_reason=absence_reason
                )
                db.add(record)
        
        db.commit()
        
        # Notify user for confirmation
        if upload_session:
            from telegram import Bot
            import asyncio
            
            async def notify():
                bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
                from app.bot.keyboards import get_confirm_attendance_keyboard
                
                summary = f"📊 *AI processing completed. Review ready.*\n\n"
                summary += f"Course: {upload_session.metadata_json.get('course', 'Unknown').capitalize()}\n"
                summary += f"Level: {upload_session.metadata_json.get('level', 'Unknown').capitalize()}\n"
                summary += f"Found: {len(matches)} students\n"
                summary += f"Absent: {len(students) - len(present_student_ids)} students\n\n"
                summary += "*Do you want to confirm this attendance list?*"
                
                try:
                    await bot.send_message(
                        chat_id=upload_session.telegram_user_id,
                        text=summary,
                        parse_mode="Markdown",
                        reply_markup=get_confirm_attendance_keyboard()
                    )
                except Exception as e:
                    print(f"Failed to notify user: {e}")

            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(notify())
            else:
                loop.run_until_complete(notify())
