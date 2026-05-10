from typing import List, Dict
import logging
from app.models.attendance_record import AttendanceRecord
from app.models.student import Student

logger = logging.getLogger(__name__)

class ValidationService:
    def __init__(self):
        pass

    def validate_attendance(self, matched_records: List[Dict]) -> List[Dict]:
        """
        Final validation of attendance records.
        Checks for duplicates within the same session and potential inconsistencies.
        """
        validated_records = []
        seen_student_ids = set()

        for record in matched_records:
            student_id = record.get('student_id')
            
            if student_id:
                if student_id in seen_student_ids:
                    record['status'] = 'duplicate'
                    logger.warning(f"Duplicate student detected in session: {student_id}")
                else:
                    seen_student_ids.add(student_id)
            
            validated_records.append(record)
            
        return validated_records

validation_service = ValidationService()
