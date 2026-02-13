import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a senior recruiter creating ATS-optimized resumes.

RULES:
- Preserve identity exactly.
- Do NOT fabricate companies.
- Only add experience if user provided.
- Align resume to target role.
- Keep skills realistic.
"""


def generate_resume(target_role, original_resume, education, employment, additional_experience, identity):
    prompt = f"""
Create ATS-optimized resume.

Target Role: {target_role}

Candidate Identity:
Name: {identity.get("name")}
Email: {identity.get("email")}
Phone: {identity.get("phone")}

Original Resume:
{original_resume}

Education:
{education}

Employment:
{employment}

Additional Experience:
{additional_experience}

Return a complete ATS resume.
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
