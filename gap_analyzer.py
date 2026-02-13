from datetime import datetime


def parse_year(text):
    if not text:
        return None
    try:
        return int(str(text).strip()[:4])
    except Exception:
        return None


def build_timeline(parsed):
    timeline = []

    for edu in parsed.get("education", []):
        timeline.append({
            "type": "Education",
            "label": f"{edu.get('degree', '')} - {edu.get('field', '')}",
            "start": parse_year(edu.get("start_year")),
            "end": parse_year(edu.get("end_year")),
        })

    for job in parsed.get("employment", []):
        timeline.append({
            "type": "Employment",
            "label": f"{job.get('company', '')} - {job.get('role', '')}",
            "start": parse_year(job.get("start_date")),
            "end": parse_year(job.get("end_date")) or datetime.now().year,
        })

    # Remove entries with invalid dates
    timeline = [t for t in timeline if t["start"] and t["end"]]

    # Sort chronologically
    timeline.sort(key=lambda x: x["start"])
    return timeline


def detect_gaps(timeline):
    gaps = []

    for i in range(len(timeline) - 1):
        current = timeline[i]
        nxt = timeline[i + 1]

        gap = nxt["start"] - current["end"]

        if gap > 1:
            gaps.append({
                "from": current["end"],
                "to": nxt["start"],
                "duration_years": gap,
                "between": f"{current['label']} → {nxt['label']}",
            })

    # Reverse chronological order (most recent gap first)
    gaps.sort(key=lambda x: x["to"], reverse=True)
    return gaps
