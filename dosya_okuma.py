import os
from pypdf import PdfReader
from docx import Document


def read_txt(file_path):
    """Read a UTF-8 text file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def read_pdf(file_path):
    """Extract text from all pages of a PDF file."""
    reader = PdfReader(file_path)
    full_text = ""

    for page in reader.pages:
        page_text = page.extract_text() or ""
        full_text += page_text + "\n"

    return full_text


def read_docx(file_path):
    """Extract paragraph text from a DOCX file."""
    document = Document(file_path)
    full_text = ""

    for paragraph in document.paragraphs:
        full_text += paragraph.text + "\n"

    return full_text


def read_document(file_path):
    """Read a supported document based on its file extension."""
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".txt":
        return read_txt(file_path)

    if extension == ".pdf":
        return read_pdf(file_path)

    if extension == ".docx":
        return read_docx(file_path)

    raise ValueError(f"Unsupported file type: {extension}")
