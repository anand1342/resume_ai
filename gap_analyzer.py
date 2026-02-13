from datetime import datetime

def parse_year(text):
    if not text:
        return None
    try:
        return int(str(text)[:4])
    except:
        return None

def build_timeline(parsed):
    timeline = []

    for edu in parsed.get("education", []):
        timeline.append({
            "label": edu.get("degree"),
            "start": parse_year(edu.get("start_year")),
            "end": parse_year(edu.get("end_year")),
        })

    for job in parsed.get("employment", []):
        timeline.append({
            "label": job.get("company"),
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
        if gap > 0:
            gaps.append({
                "from": timeline[i]["end"],
                "to": timeline[i+1]["start"],
                "duration": gap,
                "between": f"{timeline[i]['label']} → {timeline[i+1]['label']}",
            })
    return gaps
