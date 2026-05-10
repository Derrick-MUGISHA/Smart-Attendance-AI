import logging
from sqlalchemy.orm import Session
from googleapiclient.discovery import build
from google.oauth2 import service_account
from app.models.attendance_record import AttendanceRecord
from app.models.session import AttendanceSession
from app.database import SessionLocal
from datetime import datetime

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class GoogleSheetsService:
    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.creds = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=SCOPES
        )
        self.service = build('sheets', 'v4', credentials=self.creds)

    def write_attendance(self, session_id: str, sheet_id: str):
        """
        Writes attendance records to the Google Sheet.
        """
        with SessionLocal() as db:
            records = db.query(AttendanceRecord).filter_by(session_id=session_id).all()
            session = db.query(AttendanceSession).filter_by(id=session_id).first()
            
            if not session:
                logger.error(f"Session {session_id} not found")
                return

            # Prepare data for sheets
            # We follow the structure suggested in sync_sheet.py or standard attendance
            # NO, Full Name, Status, Absence Reason, Confidence, Date
            values = []
            for i, r in enumerate(records, 1):
                status = "Present" if not r.is_absent else "Absent"
                values.append([
                    i,
                    r.matched_name or r.ocr_raw_name,
                    status,
                    r.absence_reason or "",
                    f"{r.confidence_score*100:.1f}%" if r.confidence_score else "",
                    session.date.isoformat()
                ])
                
            if not values:
                logger.warning(f"No records found for session {session_id}")
                return

            # Append to the sheet
            body = {'values': values}
            range_name = 'Sheet1!A2' # Default range
            
            try:
                self.service.spreadsheets().values().append(
                    spreadsheetId=sheet_id,
                    range=range_name,
                    valueInputOption='RAW',
                    body=body
                ).execute()
                logger.info(f"Successfully wrote {len(values)} records to Google Sheet {sheet_id}")
                return True
            except Exception as e:
                logger.error(f"Error writing to Google Sheet: {e}")
                return False

    def sync_from_sheet(self, sheet_id: str):
        """
        Reads students from sheet and updates DB.
        """
        # Implementation similar to sync_students_from_sheet in scripts/sync_sheet.py
        # but using the Sheets API instead of CSV export if needed for real-time.
        pass
