import re
from collections import defaultdict

# ==============================
# IDENTITY EXTRACTION
# ==============================
def extract_identity(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    name = ""
    email = ""
    phone = ""

    for line in lines[:10]:
        if "@" in line and "." in line:
            email = line
        elif re.search(r"\d{3}[-.\s]?\d{3}[-.\s]?\d{4}", line):
            phone = line
        elif not name and len(line.split()) <= 4:
            name = line

    return {"name": name, "email": email, "phone": phone}


# ==============================
# SKILL WEIGHTING ENGINE
# ==============================
KNOWN_SKILLS = [
    "java", "spring", "spring boot", "microservices", "aws", "azure",
    "docker", "kubernetes", "jenkins", "kafka", "react", "angular",
    "sql", "mysql", "postgresql", "mongodb", "c#", ".net", "python",
    "hibernate", "rest", "api", "ci/cd"
]


def extract_skills(text):
    """
    Detect and weight skills → return primary & secondary.
    """
    text_lower = text.lower()
    skill_scores = defaultdict(int)

    # 🔹 Detect skill sections
    skill_section_match = re.search(r"(skills|technical skills)(.*?)(\n\n|\Z)", text_lower, re.S)
    if skill_section_match:
        section = skill_section_match.group(2)
        for skill in KNOWN_SKILLS:
            if skill in section:
                skill_scores[skill] += 5  # section weight

    # 🔹 Count frequency
    for skill in KNOWN_SKILLS:
        occurrences = text_lower.count(skill)
        if occurrences:
            skill_scores[skill] += occurrences

    # 🔹 Boost summary section
    summary_match = re.search(r"(summary|professional summary)(.*?)(experience)", text_lower, re.S)
    if summary_match:
        summary = summary_match.group(2)
        for skill in KNOWN_SKILLS:
            if skill in summary:
                skill_scores[skill] += 3

    # 🔹 Sort skills by score
    sorted_skills = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)

    primary = [s for s, score in sorted_skills[:5]]
    secondary = [s for s, score in sorted_skills[5:]]

    return {
        "primary": primary,
        "secondary": secondary,
        "scores": dict(sorted_skills)
    }


# ==============================
# BASIC PARSER (education & employment)
# ==============================
def parse_resume(text):
    education = []
    employment = []

    # naive extraction for now (safe)
    return {
        "education": education,
        "employment": employment
    }
