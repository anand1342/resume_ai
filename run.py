from resume_parser import parse_resume
from gap_analyzer import build_timeline, detect_gaps
from gap_resolver import resolve_gaps
from resume_optimizer import generate_resume
from exporter import export_to_word
from docx import Document
from pypdf import PdfReader
import tkinter as tk
from tkinter import filedialog
import os

print("\n===== AI RESUME BUILDER =====\n")

target_role = input("Enter Target Job Title: ").strip()

root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)

resume_path = filedialog.askopenfilename(
    title="Upload Resume",
    filetypes=[("All Supported Files", "*.txt *.doc *.docx *.pdf")]
)

if not resume_path:
    print("❌ No file selected.")
    exit()

ext = os.path.splitext(resume_path)[1].lower()

if ext == ".txt":
    original_resume = open(resume_path, encoding="utf-8", errors="ignore").read()
elif ext in [".doc", ".docx"]:
    doc = Document(resume_path)
    original_resume = "\n".join(p.text for p in doc.paragraphs)
elif ext == ".pdf":
    reader = PdfReader(resume_path)
    original_resume = "\n".join(p.extract_text() or "" for p in reader.pages)
else:
    print("Unsupported file.")
    exit()

parsed = parse_resume(original_resume)
timeline = build_timeline(parsed)
gaps = detect_gaps(timeline)

additional_experience = resolve_gaps(gaps)

final_resume = generate_resume(
    target_role,
    original_resume,
    parsed["education"],
    parsed["employment"],
    additional_experience
)

export_to_word(final_resume, "Final_ATS_Resume.docx")

print("\n✅ Resume Generated")
print("Saved as: Final_ATS_Resume.docx\n")
print(final_resume)
