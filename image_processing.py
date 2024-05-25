from PIL import Image
import pytesseract

def read_text_from_image(image, lang):
    try:
        pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'  # Replace with your Tesseract installation path
        text = pytesseract.image_to_string(image, lang=lang)
        return text
    except Exception as e:
        return f"Error: {e}"