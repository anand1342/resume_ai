from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import uuid
import os

from resume_parser import (
    extract_text_from_file,
    parse_resume,
    extract_identity,
    extract_skills
)
from gap_analyzer import build_timeline, detect_gaps
from resume_optimizer import generate_resume
from exporter import export_to_word

app = FastAPI(title="AI Resume Builder")

templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

session_store = {}

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload", response_class=HTMLResponse)
async def upload_resume(request: Request, file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # ✅ FIXED TEXT EXTRACTION
    raw_text = extract_text_from_file(file_path)

    identity = extract_identity(raw_text)
    skills = extract_skills(raw_text)
    parsed = parse_resume(raw_text)

    timeline = build_timeline(parsed)
    gaps = detect_gaps(timeline)

    session_store[file_id] = {
        "raw_text": raw_text,
        "identity": identity,
        "skills": skills,
        "parsed": parsed,
        "gaps": gaps,
    }

    return templates.TemplateResponse(
        "review.html",
        {
            "request": request,
            "file_id": file_id,
            "skills": skills,
            "gaps": gaps,
            "identity": identity
        },
    )

@app.post("/generate")
async def generate_final_resume(
    file_id: str = Form(...),
    target_role: str = Form(...),
):
    data = session_store[file_id]

    final_resume = generate_resume(
        target_role=target_role,
        identity=data["identity"],
        original_resume=data["raw_text"],
        education=data["parsed"]["education"],
        employment=data["parsed"]["employment"],
        additional_experience=[],
    )

    candidate_name = data["identity"]["name"].replace(" ", "_")
    output_file = os.path.join(
        OUTPUT_DIR, f"{candidate_name}_{target_role.replace(' ', '_')}.docx"
    )

    export_to_word(final_resume, output_file)

    return FileResponse(output_file, filename=os.path.basename(output_file))
