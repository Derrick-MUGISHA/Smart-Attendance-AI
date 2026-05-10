from telegram import Update
from telegram.ext import ContextTypes
from app.config import settings

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"Hi {user.first_name}! 🎓 (ID: {user.id})\n\n"
        "Welcome to the Smart Attendance Bot. Send me a photo of your attendance list, "
        "and I'll handle the rest.\n\n"
        "Available commands:\n"
        "/start - Start the bot\n"
        "/upload - Start attendance upload flow\n"
        "/help - Show this help message\n"
        "/status - Check system status\n"
        "/today - View today's attendance\n"
        "/process - Trigger processing of latest uploads\n"
        "/rename <old> <new> - Rename a file\n"
        "/delete <file> - Remove an upload\n"
        "/move <file> <folder> - Move a file to a folder"
    )
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 *Help Guide*\n\n"
        "1. Send a clear photo or PDF of the attendance sheet.\n"
        "2. The system will automatically organize it by date.\n"
        "3. Use /status to check if the AI is processing.\n"
        "4. Use /today to see the extracted results."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # In a real app, query the database/celery
    status_text = (
        "✅ *System Status*\n\n"
        "Backend: Online\n"
        "Database: Connected\n"
        "Workers: 3 Active\n"
        "Pending Jobs: 0"
    )
    await update.message.reply_text(status_text, parse_mode="Markdown")

async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fetching today's attendance summary...")
    # Logic to fetch from DB

async def process_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Starting AI processing for latest uploads...")
    # Trigger Celery task

async def rename_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Usage: /rename <old_filename> <new_name>")
        return
    
    old_name = context.args[0]
    new_name = context.args[1]
    
    await update.message.reply_text(f"Renaming {old_name} to {new_name} in Google Drive... Please wait.")
    
    from app.services.drive import DriveService
    try:
        drive_service = DriveService(settings.GOOGLE_CREDENTIALS_PATH)
        # Search for file by name
        results = drive_service.service.files().list(
            q=f"name = '{old_name}' and trashed = false",
            fields="files(id, name)"
        ).execute()
        files = results.get('files', [])
        
        if not files:
            await update.message.reply_text(f"❌ File '{old_name}' not found in Google Drive.")
            return
            
        file_id = files[0]['id']
        drive_service.service.files().update(
            fileId=file_id,
            body={'name': new_name}
        ).execute()
        
        await update.message.reply_text(f"✅ File renamed successfully to '{new_name}'.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error renaming file: {str(e)}")

async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /delete <filename>")
        return
        
    filename = context.args[0]
    await update.message.reply_text(f"Deleting file '{filename}' from Google Drive...")
    
    from app.services.drive import DriveService
    try:
        drive_service = DriveService(settings.GOOGLE_CREDENTIALS_PATH)
        results = drive_service.service.files().list(
            q=f"name = '{filename}' and trashed = false",
            fields="files(id, name)"
        ).execute()
        files = results.get('files', [])
        
        if not files:
            await update.message.reply_text(f"❌ File '{filename}' not found.")
            return
            
        file_id = files[0]['id']
        drive_service.service.files().update(
            fileId=file_id,
            body={'trashed': True}
        ).execute()
        
        await update.message.reply_text(f"✅ File '{filename}' moved to trash.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error deleting file: {str(e)}")

async def move_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Usage: /move <filename> <folder_name>")
        return
        
    filename = context.args[0]
    folder_name = context.args[1]
    
    await update.message.reply_text(f"Moving '{filename}' to '{folder_name}'...")
    
    from app.services.drive import DriveService
    try:
        drive_service = DriveService(settings.GOOGLE_CREDENTIALS_PATH)
        
        # Find file
        file_results = drive_service.service.files().list(
            q=f"name = '{filename}' and trashed = false",
            fields="files(id, parents)"
        ).execute()
        files = file_results.get('files', [])
        
        if not files:
            await update.message.reply_text(f"❌ File '{filename}' not found.")
            return
            
        file_id = files[0]['id']
        previous_parents = ",".join(files[0].get('parents', []))
        
        # Find or create folder
        folder_id = drive_service.get_or_create_folder(folder_name)
        
        # Move file
        drive_service.service.files().update(
            fileId=file_id,
            addParents=folder_id,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()
        
        await update.message.reply_text(f"✅ File '{filename}' moved to '{folder_name}'.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error moving file: {str(e)}")
