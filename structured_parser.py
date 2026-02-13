import re

# -----------------------------
# EDUCATION EXTRACTION
# -----------------------------
def extract_education(text: str):
    education = []
    lines = text.split("\n")

    for line in lines:
        if any(keyword in line.lower() for keyword in ["bachelor", "master", "b.tech", "m.tech", "bsc", "msc"]):
            years = re.findall(r"(19|20)\d{2}", line)
            education.append({
                "degree": line.strip(),
                "field": "",
                "start_year": years[0] if years else "",
                "end_year": years[-1] if len(years) > 1 else "",
            })

    return education


# -----------------------------
# EMPLOYMENT EXTRACTION
# -----------------------------
def extract_employment(text: str):
    employment = []
    lines = text.split("\n")

    for i, line in enumerate(lines):
        if any(keyword in line.lower() for keyword in ["developer", "engineer", "analyst", "consultant"]):
            dates = re.findall(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s?(20\d{2})", line)
            employment.append({
                "company": line.strip(),
                "role": line.strip(),
                "start_date": dates[0][1] if dates else "",
                "end_date": dates[-1][1] if dates else "",
            })

    return employment
