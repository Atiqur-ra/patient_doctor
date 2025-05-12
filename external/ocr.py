
from PIL import Image
import io
import easyocr

def extract_text_from_image(image_bytes: bytes) -> str:
    reader = easyocr.Reader(['en'])
    text = reader.readtext(image_bytes, detail=0)
    return text






