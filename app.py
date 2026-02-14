from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import uuid
import os

from structured_parser import extract_text
from resume_parser import parse_resume, extract_identity, extract_skills
from gap_analyzer import build_timeline, detect_gaps
from resume_optimizer import generate_resume
from exporter import export_to_word

app = FastAPI(title="AI Resume Builder")

templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# In-memory session store
session_store = {}

# ==============================
# HOME PAGE
# ==============================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ==============================
# UPLOAD RESUME
# ==============================
@app.post("/upload", response_class=HTMLResponse)
async def upload_resume(request: Request, file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    # Save uploaded file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Extract clean text from file
    raw_text = extract_text(file_path)

    # Parse structured data
    parsed = parse_resume(raw_text)
    identity = extract_identity(raw_text)
    skills_data = extract_skills(raw_text)

    # Build timeline & detect gaps
    timeline = build_timeline(parsed)
    gaps = detect_gaps(timeline)

    # Determine suggested role (top primary skill)
    suggested_role = ""
    if skills_data.get("primary"):
        suggested_role = f"{skills_data['primary'][0].title()} Developer"

    # Store session data
    session_store[file_id] = {
        "raw_text": raw_text,
        "parsed": parsed,
        "identity": identity,
        "skills": skills_data,
        "gaps": gaps,
    }

    # Render review page
    return templates.TemplateResponse(
        "review.html",
        {
            "request": request,
            "file_id": file_id,
            "identity": identity,
            "primary_skills": skills_data.get("primary", []),
            "secondary_skills": skills_data.get("secondary", []),
            "gaps": gaps,
            "suggested_role": suggested_role,
        },
    )


# ==============================
# GENERATE FINAL RESUME
# ==============================
@app.post("/generate")
async def generate_final_resume(
    request: Request,
    file_id: str = Form(...),
    target_role: str = Form(...),
):
    if file_id not in session_store:
        return HTMLResponse("Session expired. Please upload again.", status_code=400)

    data = session_store[file_id]

    final_resume = generate_resume(
        target_role=target_role,
        original_resume=data["raw_text"],
        education=data["parsed"].get("education", []),
        employment=data["parsed"].get("employment", []),
        additional_experience=[],
        identity=data["identity"],  # ✅ ensures name/email preserved
    )

    # Use candidate name for filename
    candidate_name = data["identity"].get("name", "Candidate").replace(" ", "_")
    output_file = os.path.join(
        OUTPUT_DIR,
        f"{candidate_name}_{target_role.replace(' ', '_')}.docx"
    )

    export_to_word(final_resume, output_file)

    return FileResponse(
        output_file,
        filename=os.path.basename(output_file),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
