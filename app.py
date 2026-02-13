from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import uuid
import os

from resume_parser import extract_text, parse_resume, extract_identity
from resume_optimizer import generate_resume
from exporter import export_to_word

app = FastAPI(title="Resume AI")

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
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # ✅ Extract raw text
    resume_text = extract_text(file_path)

    # ❌ Stop if parsing failed
    if not resume_text.strip():
        return {"error": "Resume parsing failed. Upload a text-based PDF or DOCX."}

    # ✅ Parse structured data
    parsed_data = parse_resume(resume_text)

    # ✅ Extract identity
    identity = extract_identity(resume_text)

    # ✅ Generate resume
    final_resume = generate_resume(
        target_role=target_role,
        original_resume=resume_text,
        education=parsed_data.get("education", []),
        employment=parsed_data.get("employment", []),
        additional_experience=[],
    )

    # ✅ Save using candidate name
    filename = f"{identity['name'].replace(' ', '_')}_ATS_Resume.docx"
    export_to_word(final_resume, filename)

    return FileResponse(filename, filename=filename)
