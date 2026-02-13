from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import uuid
import os

from resume_parser import parse_resume, extract_identity, extract_skills
from structured_parser import extract_education, extract_employment
from gap_analyzer import build_timeline, detect_gaps
from resume_optimizer import generate_resume
from exporter import export_to_word

# =============================
# APP SETUP
# =============================
app = FastAPI(title="AI Resume Builder")

templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# In-memory session store
session_store = {}

# =============================
# HOME
# =============================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# =============================
# UPLOAD RESUME
# =============================
@app.post("/upload", response_class=HTMLResponse)
async def upload_resume(request: Request, file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    # Save file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Read raw text
    with open(file_path, "rb") as f:
        raw_text = f.read().decode(errors="ignore")

    # =============================
    # REAL PARSING
    # =============================
    education = extract_education(raw_text)
    employment = extract_employment(raw_text)

    parsed = {
        "education": education,
        "employment": employment
    }

    # =============================
    # IDENTITY & SKILLS
    # =============================
    identity = extract_identity(raw_text)
    skills = extract_skills(raw_text)

    # Determine primary stack
    primary_stack = skills["primary"][0] if skills["primary"] else "General"

    # =============================
    # TIMELINE & GAPS
    # =============================
    timeline = build_timeline(parsed)
    gaps = detect_gaps(timeline)

    # Store session data
    session_store[file_id] = {
        "raw_text": raw_text,
        "parsed": parsed,
        "identity": identity,
        "skills": skills,
        "primary_stack": primary_stack,
        "gaps": gaps,
    }

    # =============================
    # REVIEW SCREEN
    # =============================
    return templates.TemplateResponse(
        "review.html",
        {
            "request": request,
            "file_id": file_id,
            "identity": identity,
            "skills": skills,
            "primary_stack": primary_stack,
            "gaps": gaps,
        },
    )


# =============================
# ADD GAP EXPERIENCE
# =============================
@app.post("/add-gap")
async def add_gap(
    file_id: str = Form(...),
    company: str = Form(...),
    role: str = Form(...),
    start: str = Form(...),
    end: str = Form(...),
    location: str = Form(...)
):
    if file_id not in session_store:
        return {"error": "Invalid session"}

    session_store[file_id].setdefault("additional_experience", []).append({
        "company": company,
        "role": role,
        "start": start,
        "end": end,
        "location": location
    })

    return {"status": "Gap experience added"}


# =============================
# GENERATE FINAL RESUME
# =============================
@app.post("/generate")
async def generate_final_resume(
    request: Request,
    file_id: str = Form(...),
    target_role: str = Form(...),
):
    if file_id not in session_store:
        return {"error": "Session expired. Please upload again."}

    data = session_store[file_id]

    final_resume = generate_resume(
        target_role=target_role,
        original_resume=data["raw_text"],
        education=data["parsed"]["education"],
        employment=data["parsed"]["employment"],
        additional_experience=data.get("additional_experience", []),
        identity=data["identity"],
    )

    # Safe filename
    candidate_name = data["identity"].get("name", "Candidate").replace(" ", "_")
    safe_role = target_role.replace(" ", "_")

    output_file = os.path.join(
        OUTPUT_DIR, f"{candidate_name}_{safe_role}.docx"
    )

    export_to_word(final_resume, output_file)

    return FileResponse(output_file, filename=os.path.basename(output_file))
