from pypdf import PdfReader
from pathlib import Path
from docx import Document

def load_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    return text


def load_pdf(file_path):
    reader = PdfReader(file_path)
    pages = []

    for page in reader.pages:
        text = page.extract_text()
        pages.append(text)
    return "\n".join(pages)

def load_docx(file_path):
    document = Document(file_path)
    paragraphs = []
    
    for paragraph in document.paragraphs:
        text = paragraph.text
        paragraphs.append(text)
    return "\n".join(paragraphs)


def load_document(file_path):
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return load_pdf(file_path)
    elif extension ==".docx":
        return load_docx(file_path)
    elif extension ==".txt":
        return load_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {extension}")