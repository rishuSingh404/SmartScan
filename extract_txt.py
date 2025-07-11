import PyPDF2  # type: ignore
from docx import Document  # type: ignore

def extract_text_from_pdf(file) -> str:
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        return f"[PDF extraction error: {e}]"

def extract_text_from_docx(file) -> str:
    try:
        doc = Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        return f"[DOCX extraction error: {e}]" 