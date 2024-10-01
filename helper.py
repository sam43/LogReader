from PyPDF2 import PdfReader
from docx import Document

def load_log_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.readlines()
    except Exception as e:
        return [f"Error loading file: {str(e)}"]


def load_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.readlines()
    except Exception as e:
        return [f"Error loading file: {str(e)}"]


def load_pdf_file(file_path):
    try:
        pdf_reader = PdfReader(file_path)
        pages_content = []
        for page in pdf_reader.pages:
            pages_content.append(page.extract_text())
        return "\n".join(pages_content).splitlines()
    except Exception as e:
        return [f"Error loading PDF file: {str(e)}"]


def load_word_file(file_path):
    try:
        doc = Document(file_path)
        return [para.text for para in doc.paragraphs if para.text.strip() != ""]
    except Exception as e:
        return [f"Error loading Word file: {str(e)}"]