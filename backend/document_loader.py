from pathlib import Path

from pypdf import PdfReader
from docx import Document

import fitz  # PyMuPDF
import pytesseract
from PIL import Image


# ============================================================
# TESSERACT CONFIGURATION
# ============================================================

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# ============================================================
# TEXT FILE
# ============================================================

def load_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# ============================================================
# MARKDOWN FILE
# ============================================================

def load_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# ============================================================
# DOCX FILE
# ============================================================

def load_docx(file_path):
    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)


# ============================================================
# OCR IMAGE
# ============================================================

def ocr_image(file_path):
    """
    Extract text from PNG/JPG/JPEG images using Tesseract OCR.
    """

    image = Image.open(file_path)

    text = pytesseract.image_to_string(image)

    return text


# ============================================================
# OCR PDF PAGE
# ============================================================

def ocr_pdf_page(page):
    """
    Convert a PDF page into an image and run OCR on it.
    """

    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

    image = Image.frombytes(
        "RGB",
        [pix.width, pix.height],
        pix.samples
    )

    text = pytesseract.image_to_string(image)

    return text


# ============================================================
# PDF FILE
# ============================================================

def load_pdf(file_path):
    """
    Load a PDF.

    First tries normal PDF text extraction.

    If a page contains little/no text,
    OCR is automatically used for that page.
    """

    pdf = fitz.open(file_path)

    pages = []

    for page_number, page in enumerate(pdf):

        # Try normal text extraction first
        text = page.get_text("text").strip()

        # If enough text exists, use it
        if len(text) >= 20:

            pages.append(text)

        # Otherwise, treat the page as scanned/image-based
        else:

            print(
                f"OCR required for PDF page {page_number + 1}"
            )

            ocr_text = ocr_pdf_page(page)

            pages.append(ocr_text)

    pdf.close()

    return "\n".join(pages)


# ============================================================
# MAIN DOCUMENT LOADER
# ============================================================

def load_document(file_path):

    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":

        return load_pdf(file_path)

    elif extension == ".docx":

        return load_docx(file_path)

    elif extension == ".txt":

        return load_txt(file_path)

    elif extension == ".md":

        return load_markdown(file_path)

    elif extension in [".png", ".jpg", ".jpeg"]:

        return ocr_image(file_path)

    else:

        raise ValueError(
            f"Unsupported file type: {extension}"
        )