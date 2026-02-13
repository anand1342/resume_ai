import re
from docx import Document
import pdfplumber


# ===============================
# FILE TEXT EXTRACTION
# ===============================

def extract_text(file_path: str) -> str:
    """
    Extract clean text from PDF, DOCX, or TXT.
    Prevents binary garbage like PK headers.
    """

    if file_path.lower().endswith(".pdf"):
        return extract_pdf_text(file_path)

    if file_path.lower().endswith(".docx"):
        return extract_docx_text(file_path)

    if file_path.lower().endswith(".txt"):
        with open(file_path, "r", errors="ignore") as f:
            return f.read()

    return ""


def extract_pdf_text(file_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except:
        pass
    return clean_text(text)


def extract_docx_text(file_path: str) -> str:
    text = ""
    try:
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except:
        pass
    return clean_text(text)


# ===============================
# CLEAN TEXT
# ===============================

def clean_text(text: str) -> str:
    """
    Remove binary artifacts & normalize.
    """
    if not text:
        return ""

    # Remove non-printable characters
    text = re.sub(r"[^\x20-\x7E\n]", "", text)

    # Normalize spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()
