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

    original_resume = parse_resume(file_path)

    final_resume = generate_resume(
        target_role=target_role,
        original_resume=original_resume,
        additional_experience=add_projects,
    )

    output_file = f"Generated_{file_id}.docx"
    export_to_word(final_resume, output_file)

    return FileResponse(output_file, filename="Final_ATS_Resume.docx")
