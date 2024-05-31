import PyPDF2

import pytesseract
from pdf2image import convert_from_bytes
import logging
from concurrent.futures import ThreadPoolExecutor

def read_text_from_pdf(uploaded_file, chunk_size=10, num_workers=4):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    total_pages = len(pdf_reader.pages)
    text = ""

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for i in range(0, total_pages, chunk_size):
            end_page = min(i + chunk_size, total_pages)
            futures.append(executor.submit(process_chunk, pdf_reader, i, end_page))

        for future in futures:
            try:
                text += future.result()
            except Exception as e:
                logging.error(f"Error while processing chunk: {e}")

    return text

def process_chunk(pdf_reader, start_page, end_page):
    chunk_text = ""
    for page_number in range(start_page, end_page):
        page = pdf_reader.pages[page_number]
        try:
            chunk_text += page.extract_text()
        except PyPDF2.utils.PdfReadError as e:
            if "Image" in str(e):
                images = convert_from_bytes(page.contents, dpi=300)
                for image in images:
                    chunk_text += pytesseract.image_to_string(image)
            else:
                logging.error(f"Error while processing page {page_number}: {e}")

    return chunk_text