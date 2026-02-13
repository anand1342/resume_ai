from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import uuid
import os

from resume_parser import parse_resume
from resume_optimizer import generate_resume
from gap_analyzer import build_timeline, detect_gaps
from exporter import export_to_word

app = FastAPI(title="AI Resume Builder")

templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ================= HOME =================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ================= UPLOAD =================
@app.post("/upload")
async def upload_resume(request: Request, file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    with open(file_path, "wb") as f:
        f.write(await file.read())

    parsed = parse_resume(file_path)

    timeline = build_timeline(parsed)
    gaps = detect_gaps(timeline)

    return templates.TemplateResponse(
        "review.html",
        {
            "request": request,
            "file_id": file_id,
            "identity": parsed.get("identity"),
            "skills": parsed.get("skills"),
            "education": parsed.get("education"),
            "employment": parsed.get("employment"),
            "gaps": gaps,
        },
    )


# ================= GENERATE =================
@app.post("/generate")
async def generate_resume_endpoint(request: Request):
    form = await request.form()
    file_id = form.get("file_id")
    target_role = form.get("target_role")

    # find uploaded file
    file_path = next(
        (os.path.join(UPLOAD_DIR, f) for f in os.listdir(UPLOAD_DIR) if f.startswith(file_id)),
        None
    )

    parsed = parse_resume(file_path)

    # Collect gap experience
    additional_experience = []

    for key in form.keys():
        if key.startswith("fill_gap_") and form.get(key) == "yes":
            idx = key.split("_")[-1]

            additional_experience.append({
                "company": form.get(f"company_{idx}"),
                "role": form.get(f"role_{idx}"),
                "location": form.get(f"location_{idx}"),
                "start": form.get(f"start_{idx}"),
                "end": form.get(f"end_{idx}"),
            })

    final_resume = generate_resume(
        target_role=target_role,
        original_resume=parsed,
        education=parsed.get("education"),
        employment=parsed.get("employment"),
        additional_experience=additional_experience,
    )

    filename = f"{parsed['identity']['name'].replace(' ', '_')}_ATS_Resume.docx"
    export_to_word(final_resume, filename)

    return FileResponse(filename, filename=filename)
