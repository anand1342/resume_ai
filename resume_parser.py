import json
import re
import pdfplumber
from docx import Document
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==============================
# FILE TEXT EXTRACTION
# ==============================

def extract_text_from_file(file_path):
    if file_path.lower().endswith(".pdf"):
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text

    elif file_path.lower().endswith(".docx"):
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    else:
        with open(file_path, "r", errors="ignore") as f:
            return f.read()

# ==============================
# IDENTITY EXTRACTION
# ==============================

def extract_identity(text):
    email = re.search(r"[\w\.-]+@[\w\.-]+", text)
    phone = re.search(r"\+?\d[\d\s\-]{8,}", text)
    linkedin = re.search(r"linkedin\.com/in/[^\s]+", text)
    github = re.search(r"github\.com/[^\s]+", text)

    name = text.split("\n")[0].strip()

    return {
        "name": name,
        "email": email.group(0) if email else "",
        "phone": phone.group(0) if phone else "",
        "linkedin": linkedin.group(0) if linkedin else "",
        "github": github.group(0) if github else "",
    }

# ==============================
# SKILL EXTRACTION (IMPROVED)
# ==============================

COMMON_SKILLS = [
    "java", "spring", "spring boot", "hibernate", "microservices",
    "python", "django", "flask", "pandas", "numpy",
    "c#", ".net", "asp.net",
    "javascript", "react", "angular", "vue",
    "sql", "mysql", "postgresql", "mongodb",
    "aws", "azure", "docker", "kubernetes", "jenkins",
    "kafka", "spark", "hadoop", "airflow"
]

def extract_skills(text):
    text_lower = text.lower()
    found = [skill for skill in COMMON_SKILLS if skill in text_lower]
    return sorted(set(found))

# ==============================
# OPENAI PARSER (EDU + EMPLOYMENT)
# ==============================

PARSER_PROMPT = """
Extract factual information from this resume.

Return JSON only:
{
  "education": [],
  "employment": []
}
"""

def parse_resume(text):
    print("\n🔎 Sending resume to OpenAI parser...\n")

    response = client.chat.completions.create(
        model="gpt-4.1",
        temperature=0,
        messages=[
            {"role": "system", "content": PARSER_PROMPT},
            {"role": "user", "content": text}
        ]
    )

    try:
        parsed = json.loads(response.choices[0].message.content)
        print("✅ Parsed successfully")
        return parsed
    except:
        print("❌ Parsing failed")
        return {"education": [], "employment": []}
