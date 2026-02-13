import os
import re
import json
from openai import OpenAI
from docx import Document
from PyPDF2 import PdfReader

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==============================
# FILE TEXT EXTRACTION
# ==============================
def extract_text(file_path):
    ext = file_path.lower().split(".")[-1]

    if ext == "pdf":
        reader = PdfReader(file_path)
        return "\n".join([page.extract_text() or "" for page in reader.pages])

    elif ext in ["docx", "doc"]:
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])

    elif ext == "txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    else:
        raise ValueError("Unsupported file format")


# ==============================
# IDENTITY EXTRACTION (REGEX)
# ==============================
def extract_identity(text):
    email = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phone = re.findall(r"\+?\d[\d\s\-]{8,}\d", text)
    linkedin = re.findall(r"linkedin\.com/in/[A-Za-z0-9\-_/]+", text, re.I)
    github = re.findall(r"github\.com/[A-Za-z0-9\-_/]+", text, re.I)

    lines = text.split("\n")
    name = lines[0].strip() if lines else ""

    return {
        "name": name,
        "email": email[0] if email else "",
        "phone": phone[0] if phone else "",
        "location": "",  # optional enhancement later
        "linkedin": linkedin[0] if linkedin else "",
        "github": github[0] if github else "",
    }


# ==============================
# SKILLS EXTRACTION (SAFE)
# ==============================
def extract_skills(text):
    keywords = [
        "python", "java", "c++", "c#", "sql", "mysql", "postgresql",
        "aws", "azure", "docker", "kubernetes", "pandas", "numpy",
        "spark", "hadoop", "airflow", "react", "node", "django",
        "flask", "tableau", "power bi", "excel", "git", "linux",
        "tensorflow", "pytorch", "etl", "rest api", "microservices",
        "spring", "spring boot", "angular", "vue", "mongodb"
    ]

    found = set()
    lower = text.lower()

    for skill in keywords:
        if skill in lower:
            found.add(skill)

    return sorted(list(found))


# ==============================
# OPENAI STRUCTURED PARSING
# ==============================
PARSER_PROMPT = """
Extract ONLY factual information from resume.

Return STRICT JSON:

{
  "education": [
    {
      "degree": "",
      "field": "",
      "start_year": "",
      "end_year": ""
    }
  ],
  "employment": [
    {
      "company": "",
      "role": "",
      "start_date": "",
      "end_date": ""
    }
  ]
}

Rules:
- No guessing
- No commentary
- JSON only
"""

def extract_structured_sections(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            temperature=0,
            messages=[
                {"role": "system", "content": PARSER_PROMPT},
                {"role": "user", "content": text}
            ],
        )

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        print("❌ Structured parsing failed:", e)
        return {"education": [], "employment": []}


# ==============================
# MAIN PARSER
# ==============================
def parse_resume(file_path):
    text = extract_text(file_path)

    identity = extract_identity(text)
    skills = extract_skills(text)
    structured = extract_structured_sections(text)

    return {
        "identity": identity,
        "skills": skills,
        "education": structured.get("education", []),
        "employment": structured.get("employment", []),
    }
