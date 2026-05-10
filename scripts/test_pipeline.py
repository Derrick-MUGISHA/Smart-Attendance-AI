import os
from app.services.preprocessing import preprocess_image
from app.services.ocr import OCRService
from app.services.matching import match_all
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.student import Student

def test_pipeline(image_path: str):
    print(f"--- Testing Pipeline for {image_path} ---")
    if not os.path.exists(image_path):
        print(f"Error: Image {image_path} not found.")
        return

    # 1. Preprocessing
    with open(image_path, "rb") as f:
        raw_bytes = f.read()
    
    print("Preprocessing image...")
    processed_bytes = preprocess_image(raw_bytes)
    
    # 2. OCR (Will attempt Vision then Tesseract)
    print("Extracting text via OCR...")
    ocr_service = OCRService()
    try:
        text, engine = ocr_service.extract(processed_bytes)
        print(f"OCR Engine used: {engine}")
        print("Raw text extracted:")
        print(text[:200] + "..." if len(text) > 200 else text)
        
        names = ocr_service.normalize_names(text)
        print(f"Found {len(names)} candidate names.")
    except Exception as e:
        print(f"OCR Failed: {e}")
        return

    # 3. Matching
    db: Session = SessionLocal()
    try:
        students = db.query(Student).all()
        student_names = [s.name for s in students]
        print(f"Matching against {len(student_names)} students in database...")
        
        results = match_all(names, student_names)
        
        print("\nMatching Results (Top 10):")
        for res in results[:10]:
            print(f"OCR: {res['ocr_raw']:20} -> Match: {res['matched']:20} (Score: {res['score']}, Status: {res['status']})")
            
    finally:
        db.close()

if __name__ == "__main__":
    # Test with one of the provided images
    test_pipeline("images/img_2.png")
