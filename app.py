from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import uuid
import os

from resume_parser import parse_resume
from gap_analyzer import build_timeline, detect_gaps
from resume_optimizer import generate_resume
from exporter import export_to_word

app = FastAPI(title="Resume AI")

templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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

    parsed = parse_resume(file_path)

    timeline = build_timeline(parsed)
    gaps = detect_gaps(timeline)

    session_store[file_id] = {
        "file_path": file_path,
        "parsed": parsed,
        "gaps": gaps,
    }

    return templates.TemplateResponse(
        "review.html",
        {
            "request": request,
            "file_id": file_id,
            "identity": parsed.get("identity"),
            "skills": parsed.get("skills"),
            "gaps": gaps,
        },
    )


@app.post("/generate")
async def generate(
    file_id: str = Form(...),
    target_role: str = Form(...),
    gap_action: str = Form("ignore"),
    employer: str = Form(""),
    job_title: str = Form(""),
    location: str = Form(""),
):
    data = session_store[file_id]
    parsed = data["parsed"]

    additional_experience = []

    if gap_action == "fill" and employer:
        additional_experience.append({
            "company": employer,
            "role": job_title or target_role,
            "location": location,
        })

    final_resume = generate_resume(
        target_role=target_role,
        original_resume=parsed.get("raw_text"),
        education=parsed.get("education"),
        employment=parsed.get("employment"),
        additional_experience=additional_experience,
    )

    candidate_name = parsed["identity"]["name"].replace(" ", "_")
    output_file = f"{candidate_name}_ATS_Resume.docx"

    export_to_word(final_resume, output_file)

    os.remove(data["file_path"])

    return FileResponse(output_file, filename=output_file)
