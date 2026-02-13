from datetime import datetime

def parse_year(text):
    try:
        return int(text[:4])
    except:
        return None

def build_timeline(parsed):
    timeline = []

    for edu in parsed.get("education", []):
        timeline.append({
            "type": "Education",
            "start": parse_year(edu.get("start_year")),
            "end": parse_year(edu.get("end_year")),
        })

    for job in parsed.get("employment", []):
        timeline.append({
            "type": "Employment",
            "start": parse_year(job.get("start_date")),
            "end": parse_year(job.get("end_date")) or datetime.now().year,
        })

    timeline = [t for t in timeline if t["start"] and t["end"]]
    timeline.sort(key=lambda x: x["start"])
    return timeline

def detect_gaps(timeline):
    gaps = []
    for i in range(len(timeline) - 1):
        gap = timeline[i+1]["start"] - timeline[i]["end"]
        if gap > 1:
            gaps.append({"from": timeline[i]["end"], "to": timeline[i+1]["start"], "years": gap})
    return gaps
