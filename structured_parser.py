import pdfplumber
from docx import Document
import os


def extract_text(file_path: str) -> str:
    """
    Extract clean text from PDF, DOCX, or TXT files.
    Prevents binary corruption like 'PK'.
    """

    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == ".pdf":
            return extract_pdf_text(file_path)

        elif ext == ".docx":
            return extract_docx_text(file_path)

        elif ext == ".txt":
            return open(file_path, "r", encoding="utf-8", errors="ignore").read()

        else:
            return ""

    except Exception as e:
        print("❌ Text extraction failed:", e)
        return ""


# ==============================
# PDF Extraction
# ==============================
def extract_pdf_text(file_path: str) -> str:
    text = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text.append(content)
    return "\n".join(text)


# ==============================
# DOCX Extraction
# ==============================
def extract_docx_text(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs if p.text])
