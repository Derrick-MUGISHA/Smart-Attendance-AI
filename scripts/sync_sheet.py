import csv
import io
import httpx
from sqlalchemy.orm import Session
from app.models.student import Student
from app.models.class_ import Class
from app.models.attendance_record import AttendanceRecord
from app.models.session import AttendanceSession
from app.database import SessionLocal
import uuid
from datetime import datetime

def sync_students_from_sheet(sheet_url: str):
    """
    Downloads a Google Sheet in CSV format and syncs students to the database.
    Assumes CSV has headers like: Full Name, Phone Number, etc.
    """
    # Convert Google Sheet URL to export CSV URL
    if "/edit" in sheet_url:
        sheet_url = sheet_url.split("/edit")[0] + "/export?format=csv"
    elif "/view" in sheet_url:
        sheet_url = sheet_url.split("/view")[0] + "/export?format=csv"

    print(f"Downloading data from {sheet_url}...")
    response = httpx.get(sheet_url)
    response.raise_for_status()
    
    content = response.text
    reader = csv.DictReader(io.StringIO(content))
    
    db: Session = SessionLocal()
    try:
        # For this demo/testing, we'll create a default class if none exists
        default_class = db.query(Class).filter_by(name="Web Fundamentals").first()
        if not default_class:
            default_class = Class(
                id=uuid.uuid4(),
                name="Web Fundamentals",
                instructor_name="TBD"
            )
            db.add(default_class)
            db.commit()
            db.refresh(default_class)

        count = 0
        for row in reader:
            # The sheet provided has 'Full Name' and 'Phone Number' columns based on the image img_2.png
            # Looking at the sheet columns: NO, Full Name, Phone Number, Arrival time, Departure time, Signature
            name = row.get("Full Name")
            if not name:
                continue
                
            student_code = row.get("Phone Number", f"SN-{uuid.uuid4().hex[:6]}")
            
            # Check if a student exists
            student = db.query(Student).filter_by(student_code=student_code).first()
            if not student:
                student = Student(
                    name=name,
                    student_code=student_code,
                    class_id=default_class.id
                )
                db.add(student)
                count += 1
        
        db.commit()
        print(f"Successfully synced {count} new students.")
    except Exception as e:
        db.rollback()
        print(f"Error syncing students: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1FuWMKK9MSWrrMPDkyAsVV_nPhJT3ktWz5sy7FaM4C8Y/edit?usp=sharing"
    sync_students_from_sheet(SHEET_URL)

def write_attendance_to_sheet(session_id: str, credentials_path: str, sheet_id: str):
    """
    Writes attendance records to the Google Sheet.
    Requires 'google-api-python-client' and 'google-auth'.
    """
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = service_account.Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    
    db: Session = SessionLocal()
    try:
        records = db.query(AttendanceRecord).filter_by(session_id=session_id).all()
        session = db.query(AttendanceSession).filter_by(id=session_id).first()
        
        # Prepare data for sheets
        # Row format: [Student Name, Status, Absence Reason, Confidence, Timestamp]
        values = []
        for r in records:
            status = "Present" if not r.is_absent else "Absent"
            values.append([
                r.matched_name or r.ocr_raw_name,
                status,
                r.absence_reason or "",
                f"{r.confidence_score*100:.1f}%" if r.confidence_score else "",
                session.date.isoformat() if session else datetime.now().date().isoformat()
            ])
            
        # Append to the sheet
        body = {'values': values}
        range_name = 'Sheet1!A2' # Adjust based on sheet structure
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"Successfully wrote {len(values)} records to Google Sheet.")
    finally:
        db.close()
