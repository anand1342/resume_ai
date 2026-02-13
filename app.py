from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import uuid
import os

from resume_parser import parse_resume, extract_identity, extract_skills
from gap_analyzer import build_timeline, detect_gaps
from resume_optimizer import generate_resume
from exporter import export_to_word

# ==============================
# APP INIT
# ==============================

app = FastAPI(title="AI Resume Builder")

templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# In-memory session storage
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
    try:
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

        # Save file
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Read text safely
        raw_bytes = open(file_path, "rb").read()
        raw_text = raw_bytes.decode(errors="ignore")

        # Parse resume
        parsed = parse_resume(raw_text)
        identity = extract_identity(raw_text)
        skills = extract_skills(raw_text)

        # Detect gaps
        timeline = build_timeline(parsed)
        gaps = detect_gaps(timeline)

        # Store session
        session_store[file_id] = {
            "raw_text": raw_text,
            "parsed": parsed,
            "identity": identity,
            "skills": skills or [],
            "gaps": gaps or [],
        }

        return templates.TemplateResponse(
            "review.html",
            {
                "request": request,
                "file_id": file_id,
                "skills": skills or [],
                "gaps": gaps or [],
            },
        )

    except Exception as e:
        return HTMLResponse(f"Upload error: {str(e)}", status_code=500)

# ==============================
# GENERATE PREVIEW (WITH GAP FILL)
# ==============================

@app.post("/generate", response_class=HTMLResponse)
async def generate_preview(request: Request):
    try:
        form = await request.form()

        file_id = form.get("file_id")
        target_role = form.get("target_role")

        if not file_id or file_id not in session_store:
            return HTMLResponse("Session expired. Please upload resume again.", status_code=400)

        data = session_store[file_id]

        # --------------------------
        # COLLECT GAP INPUTS
        # --------------------------
        additional_experience = []
        gaps = data.get("gaps", [])

        for i, gap in enumerate(gaps, start=1):
            if form.get(f"fill_{i}") == "yes":
                additional_experience.append({
                    "company": form.get(f"company_{i}", ""),
                    "role": form.get(f"role_{i}", target_role),
                    "location": form.get(f"location_{i}", ""),
                    "description": form.get(f"desc_{i}", ""),
                    "start": gap.get("from"),
                    "end": gap.get("to"),
                })

        # --------------------------
        # GENERATE RESUME TEXT
        # --------------------------
        final_resume = generate_resume(
            target_role=target_role,
            original_resume=data["raw_text"],
            education=data["parsed"].get("education", []),
            employment=data["parsed"].get("employment", []),
            additional_experience=additional_experience,
        )

        # Save to session
        session_store[file_id]["generated_resume"] = final_resume
        session_store[file_id]["target_role"] = target_role

        # --------------------------
        # SHOW PREVIEW PAGE
        # --------------------------
        return templates.TemplateResponse(
            "preview.html",
            {
                "request": request,
                "file_id": file_id,
                "resume_text": final_resume,
            },
        )

    except Exception as e:
        return HTMLResponse(f"Generation error: {str(e)}", status_code=500)

# ==============================
# DOWNLOAD FINAL RESUME
# ==============================

@app.post("/download")
async def download_resume(request: Request):
    try:
        form = await request.form()

        file_id = form.get("file_id")
        edited_resume = form.get("edited_resume")

        if not file_id or file_id not in session_store:
            return HTMLResponse("Session expired.", status_code=400)

        data = session_store[file_id]

        candidate_name = data["identity"].get("name", "Candidate").replace(" ", "_")
        target_role = data.get("target_role", "Resume")

        output_file = os.path.join(
            OUTPUT_DIR,
            f"{candidate_name}_{target_role.replace(' ', '_')}.docx"
        )

        export_to_word(edited_resume, output_file)

        return FileResponse(
            output_file,
            filename=os.path.basename(output_file),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

    except Exception as e:
        return HTMLResponse(f"Download error: {str(e)}", status_code=500)
