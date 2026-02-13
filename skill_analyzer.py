import re
from collections import Counter

KNOWN_SKILLS = [
    "java", "spring", "spring boot", "microservices", "aws", "azure",
    "docker", "kubernetes", "angular", "react", "sql", "mysql",
    "postgresql", "mongodb", "kafka", "jenkins", ".net", "c#", "python",
    "javascript", "node", "hibernate", "rest api"
]

SECTION_WEIGHTS = {
    "skills": 5,
    "summary": 3,
    "experience": 2,
    "other": 1
}


def detect_sections(text: str):
    """Rudimentary section splitter."""
    sections = {
        "skills": "",
        "summary": "",
        "experience": "",
        "other": text.lower()
    }

    lower = text.lower()

    if "skills" in lower:
        sections["skills"] = lower.split("skills")[1][:1000]

    if "summary" in lower:
        sections["summary"] = lower.split("summary")[1][:1000]

    if "experience" in lower:
        sections["experience"] = lower.split("experience")[1][:2000]

    return sections


def analyze_skills(text: str):
    text_lower = text.lower()
    sections = detect_sections(text)

    score = Counter()

    for skill in KNOWN_SKILLS:
        # global mentions
        score[skill] += text_lower.count(skill)

        # section weighted mentions
        for section, content in sections.items():
            if skill in content:
                score[skill] += SECTION_WEIGHTS.get(section, 1)

    # remove zero-score
    score = {k: v for k, v in score.items() if v > 0}

    # sort by weight
    sorted_skills = sorted(score.items(), key=lambda x: x[1], reverse=True)

    primary = [s for s, _ in sorted_skills[:5]]
    secondary = [s for s, _ in sorted_skills[5:]]

    return primary, secondary, sorted_skills
