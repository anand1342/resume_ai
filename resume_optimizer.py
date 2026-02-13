import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a Senior US Recruiter.

RULES:
- Preserve identity exactly.
- Keep companies unchanged.
- Use only existing skills.
- Align to target role.
"""


def generate_resume(target_role, original_resume, education, employment, additional_experience):
    prompt = f"""
Create an ATS-optimized resume.

Target Role: {target_role}

Resume Content:
{original_resume}

Education:
{education}

Employment:
{employment}

Additional Experience:
{additional_experience}

Include ATS Score at end.
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
