import os
import re
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==============================
# SYSTEM PROMPT (Guardrails)
# ==============================
SYSTEM_PROMPT = """
You are a Senior US Recruiter and ATS Specialist.

IDENTITY LOCK:
- Preserve candidate name, email, phone, location, LinkedIn, GitHub exactly.
- Never replace with placeholders.

EMPLOYMENT INTEGRITY:
- Keep existing employers and dates unchanged.
- Only add experience for user-provided gaps.
- Do not fabricate companies.

SKILL INTEGRITY (CRITICAL):
- Only use skills present in the original resume.
- You may group, categorize, or rephrase them.
- You may infer closely related capabilities.
- DO NOT introduce new technologies not mentioned.

ROLE ALIGNMENT:
- Reframe responsibilities to match the target role using existing skills.
- Do not change factual history.
"""


# ==============================
# Extract ATS Score
# ==============================
def extract_ats_score(text: str) -> float:
    match = re.search(r"ATS Score:\s*([0-9.]+)", text)
    return float(match.group(1)) if match else 0.0


# ==============================
# Skill Extraction Guard
# ==============================
def extract_skills(text: str):
    """
    Extract skills from resume text to prevent hallucination.
    """
    lines = text.lower().split("\n")
    skills = set()

    # Expand this list over time
    keywords = [
        "python", "java", "c++", "c#", "sql", "mysql", "postgresql",
        "aws", "azure", "docker", "kubernetes", "pandas", "numpy",
        "spark", "hadoop", "airflow", "react", "node", "django",
        "flask", "tableau", "power bi", "excel", "git", "linux",
        "tensorflow", "pytorch", "etl", "rest api", "microservices",
        "spring", "spring boot", "angular", "vue", "mongodb"
    ]

    for line in lines:
        for word in keywords:
            if word in line:
                skills.add(word)

    return sorted(list(skills))


# ==============================
# Resume Generator
# ==============================
def generate_resume(
    target_role,
    original_resume,
    education,
    employment,
    additional_experience
):
    """
    Generate ATS-optimized resume with integrity safeguards.
    """

    # Extract allowed skills
    allowed_skills = extract_skills(original_resume)

    # Build prompt
    USER_PROMPT = f"""
Create an ATS-optimized resume.

Target Role:
{target_role}

Allowed Skills (use only these technologies):
{allowed_skills}

Original Resume:
{original_resume}

Education:
{education}

Employment History:
{employment}

Additional Experience to include (gap filling):
{additional_experience}

Rules:
- Preserve identity exactly.
- Keep real employers unchanged.
- Insert additional experience chronologically.
- Align responsibilities with target role.
- Use ONLY allowed skills.
- Do NOT introduce new technologies.
- Provide ATS evaluation at the end.
- Print clearly: ATS Score: X.X
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT},
        ],
    )

    output = response.choices[0].message.content
    return output
