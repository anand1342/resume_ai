import re
from collections import Counter

# ==============================
# IDENTITY EXTRACTION
# ==============================
def extract_identity(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    name = ""
    for line in lines[:6]:
        if (
            "@" not in line
            and not re.search(r"\d", line)
            and len(line.split()) <= 4
        ):
            name = line
            break

    email = re.search(r"[\w\.-]+@[\w\.-]+", text)
    phone = re.search(r"\+?\d[\d\s\-\(\)]{8,}", text)
    linkedin = re.search(r"linkedin\.com/in/[^\s]+", text, re.I)
    github = re.search(r"github\.com/[^\s]+", text, re.I)

    return {
        "name": name,
        "email": email.group(0) if email else "",
        "phone": phone.group(0) if phone else "",
        "linkedin": linkedin.group(0) if linkedin else "",
        "github": github.group(0) if github else "",
    }


# ==============================
# SKILL EXTRACTION + WEIGHTING
# ==============================

SKILL_KEYWORDS = [
    "java", "spring", "spring boot", "hibernate",
    "microservices", "kafka", "aws", "docker",
    "kubernetes", "sql", "mysql", "postgresql",
    "mongodb", "react", "angular", "javascript",
    "c#", ".net", "azure", "jenkins"
]

def extract_skills(text):
    text_lower = text.lower()
    counts = Counter()

    for skill in SKILL_KEYWORDS:
        counts[skill] = text_lower.count(skill)

    counts = {k: v for k, v in counts.items() if v > 0}
    sorted_skills = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    primary = [s for s, _ in sorted_skills[:5]]
    secondary = [s for s, _ in sorted_skills[5:12]]
    others = [s for s, _ in sorted_skills[12:]]

    return {
        "primary": primary,
        "secondary": secondary,
        "others": others,
        "all": [s for s, _ in sorted_skills],
        "weights": counts
    }


# ==============================
# ROLE SUGGESTION (A)
# ==============================
def suggest_roles(primary_skills):
    mapping = {
        "java": ["Java Developer", "Backend Engineer"],
        "spring": ["Java Developer", "Microservices Engineer"],
        "aws": ["Cloud Engineer", "DevOps Engineer"],
        "docker": ["DevOps Engineer"],
        "kubernetes": ["DevOps Engineer"],
        "react": ["Frontend Developer"],
        "angular": ["Frontend Developer"],
        "sql": ["Data Engineer", "Backend Developer"],
    }

    suggestions = set()
    for skill in primary_skills:
        for role in mapping.get(skill, []):
            suggestions.add(role)

    return sorted(list(suggestions))


# ==============================
# EXPERIENCE ESTIMATION (B)
# ==============================
def estimate_experience(skill_weights):
    experience = {}
    for skill, count in skill_weights.items():
        years = min(5, max(1, count // 2))
        experience[skill] = years
    return experience
