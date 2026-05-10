from google.cloud import vision
import pytesseract
from PIL import Image
import io
import os

class OCRService:
    def __init__(self):
        # The credentials should be pointed to by GOOGLE_APPLICATION_CREDENTIALS 
        # environment variable, which usually points to the same file as settings.GOOGLE_CREDENTIALS_PATH
        try:
            self.client = vision.ImageAnnotatorClient()
        except Exception:
            self.client = None

    def extract_text_vision(self, image_bytes: bytes) -> str:
        """Primary OCR using Google Cloud Vision."""
        if not self.client:
            raise RuntimeError("Vision API client not initialized")
            
        image = vision.Image(content=image_bytes)
        response = self.client.text_detection(image=image)
        if response.error.message:
            raise RuntimeError(f"Vision API error: {response.error.message}")
        
        texts = response.text_annotations
        return texts[0].description if texts else ""

    def extract_text_tesseract(self, image_bytes: bytes) -> str:
        """Fallback OCR using Tesseract."""
        img = Image.open(io.BytesIO(image_bytes))
        return pytesseract.image_to_string(img, lang='eng')

    def extract(self, image_bytes: bytes) -> tuple[str, str]:
        """Try Vision first, fall back to Tesseract. Return (text, engine)."""
        try:
            return self.extract_text_vision(image_bytes), 'google_vision'
        except Exception as e:
            # Log error if needed
            return self.extract_text_tesseract(image_bytes), 'tesseract'

    def normalize_names(self, raw_text: str) -> list[str]:
        """Parse OCR output into a clean list of candidate names."""
        lines = [line.strip() for line in raw_text.splitlines()]
        names = []
        for line in lines:
            # Skip blank lines, numbers-only lines, header patterns
            if not line or line.isdigit():
                continue
            if any(kw in line.lower() for kw in ['date', 'class', 'attendance', 'name', 'no.', 'present', 'absent']):
                continue
            names.append(line)
        return names
