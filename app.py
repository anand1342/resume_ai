from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import uuid, os, re

from resume_parser import parse_resume
from resume_optimizer import generate_resume
from exporter import export_to_word
from gap_analyzer import build_timeline, detect_gaps

app = FastAPI(title="Resume AI")

templates = Jinja2Templates(directory="templates")
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

TEMP_DATA = {}  # store session data


def safe_filename(name):
    return re.sub(r'[^a-zA-Z0-9]', '_', name)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    target_role: str = Form(...),
):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    with open(file_path, "wb") as f:
        f.write(await file.read())

    with open(file_path, "r", errors="ignore") as f:
        resume_text = f.read()

    parsed = parse_resume(resume_text)
    timeline = build_timeline(parsed)
    gaps = detect_gaps(timeline)

    TEMP_DATA[file_id] = {
        "resume_text": resume_text,
        "parsed": parsed,
        "target_role": target_role,
        "gaps": gaps,
    }

    if not gaps:
        return await generate_final_resume(file_id, [])

    return templates.TemplateResponse(
        "gaps.html",
        {"request": request, "gaps": gaps, "file_id": file_id},
    )


@app.post("/generate")
async def generate_with_gaps(
    request: Request,
    file_id: str = Form(...),
    company: list[str] = Form([]),
    role: list[str] = Form([]),
    location: list[str] = Form([]),
    start: list[str] = Form([]),
    end: list[str] = Form([]),
):
    additional_experience = []

    for i in range(len(company)):
        if company[i]:
            additional_experience.append({
                "company": company[i],
                "role": role[i],
                "location": location[i],
                "start": start[i],
                "end": end[i],
            })

    return await generate_final_resume(file_id, additional_experience)


async def generate_final_resume(file_id, additional_experience):
    data = TEMP_DATA[file_id]

    final_resume = generate_resume(
        target_role=data["target_role"],
        original_resume=data["resume_text"],
        education=data["parsed"].get("education", []),
        employment=data["parsed"].get("employment", []),
        additional_experience=additional_experience,
    )

    candidate_name = data["resume_text"].split("\n")[0].strip()
    output_file = f"{safe_filename(candidate_name)}_Resume.docx"

    export_to_word(final_resume, output_file)

    return FileResponse(output_file, filename=output_file)
