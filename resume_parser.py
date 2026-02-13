import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==============================
# RESUME PARSER PROMPT
# ==============================
PARSER_PROMPT = """
You are a resume parsing engine.

Extract ONLY factual information.

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

# ==============================
# SAFE TEXT CLEANER
# ==============================
def clean_text(text: str) -> str:
    if not text:
        return ""
    return text.replace("\x00", " ").strip()

# ==============================
# PARSE RESUME
# ==============================
def parse_resume(resume_text):
    resume_text = clean_text(resume_text)

    if not resume_text:
        return {"education": [], "employment": []}

    response = client.chat.completions.create(
        model="gpt-4.1",
        temperature=0,
        messages=[
            {"role": "system", "content": PARSER_PROMPT},
            {"role": "user", "content": resume_text[:12000]},  # limit size
        ],
    )

    try:
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {"education": [], "employment": []}

# ==============================
# IDENTITY EXTRACTION
# ==============================
def extract_identity(text: str):
    lines = text.split("\n")

    identity = {
        "name": "",
        "email": "",
        "phone": "",
        "location": "",
        "linkedin": "",
        "github": "",
    }

    for line in lines[:15]:
        if "@" in line and "." in line:
            identity["email"] = line.strip()

        if any(char.isdigit() for char in line) and len(line) >= 10:
            identity["phone"] = line.strip()

        if "linkedin.com" in line.lower():
            identity["linkedin"] = line.strip()

        if "github.com" in line.lower():
            identity["github"] = line.strip()

    identity["name"] = lines[0].strip() if lines else "Candidate"

    return identity

# ==============================
# SKILL EXTRACTION
# ==============================
def extract_skills(text: str):
    keywords = [
        "python", "java", "c++", "c#", "sql", "mysql", "postgresql",
        "aws", "azure", "docker", "kubernetes", "pandas", "numpy",
        "spark", "hadoop", "airflow", "react", "node", "django",
        "flask", "tableau", "power bi", "excel", "git", "linux",
        "tensorflow", "pytorch", "etl", "rest api", "microservices",
        "spring", "spring boot", "angular", "vue", "mongodb",
        ".net", "asp.net", "mvc", "entity framework"
    ]

    text_lower = text.lower()
    skills = [k for k in keywords if k in text_lower]

    return sorted(list(set(skills)))
