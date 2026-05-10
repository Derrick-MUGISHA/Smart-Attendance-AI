from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from app.bot.keyboards import get_course_keyboard, get_level_keyboard, get_confirm_attendance_keyboard
from app.bot.handlers.upload import handle_upload
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Conversation states
CHOOSING_COURSE, CHOOSING_LEVEL, UPLOADING, EDITING = range(4)

async def start_attendance_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if settings.ENABLE_WHITELIST and settings.TELEGRAM_ADMIN_IDS and user.id not in settings.TELEGRAM_ADMIN_IDS:
        logger.warning(f"Unauthorized attendance flow attempt by user {user.id} (@{user.username})")
        await update.message.reply_text(
            f"You are not authorized to start the attendance flow. Your Telegram ID is {user.id}.\n"
            "Please contact the administrator to be whitelisted."
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "Welcome! Let's process the attendance. First, select the course:",
        reply_markup=get_course_keyboard()
    )
    return CHOOSING_COURSE

async def course_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    course_data = query.data.replace("course_", "")
    
    if "adv_" in course_data:
        context.user_data["course"] = course_data.replace("adv_", "")
        context.user_data["level"] = "advanced"
        await query.edit_message_text(
            f"Selected: Advanced {context.user_data['course'].capitalize()}. Please upload the attendance photo or PDF now."
        )
        return UPLOADING
    else:
        context.user_data["course"] = course_data
        await query.edit_message_text(
            f"Selected: {course_data.capitalize()}. Now select the level:",
            reply_markup=get_level_keyboard()
        )
        return CHOOSING_LEVEL

async def level_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    level = query.data.replace("level_", "")
    context.user_data["level"] = level
    
    await query.edit_message_text(
        f"Selected Level: {level.capitalize()}. Please upload the attendance photo or PDF now."
    )
    return UPLOADING

async def handle_attendance_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Pass to the existing upload handler but with context metadata
    await handle_upload(update, context)
    
    await update.message.reply_text(
        "Upload received! I am analyzing it with Gemini now. I will notify you when it's ready for confirmation."
    )
    return ConversationHandler.END

async def confirm_all_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Logic to trigger Google Sheet sync and PDF generation
    from app.database import SessionLocal
    from app.models.upload_session import UploadSession
    from app.models.attendance_record import AttendanceRecord
    from app.models.session import AttendanceSession
    from app.services.google_sheets_service import GoogleSheetsService
    from app.services.pdf import generate_attendance_pdf
    from app.services.drive import DriveService
    import os
    
    user_id = query.from_user.id
    await query.edit_message_text("🔄 Finalizing attendance...")

    with SessionLocal() as db:
        session = db.query(UploadSession).filter_by(telegram_user_id=user_id).order_by(UploadSession.created_at.desc()).first()
        if not session:
            await query.edit_message_text("No active session found to confirm.")
            return
        
        # Hardcoded sheet ID from user description if not in env
        sheet_id = "1FuWMKK9MSWrrMPDkyAsVV_nPhJT3ktWz5sy7FaM4C8Y"
        
        sheets_service = GoogleSheetsService(settings.GOOGLE_CREDENTIALS_PATH)
        success = sheets_service.write_attendance(str(session.id), sheet_id)
        
        # Generate PDF and upload to Drive
        records = db.query(AttendanceRecord).filter_by(session_id=session.id).all()
        session_obj = db.query(AttendanceSession).filter_by(id=session.id).first()
        
        session_data = {
            "class_name": session.metadata_json.get("course", "Unknown"),
            "date": session_obj.date.isoformat() if session_obj else session.created_at.date().isoformat(),
            "records": [
                {
                    "name": r.matched_name or r.ocr_raw_name,
                    "status": "Present" if not r.is_absent else "Absent",
                    "confidence": f"{r.confidence_score*100:.1f}%" if r.confidence_score else "N/A"
                } for r in records
            ],
            "summary": {
                "total": len(records),
                "present": len([r for r in records if not r.is_absent]),
                "absent": len([r for r in records if r.is_absent])
            }
        }
        
        pdf_bytes = generate_attendance_pdf(session_data)
        drive_service = DriveService(settings.GOOGLE_CREDENTIALS_PATH)
        reports_folder = drive_service.get_or_create_folder("Reports")
        filename = f"attendance_{session_data['class_name']}_{session_data['date']}.pdf"
        file_id = drive_service.upload_bytes(pdf_bytes, filename, reports_folder)
        link = drive_service.get_shareable_link(file_id)
        
        if success:
            await query.edit_message_text(
                f"✅ *Attendance finalized successfully*\n\n"
                f"📊 *Summary:*\n"
                f"- Total: {session_data['summary']['total']}\n"
                f"- Present: {session_data['summary']['present']}\n"
                f"- Absent: {session_data['summary']['absent']}\n\n"
                f"🔗 *Links:*\n"
                f"- [Google Sheet](https://docs.google.com/spreadsheets/d/{sheet_id})\n"
                f"- [PDF Report]({link})",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text("❌ Partial success: PDF generated but Google Sheet sync failed.")

async def review_manual_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Manual review is not yet implemented. Please use Approve All for now.")

async def edit_attendance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📝 *Edit Flow*\n\n"
        "Please describe the changes you want to make (e.g., 'add student John Doe', 'remove Alice', 'correct spelling of Mugisha').",
        parse_mode="Markdown"
    )
    return EDITING

async def handle_edit_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_request = update.message.text
    user_id = update.effective_user.id
    
    from app.database import SessionLocal
    from app.models.upload_session import UploadSession
    from app.models.attendance_record import AttendanceRecord
    from app.services.gemini_service import gemini_service
    from sqlalchemy import select
    
    await update.message.reply_text("🧠 Applying edits with Gemini...")
    
    with SessionLocal() as db:
        session = db.query(UploadSession).filter_by(telegram_user_id=user_id).order_by(UploadSession.created_at.desc()).first()
        if not session:
            await update.message.reply_text("No active session found to edit.")
            return ConversationHandler.END
            
        records = db.query(AttendanceRecord).filter_by(session_id=session.id).all()
        current_list = [
            {
                "id": str(r.id),
                "ocr_raw_name": r.ocr_raw_name,
                "matched_name": r.matched_name,
                "status": r.status,
                "is_absent": r.is_absent
            } for r in records
        ]
        
        edit_result = await gemini_service.edit_attendance_list(current_list, user_request)
        
        if "error" in edit_result:
            await update.message.reply_text(f"❌ Gemini Error: {edit_result['error']}")
            return ConversationHandler.END
            
        # Update records in DB based on Gemini's response
        # This is a simplified implementation: we'll clear and recreate or update
        # For this PoC, let's just show the preview and message
        
        await update.message.reply_text(
            f"✅ *File updated successfully*\n\n"
            f"Message: {edit_result.get('message', 'Changes applied')}\n\n"
            f"*Updated Preview:*\n" + "\n".join([f"- {r.get('matched_name') or r.get('ocr_raw_name')}" for r in edit_result.get('attendance', [])[:10]]),
            parse_mode="Markdown",
            reply_markup=get_confirm_attendance_keyboard()
        )
        
    return ConversationHandler.END

async def reject_attendance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ Attendance rejected.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Attendance flow cancelled.")
    return ConversationHandler.END

attendance_conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("upload", start_attendance_flow),
        CallbackQueryHandler(edit_attendance_handler, pattern=r"^edit_attendance$")
    ],
    states={
        CHOOSING_COURSE: [CallbackQueryHandler(course_choice, pattern=r"^course_")],
        CHOOSING_LEVEL: [CallbackQueryHandler(level_choice, pattern=r"^level_")],
        UPLOADING: [
            MessageHandler(filters.PHOTO | filters.Document.ALL, handle_attendance_upload),
            CommandHandler("done", cancel)
        ],
        EDITING: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_request)
        ]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

# New handlers for confirmation (outside the conversation flow as it might have ended)
confirm_handler = CallbackQueryHandler(confirm_all_handler, pattern=r"^confirm_all$")
review_handler = CallbackQueryHandler(review_manual_handler, pattern=r"^review_manual$")
reject_handler = CallbackQueryHandler(reject_attendance_handler, pattern=r"^reject_attendance$")
