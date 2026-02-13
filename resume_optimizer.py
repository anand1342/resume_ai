import os
import re
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a Senior US Recruiter and ATS Specialist.

STRICT RULES:
- Preserve identity exactly.
- Do NOT use placeholders.
- Keep real employers unchanged.
- Do NOT fabricate companies.
- Align responsibilities with target role.
"""

def extract_ats_score(text):
    match = re.search(r"ATS Score[:\s]+(\d+)", text)
    return float(match.group(1)) if match else 0

def generate_resume(target_role, identity, original_resume, education, employment, additional_experience):
    USER_PROMPT = f"""
Create an ATS-optimized resume.

Candidate Identity:
Name: {identity['name']}
Email: {identity['email']}
Phone: {identity['phone']}
LinkedIn: {identity['linkedin']}
GitHub: {identity['github']}

Target Role: {target_role}

Resume Content:
{original_resume}

Education:
{education}

Employment:
{employment}

Additional Experience:
{additional_experience}

Rules:
- Preserve identity.
- Keep companies real.
- Align to target role.
- Provide ATS Score.
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT},
        ],
    )

    resume_text = response.choices[0].message.content
    score = extract_ats_score(resume_text)

    return resume_text + f"\n\nREAL ATS Score: {score}/10"
