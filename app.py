from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import uuid
import os

from resume_parser import extract_identity, extract_skills, suggest_roles, estimate_experience
from gap_analyzer import build_timeline, detect_gaps, auto_fill_gaps
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
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    raw_text = open(file_path, "rb").read().decode(errors="ignore")

    identity = extract_identity(raw_text)
    skills = extract_skills(raw_text)
    role_suggestions = suggest_roles(skills["primary"])
    experience_estimate = estimate_experience(skills["weights"])

    # Dummy parsed data for gap detection (extend later)
    parsed = {"education": [], "employment": []}
    timeline = build_timeline(parsed)
    gaps = detect_gaps(timeline)

    session_store[file_id] = {
        "raw_text": raw_text,
        "identity": identity,
        "skills": skills,
        "gaps": gaps
    }

    return templates.TemplateResponse(
        "review.html",
        {
            "request": request,
            "file_id": file_id,
            "identity": identity,
            "skills": skills,
            "role_suggestions": role_suggestions,
            "experience_estimate": experience_estimate,
            "gaps": gaps,
        },
    )


@app.post("/generate")
async def generate_final_resume(
    file_id: str = Form(...),
    target_role: str = Form(...),
):
    data = session_store[file_id]

    additional_experience = auto_fill_gaps(data["gaps"], target_role)

    final_resume = generate_resume(
        target_role=target_role,
        original_resume=data["raw_text"],
        skills=data["skills"],
        additional_experience=additional_experience,
    )

    candidate_name = data["identity"]["name"] or "Candidate"
    output_file = os.path.join(
        OUTPUT_DIR, f"{candidate_name}_{target_role}.docx".replace(" ", "_")
    )

    export_to_word(final_resume, output_file)

    return FileResponse(output_file, filename=os.path.basename(output_file))
