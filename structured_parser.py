import os

# ==============================
# SAFE TEXT EXTRACTION
# ==============================

def extract_text(file_path: str) -> str:
    """
    Extract clean text from PDF, DOCX, or TXT files.
    Prevents binary garbage like 'PK' from appearing.
    """

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_pdf_text(file_path)

    elif ext == ".docx":
        return extract_docx_text(file_path)

    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    else:
        raise ValueError("Unsupported file format. Upload PDF, DOCX, or TXT.")


# ==============================
# PDF PARSER
# ==============================
def extract_pdf_text(file_path):
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        raise ImportError("PyPDF2 not installed. Add it to requirements.txt")

    reader = PdfReader(file_path)
    text = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)

    return "\n".join(text)


# ==============================
# DOCX PARSER
# ==============================
def extract_docx_text(file_path):
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx not installed. Add it to requirements.txt")

    doc = Document(file_path)
    text = []

    for para in doc.paragraphs:
        if para.text.strip():
            text.append(para.text)

    return "\n".join(text)
