from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import uuid
import os

from resume_parser import parse_resume
from resume_optimizer import generate_resume
from exporter import export_to_word

app = FastAPI(title="Resume AI")

templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ==============================
# HOME PAGE
# ==============================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ==============================
# UPLOAD RESUME → PARSE → REVIEW
# ==============================
@app.post("/upload", response_class=HTMLResponse)
async def upload_resume(request: Request, file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

        # Save file
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Parse resume text
        parsed = parse_resume(file_path)

        # Ensure parsed structure exists
        identity = parsed.get("identity", {})
        skills = parsed.get("skills", [])
        education = parsed.get("education", [])
        employment = parsed.get("employment", [])

        return templates.TemplateResponse(
            "review.html",
            {
                "request": request,
                "identity": identity,
                "skills": skills,
                "education": education,
                "employment": employment,
                "file_id": file_id,
            },
        )

    except Exception as e:
        return HTMLResponse(f"<h3>Upload Error:</h3><pre>{str(e)}</pre>", status_code=500)


# ==============================
# GENERATE FINAL RESUME
# ==============================
@app.post("/generate")
async def generate(
    file_id: str = Form(...),
    target_role: str = Form(...),
):
    try:
        # Find uploaded file
        file_path = None
        for f in os.listdir(UPLOAD_DIR):
            if f.startswith(file_id):
                file_path = os.path.join(UPLOAD_DIR, f)
                break

        if not file_path:
            return HTMLResponse("File not found", status_code=404)

        # Parse again for full data
        parsed = parse_resume(file_path)

        identity = parsed.get("identity", {})
        skills = parsed.get("skills", [])
        education = parsed.get("education", [])
        employment = parsed.get("employment", [])

        # Generate resume
        final_resume = generate_resume(
            target_role=target_role,
            original_resume=str(parsed),
            education=education,
            employment=employment,
            additional_experience=[],
        )

        # Save with candidate name
        candidate_name = identity.get("name", "Candidate").replace(" ", "_")
        output_file = f"{candidate_name}_ATS_Resume.docx"

        export_to_word(final_resume, output_file)

        return FileResponse(output_file, filename=output_file)

    except Exception as e:
        return HTMLResponse(f"<h3>Generation Error:</h3><pre>{str(e)}</pre>", status_code=500)
