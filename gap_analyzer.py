from datetime import datetime

def parse_year(text):
    if not text:
        return None
    try:
        return int(text.strip()[:4])
    except:
        return None

def build_timeline(parsed):
    timeline = []

    for edu in parsed["education"]:
        timeline.append({
            "type": "Education",
            "label": f"{edu.get('degree')} - {edu.get('field')}",
            "start": parse_year(edu.get("start_year")),
            "end": parse_year(edu.get("end_year"))
        })

    for job in parsed["employment"]:
        timeline.append({
            "type": "Employment",
            "label": f"{job.get('company')} - {job.get('role')}",
            "start": parse_year(job.get("start_date")),
            "end": parse_year(job.get("end_date")) or datetime.now().year
        })

    timeline = [t for t in timeline if t["start"] and t["end"]]
    timeline.sort(key=lambda x: x["start"])
    return timeline

def detect_gaps(timeline):
    gaps = []
    for i in range(len(timeline) - 1):
        current = timeline[i]
        nxt = timeline[i+1]
        gap = nxt["start"] - current["end"]
        if gap > 1:
            gaps.append({
                "from": current["end"],
                "to": nxt["start"],
                "duration_years": gap,
                "between": f"{current['label']} → {nxt['label']}"
            })

    # Reverse chronological
    gaps.sort(key=lambda x: x["to"], reverse=True)
    return gaps
