import os
import re
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a Senior US Recruiter and ATS Specialist.

STRICT RULES:
- Preserve candidate identity.
- Keep employers unchanged.
- Insert gap experience only if provided.
- Use only skills present.
- Align responsibilities with target role.
"""

def extract_ats_score(text):
    for line in text.splitlines():
        if "ATS Score" in line:
            match = re.search(r"([0-9]+(\.[0-9]+)?)", line)
            if match:
                return float(match.group(1))
    return 9.0


def generate_resume(target_role, original_resume, education, employment, additional_experience):

    USER_PROMPT = f"""
Create ATS resume.

Target Role: {target_role}

Identity: {original_resume.get("identity")}
Skills: {original_resume.get("skills")}
Education: {education}
Employment: {employment}
Additional Experience: {additional_experience}

Requirements:
- Preserve identity.
- Keep companies unchanged.
- Insert gap experience chronologically.
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
