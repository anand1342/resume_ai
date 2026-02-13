import os, re
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a Senior US Recruiter and ATS Specialist.

IDENTITY LOCK:
- Preserve name, email, phone, location, LinkedIn, GitHub exactly.
- Never invent employers or dates.
- Only add experience for provided gaps.

ROLE ALIGNMENT:
Reframe responsibilities to match the target role without changing facts.
"""

def extract_ats_score(text):
    match = re.search(r"ATS Score:\s*([0-9.]+)", text)
    return float(match.group(1)) if match else 0.0


def generate_resume(target_role, original_resume, education, employment, additional_experience):
    prompt = f"""
Create an ATS-optimized resume.

Target Role: {target_role}

Original Resume:
{original_resume}

Education: {education}
Employment: {employment}
Additional Experience: {additional_experience}

Rules:
- Preserve identity.
- Keep real employers.
- Insert additional experience chronologically.
- Provide ATS Score at end.
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content
