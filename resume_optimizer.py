import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==============================
# SYSTEM PROMPT — IDENTITY LOCK
# ==============================
SYSTEM_PROMPT = """
You are a Senior US Recruiter and ATS Specialist.

🚨 IDENTITY LOCK (ABSOLUTE RULE)
- Preserve candidate name, email, phone, location EXACTLY.
- NEVER replace with placeholders.
- NEVER invent contact details.
- Header must remain unchanged.

EMPLOYMENT INTEGRITY
- Keep real employers unchanged.
- Only add experience for user-approved gaps.

SKILL INTEGRITY
- Use only skills present in resume.

ROLE ALIGNMENT
- Reframe responsibilities to match target role.
- Do not alter factual history.
"""

# ==============================
# RESUME GENERATOR
# ==============================
def generate_resume(
    target_role,
    original_resume,
    education,
    employment,
    identity,
    additional_experience,
):
    """
    Generate ATS resume while preserving identity.
    """

    # 🔒 Build locked identity header
    header = f"""
{identity.get("name", "")}
{identity.get("email", "")} | {identity.get("phone", "")}
"""

    USER_PROMPT = f"""
Create an ATS-optimized resume.

TARGET ROLE:
{target_role}

LOCKED HEADER (MUST USE EXACTLY):
{header}

ORIGINAL RESUME:
{original_resume}

EDUCATION:
{education}

EMPLOYMENT:
{employment}

ADDITIONAL EXPERIENCE:
{additional_experience}

RULES:
- Use the LOCKED HEADER exactly.
- Do not replace or invent identity.
- Keep company names unchanged.
- Align responsibilities with target role.
- Maintain ATS-friendly formatting.
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

    # 🔒 FINAL SAFETY: enforce header if model changed it
    if identity.get("name") not in resume_text:
        resume_text = header + "\n\n" + resume_text

    return resume_text
