# Resume AI - Copilot Instructions

## Project Overview
Resume AI is a dual-interface resume optimization system (FastAPI web + CLI) that uses OpenAI GPT-4.1 to generate ATS-optimized resumes. It analyzes employment gaps, extracts candidate identity, and exports optimized documents to DOCX format.

## Architecture & Data Flow

### Multi-Stage Pipeline
```
File Upload → Text Extraction → Parse Resume → Gap Detection → 
Resume Generation → ATS Scoring → Export (DOCX)
```

### Core Components

| Module | Purpose | Key Pattern |
|--------|---------|------------|
| [resume_parser.py](resume_parser.py) | Multi-format text extraction (PDF/DOCX/TXT) + structured parsing | **LLM-based**: Use GPT-4.1 with temperature=0 for deterministic JSON parsing |
| [resume_optimizer.py](resume_optimizer.py) | Generate ATS-optimized resume content | **System prompts crucial**: Embed "STRICT RULES" to prevent fabrication |
| [gap_analyzer.py](gap_analyzer.py) | Detect employment/education gaps in timeline | Year-parsing extraction from free text fields |
| [ats_scorer.py](ats_scorer.py) | Calculate ATS score (0-10) using weighted factors | Keyword matching (30%) + structure (15%) + metrics presence (10%) |
| [exporter.py](exporter.py) | Convert resume text to DOCX | Simple line-by-line paragraph creation |

### Entry Points
- **Web**: [app.py](app.py) - FastAPI with POST `/generate` endpoint, file upload to `uploads/` directory
- **CLI**: [run.py](run.py) - Interactive tkinter file picker + console I/O for gap resolution

## Critical Development Patterns

### 1. LLM Integration (OpenAI API)
- **Always use system prompts** to constrain behavior (see [resume_optimizer.py](resume_optimizer.py) SYSTEM_PROMPT)
- **Temperature settings matter**:
  - `temperature=0` for parsing (extract_identity, parse_resume) → deterministic
  - `temperature=0.2` for generation → slight creativity without hallucination
- **Extract function calls JSON directly** from `response.choices[0].message.content`
- **Error handling**: Resume parsing can fail silently—return empty dicts `{"education": [], "employment": []}`

### 2. File Handling
- **Multi-format support**: .txt, .docx, .pdf (using python-docx, PyPDF2)
- **Encoding safety**: Use `encoding="utf-8", errors="ignore"` for text files
- **Web uploads**: Store as `{uuid}_{original_filename}` in `uploads/` directory
- **Identity extraction**: First line = name, regex for email/phone (basic but functional)

### 3. Data Structure Conventions
Resume data from LLM is **always returned as structured JSON**:
```python
{
  "education": [{"degree": "", "field": "", "start_year": "", "end_year": ""}],
  "employment": [{"company": "", "role": "", "start_date": "", "end_date": ""}]
}
```
Year/date parsing: Extract first 4 characters to int, fallback to current year for ongoing roles.

### 4. CLI Output Conventions
Use emoji prefixes for user feedback (see [run.py](run.py)):
- `✅` Success/completion
- `❌` Error/failure
- `⚠️` Warning/user input required

### 5. ATS Scoring Calculation
[ats_scorer.py](ats_scorer.py) implements weighted scoring (not used in resume_optimizer.py, but illustrates scoring logic):
- Keyword relevancy (30%)
- Skills section presence (20%)
- Resume structure completeness (15%)
- Experience alignment (15%)
- Metrics/quantification (10%)
- ATS-safe formatting (10%)

Role keywords hardcoded in `ROLE_KEYWORDS` dict—expand per job family as needed.

## Project-Specific Conventions

### API/Response Handling
- Web endpoint returns `FileResponse` for downloads or JSON error: `{"error": "message"}`
- No explicit validation on form inputs—sanitize input before LLM calls
- File IDs use `uuid.uuid4()` for uniqueness (sufficient for free tier)

### External Dependencies
- **FastAPI + Uvicorn**: Web framework; deploy via `uvicorn app:app --host 0.0.0.0`
- **OpenAI API**: Requires `OPENAI_API_KEY` env variable (no fallback if missing)
- **python-docx**: Document creation (not formatting—simple text import)
- **PyPDF2**: PDF extraction (may fail on scanned/image PDFs)

### Workflow Differences (Web vs CLI)
- **Web**: Single-pass optimization (no gap filling UI)
- **CLI**: Multi-step with user prompts to fill gaps (see [gap_resolver.py](gap_resolver.py))
- Web uses `add_projects` form parameter but **doesn't implement** gap filling—potential extension point

## Common Pitfalls & Solutions

| Issue | Root Cause | Solution |
|-------|-----------|----------|
| Resume parsing fails silently | Scanned/image PDF, no OCR | Test with text-based PDFs; add error message |
| LLM fabricates companies | Weak system prompt constraints | Review STRICT RULES in [resume_optimizer.py](resume_optimizer.py); add explicit guardrails |
| Identity extraction fails | Resume doesn't have email/phone | Make fields optional; don't require all three |
| Gap detection misses years | Free-form date format | Improve parse_year() to handle "Jan 2020", "2020-2021" ranges |
| DOCX export lacks formatting | Simple line-by-line approach | Use python-docx style/font APIs if rich formatting needed |

## Testing & Deployment

### Local Development
```bash
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."
uvicorn app:app --reload  # Web: http://localhost:8000
python run.py              # CLI: interactive mode
```

### Deployment
- [render.yaml](render.yaml) specifies Render.com free tier: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- Ensure `OPENAI_API_KEY` set as env secret in Render dashboard
- `uploads/` directory should be writable; may need persistent volume on production

## Extension Points

1. **Gap Resolution UI**: Extend [app.py](app.py) POST `/generate` to store gaps, add UI form for filling them
2. **ATS Scoring in Web**: Integrate [ats_scorer.py](ats_scorer.py) into response; currently only returns resume text + score appended
3. **More LLM Models**: Abstract client.chat.completions.create() to support Claude, Gemini (temperature/prompt parity matters)
4. **Resume Formatting**: Enhance [exporter.py](exporter.py) to create styled sections (bold headers, bullet lists via python-docx)
5. **Batch Processing**: CLI could accept multiple resume files; web could queue jobs async with celery/rq
