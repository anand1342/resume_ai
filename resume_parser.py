import re

# ==============================
# PARSE EDUCATION & EMPLOYMENT
# ==============================
def parse_resume(text: str):
    """
    Extract education and employment using simple heuristics.
    This keeps your gap detection working.
    """

    education = []
    employment = []

    # --- Education ---
    edu_patterns = [
        r"(Bachelor.*?)(\d{4})",
        r"(Master.*?)(\d{4})",
        r"(B\.?Tech.*?)(\d{4})",
        r"(M\.?Tech.*?)(\d{4})",
    ]

    for pattern in edu_patterns:
        for match in re.findall(pattern, text, re.IGNORECASE):
            education.append({
                "degree": match[0],
                "field": "",
                "start_year": "",
                "end_year": match[1],
            })

    # --- Employment ---
    job_pattern = r"([A-Z][A-Za-z &]+)\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?.*?(\d{4})\s*–\s*(Present|\d{4})"

    for match in re.findall(job_pattern, text):
        employment.append({
            "company": match[0],
            "role": "",
            "start_date": match[2],
            "end_date": match[3] if match[3] != "Present" else "",
        })

    return {
        "education": education,
        "employment": employment
    }


# ==============================
# IDENTITY EXTRACTION
# ==============================
def extract_identity(text: str):
    identity = {
        "name": "",
        "email": "",
        "phone": "",
        "location": "",
        "linkedin": "",
        "github": ""
    }

    # Email
    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    if email_match:
        identity["email"] = email_match.group()

    # Phone
    phone_match = re.search(r"(\+?\d[\d\s\-]{8,}\d)", text)
    if phone_match:
        identity["phone"] = phone_match.group()

    # LinkedIn
    linkedin_match = re.search(r"linkedin\.com/in/[^\s]+", text)
    if linkedin_match:
        identity["linkedin"] = linkedin_match.group()

    # GitHub
    github_match = re.search(r"github\.com/[^\s]+", text)
    if github_match:
        identity["github"] = github_match.group()

    # Name (first line heuristic)
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if lines:
        identity["name"] = lines[0]

    return identity


# ==============================
# SKILL EXTRACTION + WEIGHTING
# ==============================
def extract_skills(text: str):
    text_lower = text.lower()

    keywords = [
        "java", "spring", "spring boot", "hibernate", "microservices",
        "c#", ".net", "asp.net",
        "python", "django", "flask",
        "javascript", "react", "angular", "vue",
        "aws", "azure", "docker", "kubernetes",
        "sql", "mysql", "postgresql", "mongodb",
        "jenkins", "kafka"
    ]

    counts = {}
    for skill in keywords:
        count = text_lower.count(skill)
        if count > 0:
            counts[skill] = count

    sorted_skills = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    primary = [s[0] for s in sorted_skills[:5]]
    secondary = [s[0] for s in sorted_skills[5:]]

    return {
        "primary": primary,
        "secondary": secondary,
        "weights": counts
    }
