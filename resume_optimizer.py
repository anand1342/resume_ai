import re

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a Senior US Recruiter and ATS Specialist.

STRICT RULES:
- No invented employers
- No exaggerated metrics
- US formatting standards

ROLE TRANSFORMATION (MANDATORY):

Aggressively align the entire resume to the Target Job Title.

For ANY Target Role:

- Reframe previous responsibilities through the lens of the selected role.
- Highlight role-relevant activities even if original title was different.
- De-emphasize work not aligned to the target role.
- Preserve factual integrity but shift narrative positioning.

Examples:

If Target Role = QA Engineer:
→ Emphasize testing, validation, automation, defect reduction

If Target Role = Java Developer:
→ Emphasize backend development, APIs, performance, scalability

If Target Role = Data Analyst:
→ Emphasize analytics, SQL, reporting, insights

If Target Role = DevOps:
→ Emphasize CI/CD, infrastructure, deployment

If Target Role = Product Manager:
→ Emphasize delivery, stakeholder coordination, roadmap impact

The resume MUST read like the candidate primarily belongs to the Target Role.
"""


def extract_ats_score(text):
    for line in text.splitlines():
        if "ATS Score" in line:
            match = re.search(r"([0-9]+(\.[0-9]+)?)", line)
            if match:
                return float(match.group(1))
    return 0.0


def generate_resume(target_role, original_resume, education, employment, additional_experience):
    attempt = 0
    final_output = ""

    while attempt < 3:
        attempt += 1

        USER_PROMPT = f"""
Generate an ATS-optimized resume.

STRICT STRUCTURE:
1. Header
2. Professional Summary (7–8 bullets)
3. Technical Skills (TABLE FORMAT ONLY)
4. Professional Experience (7–8 bullets per role + Environment)
5. Additional Experience
6. Education

Target Role: {target_role}

Original Resume:
{original_resume}

Education:
{education}

Employment:
{employment}

Additional Experience:
{additional_experience}

After writing:
1. Validate strong alignment with Target Role.
2. Then provide ATS Evaluation.
3. Print clearly: ATS Score: X.X
4. If ATS < 9.0, internally revise before returning.
"""

        response = client.chat.completions.create(
            model="gpt-4.1",
            temperature=0.2,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT}
            ]
        )

        output = response.choices[0].message.content
        score = extract_ats_score(output)

        print(f"Attempt {attempt}, ATS Score: {score}")

        final_output = output

        if score >= 9.0:
            break

    return final_output
