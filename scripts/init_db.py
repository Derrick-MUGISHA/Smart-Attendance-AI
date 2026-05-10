from app.database import engine, Base
from app.models.student import Student
from app.models.class_ import Class
from app.models.attendance_record import AttendanceRecord
from app.models.session import AttendanceSession
from app.models.ocr_job import OCRJob
from app.models.telegram_user import TelegramUser
from app.models.upload_session import UploadSession

def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    init_db()
