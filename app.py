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


def safe_filename(name):
    return re.sub(r'[^a-zA-Z0-9]', '_', name)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate")
async def generate(
    request: Request,
    file: UploadFile = File(...),
    target_role: str = Form(...),
):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    # Save uploaded file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Read text
    with open(file_path, "r", errors="ignore") as f:
        resume_text = f.read()

    parsed = parse_resume(resume_text)

    # Detect gaps
    timeline = build_timeline(parsed)
    gaps = detect_gaps(timeline)

    # For web version we skip interactive gap filling
    additional_experience = []

    final_resume = generate_resume(
        target_role=target_role,
        original_resume=resume_text,
        education=parsed.get("education", []),
        employment=parsed.get("employment", []),
        additional_experience=additional_experience,
    )

    candidate_name = resume_text.split("\n")[0].strip()
    output_file = f"{safe_filename(candidate_name)}_Resume.docx"

    export_to_word(final_resume, output_file)

    return FileResponse(output_file, filename=output_file)
