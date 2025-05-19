
import os
import io
import json
from PIL import Image
import google.generativeai as genai

GOOGLE_API_KEY = os.getenv("GEMNI_API")
if not GOOGLE_API_KEY:
    raise EnvironmentError("GEMNI_API environment variable not set.")
genai.configure(api_key=GOOGLE_API_KEY)


MODEL_NAME = "gemini-2.5-flash-preview-04-17"

def load_image(image_path: str) -> Image.Image:
    """Loads an image from file."""
    with open(image_path, "rb") as f:
        return Image.open(io.BytesIO(f.read()))

def get_prescription_prompt() -> str:
    """Returns the prompt for extracting structured prescription data."""
    return """
    Extract the following information from the medical prescription:
    - Patient Name
    - Doctor's Name
    - Birthdate
    - Age
    - Medications (including name, dosage, route, frequency, and duration if available)
    - Any special instructions

    Format your response in JSON:
    {
      "patient_name": "...",
      "doctor_name": "...",
      "Birthdate": "...",
      "age": "...",
      "medications": [
        {
          "name": "...",
          "dosage": "...",
          "route": "...",
          "frequency": "...",
          "duration": "..."
        }
      ],
      "instructions": "..."
    }

    If any value is missing, return "N/A".
    Only return valid JSON.
    """

def query_gemini_with_image(image: Image.Image, prompt: str) -> str:
    """Queries Gemini with a prompt and image, returns raw text response."""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content([prompt, image])
        response.resolve()
        return response.text
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return None

def extract_structured_prescription_info(image_path: str) -> dict:
    """Extracts structured prescription info from an image."""
    image = load_image(image_path)
    prompt = get_prescription_prompt()
    result_text = query_gemini_with_image(image, prompt)

    if result_text:
        cleaned_text = result_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text.replace("```json", "").strip()
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3].strip()

        try:
            parsed = json.loads(cleaned_text)
            return parsed
        except json.JSONDecodeError:
            return {"error": "json_decode_error", "raw_text": result_text}
    return {"error": "gemini_failed", "message": "No response from Gemini."}


def prepare_for_db(data: dict) -> dict:
    """Transforms extracted data to be ready for DB storage."""
    return {
        "patient_name": data.get("patient_name", None),
        "doctor_name": data.get("doctor_name", None),
        "date_of_birth": data.get("Birthdate", None),
        "age": data.get("age", None),
        "instructions": data.get("instructions", None),
        "medications": [
            {
                "name": med.get("name", None),
                "dosage": med.get("dosage", None),
                "route": med.get("route", None),
                "frequency": med.get("frequency", None),
                "duration": med.get("duration", None)
            }
            for med in data.get("medications", [])
        ]
    }

