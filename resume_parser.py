import re
from collections import Counter
from skill_analyzer import analyze_skills


# -----------------------------
# IDENTITY EXTRACTION
# -----------------------------
def extract_identity(text: str):
    email = re.search(r"[\w\.-]+@[\w\.-]+", text)
    phone = re.search(r"\+?\d[\d\s\-]{8,}", text)

    lines = text.split("\n")
    name = lines[0].strip() if lines else "Candidate"

    return {
        "name": name,
        "email": email.group(0) if email else "",
        "phone": phone.group(0) if phone else "",
    }


# -----------------------------
# SKILL EXTRACTION + WEIGHTING
# -----------------------------
KNOWN_SKILLS = [
    "java", "spring", "spring boot", "c#", ".net", "asp.net",
    "python", "django", "flask",
    "aws", "azure", "docker", "kubernetes",
    "sql", "mysql", "postgresql", "mongodb",
    "react", "angular", "vue", "javascript",
    "microservices", "kafka", "jenkins"
]


def extract_skills(text):
    primary, secondary, weighted = analyze_skills(text)
    return {
        "primary": primary,
        "secondary": secondary,
        "weighted": weighted
    }

    for skill in KNOWN_SKILLS:
        occurrences = text_lower.count(skill)
        if occurrences:
            counter[skill] += occurrences

    primary = [skill for skill, count in counter.most_common(5)]
    secondary = [skill for skill in counter if skill not in primary]

    return {
        "primary": primary,
        "secondary": secondary,
        "all": list(counter.keys())
    }


# -----------------------------
# PARSE RESUME (STRUCTURED)
# -----------------------------
def parse_resume(text: str):
    # kept for compatibility
    return {
        "education": [],
        "employment": []
    }
