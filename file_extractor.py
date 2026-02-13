import os

def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_pdf(file_path)
    elif ext == ".docx":
        return extract_docx(file_path)
    elif ext == ".txt":
        return open(file_path, "r", errors="ignore").read()
    else:
        return ""


def extract_pdf(file_path):
    import pdfplumber
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def extract_docx(file_path):
    from docx import Document
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])
