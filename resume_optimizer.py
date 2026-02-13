import os
import re
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a Senior US Recruiter and ATS Specialist.

STRICT RULES:
- Preserve candidate identity exactly.
- Keep real employers unchanged.
- Do NOT fabricate companies.
- Use only skills present in the resume.
- Align responsibilities with target role.
"""

def extract_ats_score(text):
    for line in text.splitlines():
        if "ATS Score" in line:
            match = re.search(r"([0-9]+(\.[0-9]+)?)", line)
            if match:
                return float(match.group(1))
    return 0.0


def generate_resume(target_role, original_resume, education, employment, additional_experience):
    USER_PROMPT = f"""
Create an ATS-optimized resume.

Target Role: {target_role}

Resume Content:
{original_resume}

Education:
{education}

Employment:
{employment}

Rules:
- Preserve name and contact details.
- Keep real companies.
- Do not insert placeholders.
- Align to target role.
- Provide ATS Score at end.
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
    ats_score = extract_ats_score(resume_text)

    return resume_text + f"\n\nREAL ATS Score: {ats_score}/10"
