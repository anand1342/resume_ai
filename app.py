from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import uuid
import os

from resume_parser import parse_resume
from resume_optimizer import generate_resume
from exporter import export_to_word

app = FastAPI(title="Resume AI")

# Ensure templates directory exists (prevents Render errors)
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate")
async def generate(
    request: Request,
    file: UploadFile = File(...),
    target_role: str = Form(...),
    add_projects: str = Form("yes"),
):
    # Generate unique file ID
    file_id = str(uuid.uuid4())
    safe_filename = file.filename.replace(" ", "_")
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{safe_filename}")

    # Save uploaded file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Parse resume content
   # Read resume text
with open(file_path, "r", errors="ignore") as f:
    resume_text = f.read()

# Parse resume
parsed_data = parse_resume(resume_text)

# Generate resume
final_resume = generate_resume(
    target_role=target_role,
    original_resume=resume_text,
    education=parsed_data.get("education", []),
    employment=parsed_data.get("employment", []),
    additional_experience=add_projects,
)


    # Export to Word
    output_file = f"Generated_{file_id}.docx"
    export_to_word(final_resume, output_file)

    # Return file download
    return FileResponse(
        path=output_file,
        filename="Final_ATS_Resume.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
