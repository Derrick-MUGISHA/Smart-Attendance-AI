from app.tasks.celery_app import celery_app
from app.services.preprocessing import preprocess_image
from app.services.ocr import OCRService
from app.services.drive import DriveService
from app.config import settings
from telegram import Bot
import base64
import time
from app.database import SessionLocal
from app.models.ocr_job import OCRJob

from app.services.gemini_service import gemini_service
import asyncio

@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def process_screenshot(self, job_id: str, image_bytes_b64: str, session_id: str):
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    
    # Helper to send async messages from sync Celery task
    def send_update(text):
        from app.database import SessionLocal
        from app.models.upload_session import UploadSession
        with SessionLocal() as db:
            session = db.get(UploadSession, session_id)
            if session:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.ensure_future(bot.send_message(chat_id=session.telegram_user_id, text=text))
                else:
                    loop.run_until_complete(bot.send_message(chat_id=session.telegram_user_id, text=text))

    try:
        raw_bytes = base64.b64decode(image_bytes_b64)
        processed_bytes = preprocess_image(raw_bytes)

        send_update("📂 Uploading images to Google Drive...")
        drive = DriveService(settings.GOOGLE_CREDENTIALS_PATH)
        raw_folder = drive.get_or_create_folder('Raw Screenshots')
        proc_folder = drive.get_or_create_folder('Processed Images')

        raw_id = drive.upload_bytes(raw_bytes, f'{job_id}-raw.jpg', raw_folder, mime_type='image/jpeg')
        proc_id = drive.upload_bytes(processed_bytes, f'{job_id}-processed.jpg', proc_folder, mime_type='image/jpeg')

        # Use Gemini for enhanced OCR and analysis
        send_update("🧠 AI processing started...")
        from app.models.upload_session import UploadSession
        course_info = "Unknown"
        with SessionLocal() as db:
            upload_session = db.get(UploadSession, session_id)
            if upload_session and upload_session.metadata_json:
                course = upload_session.metadata_json.get("course", "")
                level = upload_session.metadata_json.get("level", "")
                course_info = f"{course} - {level}"

        loop = asyncio.get_event_loop()
        gemini_result = loop.run_until_complete(gemini_service.analyze_attendance_image(processed_bytes, course_info))
        
        names = gemini_result.get("names", [])
        text = str(gemini_result)
        engine = "gemini-1.5-flash"
        duration_ms = 0 # In a real scenario we'd track this

        # Fallback to standard OCR if Gemini fails or returns no names
        if not names:
            ocr = OCRService()
            start = time.time()
            text, engine = ocr.extract(processed_bytes)
            duration_ms = int((time.time() - start) * 1000)
            names = ocr.normalize_names(text)

        with SessionLocal() as db:
            job = db.get(OCRJob, job_id)
            if job:
                job.raw_image_drive_id = raw_id
                job.processed_image_drive_id = proc_id
                job.raw_ocr_text = text
                job.engine = engine
                job.duration_ms = duration_ms
                job.status = 'completed'
                db.commit()

        from app.tasks.validation_tasks import validate_attendance
        validate_attendance.delay(session_id, names)

    except Exception as exc:
        raise self.retry(exc=exc)
