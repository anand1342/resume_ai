import re
from collections import Counter

# ==============================
# RESUME PARSER
# ==============================

def parse_resume(text):
    """
    Extract education and employment timeline from resume text.
    This is a lightweight parser — avoids hallucination.
    """

    education = []
    employment = []

    # ------------------------------
    # EDUCATION EXTRACTION
    # ------------------------------
    edu_patterns = [
        r"(Bachelor|Master|B\.Tech|M\.Tech|BSc|MSc|MBA)[^\n]*\b(20\d{2})\b",
        r"(University|College)[^\n]*\b(20\d{2})\b",
    ]

    for pattern in edu_patterns:
        for match in re.findall(pattern, text, re.IGNORECASE):
            education.append({
                "degree": match[0],
                "end_year": match[-1],
                "start_year": "",
                "field": ""
            })

    # ------------------------------
    # EMPLOYMENT EXTRACTION
    # ------------------------------
    job_patterns = [
        r"([A-Z][A-Za-z &]+)\s*\|\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?.*\d{4}\s*[-–]\s*(Present|\d{4})",
        r"([A-Z][A-Za-z &]+)\s*(20\d{2})\s*[-–]\s*(20\d{2}|Present)",
    ]

    for pattern in job_patterns:
        for match in re.findall(pattern, text):
            employment.append({
                "company": match[0],
                "role": "",
                "start_date": match[1] if len(match) > 1 else "",
                "end_date": match[-1],
            })

    return {
        "education": education,
        "employment": employment,
    }


# ==============================
# IDENTITY EXTRACTION (ROBUST)
# ==============================
def extract_identity(text):
    """
    Extract name, email, phone safely.
    Prevents garbage values from binary text.
    """

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    name = ""
    email = ""
    phone = ""

    # ------------------------------
    # EMAIL
    # ------------------------------
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    if email_match:
        email = email_match.group(0)

    # ------------------------------
    # PHONE
    # ------------------------------
    phone_match = re.search(r"\+?\d[\d\-\(\) ]{8,}\d", text)
    if phone_match:
        phone = phone_match.group(0)

    # ------------------------------
    # NAME DETECTION LOGIC
    # ------------------------------
    for line in lines[:10]:  # only first meaningful lines
        if any(char.isdigit() for char in line):
            continue
        if "@" in line:
            continue
        if len(line) < 3 or len(line) > 50:
            continue

        words = line.split()

        # Must look like a real name
        if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words):
            name = line
            break

    # ------------------------------
    # FALLBACK FROM EMAIL
    # ------------------------------
    if not name and email:
        username = email.split("@")[0]
        username = username.replace(".", " ").replace("_", " ")
        name = username.title()

    return {
        "name": name if name else "Candidate",
        "email": email,
        "phone": phone,
    }


# ==============================
# SKILL EXTRACTION WITH WEIGHTING
# ==============================
def extract_skills(text):
    """
    Extract skills and determine primary vs secondary based on frequency.
    """

    text_lower = text.lower()

    skill_keywords = [
        "java", "spring", "spring boot", "hibernate",
        "python", "django", "flask",
        "c#", ".net", "asp.net",
        "javascript", "react", "angular", "vue",
        "aws", "azure", "docker", "kubernetes",
        "sql", "mysql", "postgresql", "mongodb",
        "microservices", "rest api", "kafka", "jenkins"
    ]

    found = []
    for skill in skill_keywords:
        if skill in text_lower:
            count = text_lower.count(skill)
            found.extend([skill] * count)

    counter = Counter(found)

    primary = [skill for skill, count in counter.items() if count >= 3]
    secondary = [skill for skill, count in counter.items() if count < 3]

    return {
        "primary": sorted(primary),
        "secondary": sorted(secondary),
    }
