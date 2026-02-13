import os
from openai import OpenAI
from ats_scorer import calculate_ats_score

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

def generate_resume(target_role, original_resume, skills, additional_experience):
    USER_PROMPT = f"""
Create an ATS-optimized resume.

Target Role: {target_role}

Resume Content:
{original_resume}

Skills:
Primary: {skills['primary']}
Secondary: {skills['secondary']}

Additional Experience:
{additional_experience}

Rules:
- Preserve identity.
- Keep real companies.
- Align responsibilities with target role.
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
    ats_score = calculate_ats_score(skills, target_role)

    return resume_text + f"\n\nREAL ATS Score: {ats_score}/10"
