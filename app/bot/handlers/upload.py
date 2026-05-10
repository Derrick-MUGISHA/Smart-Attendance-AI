import os
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes
import logging

from app.services.file_manager import file_manager
from app.config import settings
from app.database import SessionLocal
import datetime
from app.models.telegram_user import TelegramUser
from app.models.upload_session import UploadSession
from app.tasks.ocr_tasks import process_screenshot
import base64

logger = logging.getLogger(__name__)

async def handle_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return

    # Check whitelist if configured
    if settings.ENABLE_WHITELIST and settings.TELEGRAM_ADMIN_IDS and user.id not in settings.TELEGRAM_ADMIN_IDS:
        logger.warning(f"Unauthorized upload attempt by user {user.id} (@{user.username})")
        await update.message.reply_text(
            f"You are not authorized to upload files. Your Telegram ID is {user.id}.\n"
            "Please contact the administrator to be whitelisted."
        )
        return

    message = update.message
    file_obj = None
    filename = "file"

    if message.photo:
        file_obj = await message.photo[-1].get_file()
        filename = f"image_{file_obj.file_unique_id}.jpg"
    elif message.document:
        file_obj = await message.document.get_file()
        filename = message.document.file_name
    elif message.pdf: # Custom check if library supports it directly or via document
        file_obj = await message.pdf.get_file()
        filename = message.pdf.file_name

    if not file_obj:
        await update.message.reply_text("Unsupported file type. Please send a photo or document.")
        return

    # Basic extension validation
    ext = Path(filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        await update.message.reply_text(f"File type {ext} not allowed. Supported: {', '.join(settings.ALLOWED_EXTENSIONS)}")
        return

    try:
        # Download file into memory first to avoid large temp files if possible, 
        # or use a bytearray. Here we use a bytearray for the file_manager
        file_bytearray = await file_obj.download_as_bytearray()
        
        # Immediate confirmation
        metadata_date = datetime.datetime.now().strftime("%Y-%m-%d")
        await update.message.reply_text(
            f"✅ File received successfully\n"
            f"Original: {filename}\n"
            f"Folder: /Attendance/{metadata_date}/"
        )
        
        # Save using file manager
        metadata = await file_manager.save_upload(
            content=bytes(file_bytearray),
            original_filename=filename,
            sender_id=user.id
        )

        await update.message.reply_text("🚀 Processing started using OCR + AI...")

        # Create or update upload session with metadata from context
        course = context.user_data.get("course")
        level = context.user_data.get("level")

        with SessionLocal() as db:
            # For simplicity, create a new session per file if we want to process immediately
            # or link to an existing active session for the user
            session_metadata = {"course": course, "level": level}
            db_session = UploadSession(
                telegram_user_id=user.id,
                folder_path=str(Path(metadata['path']).parent),
                file_count=1,
                status="completed",
                metadata_json=session_metadata
            )
            db.add(db_session)
            db.commit()
            db.refresh(db_session)
            
            # Trigger OCR task
            image_b64 = base64.b64encode(bytes(file_bytearray)).decode('utf-8')
            process_screenshot.delay(
                job_id=str(db_session.id), # Reusing session id as job id for now or create OCRJob
                image_bytes_b64=image_b64,
                session_id=str(db_session.id)
            )

        await message.reply_text(
            f"✅ File received and organized!\n\n"
            f"Original: {metadata['original_filename']}\n"
            f"Saved as: {metadata['filename']}\n"
            f"Folder: {Path(metadata['path']).parent.name}\n"
            f"Status: {metadata['status']}"
        )
        
        logger.info(f"User {user.id} uploaded {filename} -> {metadata['path']}")

    except Exception as e:
        logger.error(f"Error handling upload: {e}")
        await message.reply_text(f"❌ Failed to process upload: {str(e)}")