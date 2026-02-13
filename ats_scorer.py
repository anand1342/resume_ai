import re

# ==============================
# ROLE KEYWORDS
# ==============================

ROLE_KEYWORDS = {
    "java developer": ["java", "spring", "spring boot", "rest api", "microservices", "sql"],
    "data engineer": ["etl", "python", "sql", "data pipeline", "aws", "spark"],
    "qa engineer": ["testing", "selenium", "automation", "test cases", "qa", "defects"],
    "devops engineer": ["ci/cd", "docker", "kubernetes", "aws", "deployment", "infrastructure"],
}


# ==============================
# KEYWORD MATCH SCORE
# ==============================
def keyword_score(text, role):
    role = role.lower()
    keywords = ROLE_KEYWORDS.get(role, [])
    if not keywords:
        return 0.5  # neutral if role not in dictionary

    matches = sum(1 for kw in keywords if kw in text.lower())
    return min(matches / len(keywords), 1.0)


# ==============================
# SKILLS RELEVANCE
# ==============================
def skills_score(text):
    if "technical skills" in text.lower():
        return 1.0
    return 0.5


# ==============================
# STRUCTURE SCORE
# ==============================
def structure_score(text):
    sections = ["summary", "technical skills", "professional experience", "education"]
    found = sum(1 for s in sections if s in text.lower())
    return found / len(sections)


# ==============================
# EXPERIENCE RELEVANCE
# ==============================
def experience_score(text, role):
    return keyword_score(text, role)


# ==============================
# METRICS SCORE
# ==============================
def metrics_score(text):
    if re.search(r"\d+%|\d+\+", text):
        return 1.0
    return 0.5


# ==============================
# FORMATTING SAFETY
# ==============================
def formatting_score(text):
    # basic ATS safety checks
    if "|" in text and "table" in text.lower():
        return 1.0
    return 0.8


# ==============================
# FINAL ATS SCORE
# ==============================
def calculate_ats_score(text, role):
    score = (
        keyword_score(text, role) * 0.30 +
        skills_score(text) * 0.20 +
        structure_score(text) * 0.15 +
        experience_score(text, role) * 0.15 +
        metrics_score(text) * 0.10 +
        formatting_score(text) * 0.10
    )

    return round(score * 10, 2)  # score out of 10
