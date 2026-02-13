import re

# ===============================
# IDENTITY EXTRACTION
# ===============================

def extract_identity(text: str) -> dict:
    """
    Extract candidate identity from clean resume text.
    """

    identity = {
        "name": "",
        "email": "",
        "phone": "",
        "location": "",
        "linkedin": "",
        "github": "",
    }

    if not text:
        return identity

    # Email
    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    if email_match:
        identity["email"] = email_match.group()

    # Phone
    phone_match = re.search(r"\+?\d[\d\-\s]{8,}\d", text)
    if phone_match:
        identity["phone"] = phone_match.group()

    # LinkedIn
    linkedin_match = re.search(r"linkedin\.com/in/[A-Za-z0-9\-_/]+", text, re.I)
    if linkedin_match:
        identity["linkedin"] = linkedin_match.group()

    # GitHub
    github_match = re.search(r"github\.com/[A-Za-z0-9\-_/]+", text, re.I)
    if github_match:
        identity["github"] = github_match.group()

    # Name → assume first non-empty line without symbols
    lines = text.split("\n")
    for line in lines[:10]:
        line = line.strip()
        if len(line.split()) >= 2 and not any(char.isdigit() for char in line):
            identity["name"] = line
            break

    # Location (simple heuristic)
    location_match = re.search(r"[A-Za-z]+,\s?[A-Za-z]{2}", text)
    if location_match:
        identity["location"] = location_match.group()

    return identity
