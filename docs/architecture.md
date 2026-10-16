# Architecture

## Data Flow

```
Receipt / Invoice Upload (PDF, PNG, JPG)
        ↓
Document Processing
  - PDF: pdfplumber text extraction
  - Image: Tesseract OCR
        ↓
Local AI via Ollama + Gemma
  - Structured JSON extraction (merchant, date, amount, currency, category)
        ↓
Validation + Human Review
  - Editable form, date/amount checks, duplicate detection
        ↓
SQLite Database
        ↓
Dashboard + Reports + CSV Export
```

## Components

| Layer | Technology |
|-------|-----------|
| Frontend | Vite + React + TailwindCSS |
| Backend API | Python FastAPI |
| OCR | Tesseract |
| AI Inference | Ollama + Gemma (local) |
| Database | SQLite via SQLAlchemy |

## Privacy Model

In the local-first edition, all processing stays on the user's machine:
- Uploaded files are stored locally in `backend/uploads/`
- OCR and AI inference run via local Ollama instance
- SQLite database is a local file (`freelanceflow.db`)
- No telemetry or receipt data is sent to external servers
