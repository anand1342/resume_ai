import json
import os
import re
from openai import OpenAI
from docx import Document
import PyPDF2

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==============================
# TEXT EXTRACTION
# ==============================
def extract_text(file_path):
    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])

    elif file_path.endswith(".pdf"):
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text

    return ""


# ==============================
# IDENTITY EXTRACTION
# ==============================
def extract_identity(text):
    name = text.split("\n")[0].strip()

    email = re.search(r'[\w\.-]+@[\w\.-]+', text)
    phone = re.search(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', text)

    return {
        "name": name,
        "email": email.group(0) if email else "",
        "phone": phone.group(0) if phone else "",
    }


# ==============================
# LLM PARSER
# ==============================
PARSER_PROMPT = """
Extract ONLY factual data.

Return JSON:
{
  "education": [{"degree":"","field":"","start_year":"","end_year":""}],
  "employment": [{"company":"","role":"","start_date":"","end_date":""}]
}
"""

def parse_resume(resume_text):
    response = client.chat.completions.create(
        model="gpt-4.1",
        temperature=0,
        messages=[
            {"role": "system", "content": PARSER_PROMPT},
            {"role": "user", "content": resume_text}
        ],
    )

    try:
        return json.loads(response.choices[0].message.content)
    except:
        return {"education": [], "employment": []}
