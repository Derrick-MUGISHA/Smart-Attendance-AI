from google import genai
from google.genai import types
from app.config import settings
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            self.model_id = 'gemini-1.5-flash'
        else:
            self.client = None
            logger.warning("GEMINI_API_KEY not set. Gemini features will be unavailable.")

    async def analyze_attendance_image(self, image_bytes: bytes, course_info: str) -> Dict:
        """
        Uses Gemini to extract names and analyze attendance from an image.
        """
        if not self.client:
            return {"error": "Gemini client not initialized", "names": []}

        prompt = f"""
        Analyze this attendance screenshot for the course: {course_info}.
        
        Tasks:
        1. Extract all student names clearly visible in the list.
        2. Identify if it's a Fundamental, Frontend, or Backend class (Standard or Advanced).
        3. If there are any handwritten notes next to a name (e.g., 'sick', 'late', 'permission'), extract that as an observation.
        
        Output Requirements:
        Return ONLY a JSON object with:
        - "names": list of strings (extracted student names)
        - "observations": list of objects with "name" and "note" keys
        - "course_context": the detected course and level
        """

        try:
            # Use google-genai Client
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[
                    prompt,
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            import json
            if response.text:
                try:
                    return json.loads(response.text)
                except json.JSONDecodeError:
                    # Fallback for parsing if it's not pure JSON
                    import re
                    json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                    return {"names": [], "raw_response": response.text}
            else:
                return {"names": [], "error": "Empty response from Gemini"}

        except Exception as e:
            logger.error(f"Error analyzing image with Gemini: {e}")
            return {"error": str(e), "names": []}


    async def edit_attendance_list(self, current_list: List[Dict], user_request: str) -> Dict:
        """
        Uses Gemini to apply edits to an existing attendance list.
        """
        if not self.client:
            return {"error": "Gemini client not initialized", "attendance": current_list}

        prompt = f"""
        Current Attendance List:
        {current_list}

        User Request: {user_request}

        Apply the requested edits to the attendance list. Edits may include adding/removing students, 
        correcting spelling, or reordering.
        
        Output Requirements:
        Return ONLY a JSON object with:
        - "status": "success"
        - "message": "Brief description of changes"
        - "attendance": the updated list of attendance objects
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            import json
            if response.text:
                return json.loads(response.text)
            return {"error": "Empty response from Gemini", "attendance": current_list}
        except Exception as e:
            logger.error(f"Error editing attendance with Gemini: {e}")
            return {"error": str(e), "attendance": current_list}

gemini_service = GeminiService()
