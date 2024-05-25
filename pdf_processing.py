import PyPDF2
import io
import pdf2image
import pytesseract
from pdf2image import convert_from_bytes

def read_text_from_pdf(uploaded_file, chunk_size=10):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    total_pages = len(pdf_reader.pages)
    text = ""
    for i in range(0, total_pages, chunk_size):
        end_page = min(i + chunk_size, total_pages)
        for page_number in range(i, end_page):
            page = pdf_reader.pages[page_number]
            try:
                text += page.extract_text()
            except PyPDF2.utils.PdfReadError as e:
                # This error may occur if the page contains an image
                if "Image" in str(e):
                    # Convert the PDF page to an image and use OCR to extract text
                    images = convert_from_bytes(page.contents, dpi=300)
                    for image in images:
                        text += pytesseract.image_to_string(image)
                else:
                    raise e
    return text