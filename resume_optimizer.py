import os
import re
from openai import OpenAI

# ==============================
# OpenAI Client
# ==============================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==============================
# SYSTEM PROMPT (STRICT GUARDRAILS)
# ==============================
SYSTEM_PROMPT = """
You are a Senior US Recruiter and ATS Specialist.

IDENTITY LOCK:
- Preserve candidate name, email, phone, location, LinkedIn, GitHub exactly.
- Never replace identity with placeholders.

EMPLOYMENT INTEGRITY:
- Keep existing employers and dates unchanged.
- Only add experience for user-provided gaps.
- Do NOT fabricate companies.

SKILL INTEGRITY:
- Only use skills present in the original resume.
- You may group or categorize them.
- You may infer closely related capabilities.
- DO NOT introduce new technologies.

ROLE ALIGNMENT:
- Reframe responsibilities to match the target role using existing skills.
- Do not alter factual history.
"""

# ==============================
# ATS SCORE EXTRACTION
# ==============================
def extract_ats_score(text: str) -> float:
    """
    Extract ATS score from model output.
    """
    for line in text.splitlines():
        if "ATS Score" in line:
            match = re.search(r"([0-9]+(\.[0-9]+)?)", line)
            if match:
                return float(match.group(1))
    return 0.0


# ==============================
# SKILL EXTRACTION
# ==============================
def extract_skills(text: str):
    """
    Extract skills from resume text to prevent hallucination.
    """
    lines = text.lower().split("\n")
    skills = set()

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
# RESUME GENERATOR
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

    # ==============================
    # USER PROMPT
    # ==============================
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
- Ensure ATS-friendly formatting.

At the end, print:
ATS Score: X.X
"""

    # ==============================
    # CALL MODEL
    # ==============================
    response = client.chat.completions.create(
        model="gpt-4.1",
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT},
        ],
    )

    resume_text = response.choices[0].message.content

    # ==============================
    # ATS SCORING (from model output)
    # ==============================
    ats_score = extract_ats_score(resume_text)

    final_output = (
        resume_text
        + "\n\n====================\n"
        + f"REAL ATS Score: {ats_score}/10\n"
    )

    return final_output
