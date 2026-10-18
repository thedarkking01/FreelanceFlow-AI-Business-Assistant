# FreelanceFlow — AI Business Assistant

> A local-first AI receipt and expense manager for freelancers.  
> Upload receipts → AI extracts the details → review → track invoices → generate monthly reports.  
> Everything runs on your machine. No data leaves your device.

Built for the **Hacktoberfest 2026 Open-Source AI Challenge**.

---

## Features

| Feature | Description |
|---------|-------------|
| Smart Receipt Scanner | Upload JPG, PNG, or PDF — OCR + Gemma extracts merchant, date, amount, category |
| Human-in-the-loop Review | AI suggestions are editable before saving — no blind trust in model output |
| AI Expense Categorization | Software, Hardware, Travel, Food, Office Supplies, Marketing, Other |
| Financial Dashboard | Income, expenses, net cash flow, category pie chart, monthly bar chart |
| Invoice Tracker | Record invoices, auto-detect overdue, mark as paid, delete |
| Monthly Report Generator | AI-written summary + CSV export — fallback summary if Ollama is offline |
| Privacy by Design | All OCR, AI inference, and storage happen locally — zero telemetry |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vite + React + TailwindCSS + Recharts |
| Backend | Python FastAPI |
| AI Inference | Ollama + Gemma 3 (local) |
| OCR | Tesseract + pdfplumber |
| Database | SQLite via SQLAlchemy |

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) installed
- [Ollama](https://ollama.com) installed and running

### 1. Pull the AI model

```bash
ollama pull gemma3:4b
ollama serve
```

### 2. Backend

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate        # Windows PowerShell
pip install -r requirements.txt
python seed.py                 # optional: load sample data
uvicorn main:app --reload
```

Backend runs on http://localhost:8000  
API docs at http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:5173

### Tesseract path (Windows)

If Tesseract is not on your PATH, uncomment and set this line in `backend/services/ocr.py`:

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

---

## Project Structure

```
freelanceflow/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # SQLAlchemy models + DB init
│   ├── models.py            # Pydantic schemas + validation
│   ├── seed.py              # Sample data loader
│   ├── requirements.txt
│   ├── routes/
│   │   ├── receipts.py      # Upload, OCR, confirm
│   │   ├── invoices.py      # Invoice CRUD
│   │   ├── dashboard.py     # Financial aggregations
│   │   └── reports.py       # Monthly summary + CSV export
│   └── services/
│       ├── ocr.py           # Tesseract + pdfplumber
│       ├── ai_extractor.py  # Ollama + Gemma structured extraction
│       └── categorizer.py   # Keyword-based category fallback
├── frontend/
│   └── src/
│       ├── pages/           # Dashboard, Receipts, Invoices, Reports
│       ├── components/      # Sidebar
│       └── api/             # Axios API client
├── tests/
│   ├── test_validators.py   # Pydantic model validation (13 tests)
│   ├── test_reports.py      # CSV + summary logic (7 tests)
│   └── test_dashboard.py    # Financial aggregation math (7 tests)
├── sample_data/
│   └── sample_transactions.csv
└── docs/
    └── architecture.md
```

---

## Running Tests

```bash
cd backend
.\venv\Scripts\activate
python -m pytest ..\tests\ -v
```

23 tests — validators, financial calculations, report logic.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/receipts/upload` | Upload receipt file → OCR + AI extraction |
| POST | `/receipts/confirm` | Save confirmed expense to DB |
| GET | `/receipts` | List all expenses |
| GET | `/invoices` | List all invoices |
| POST | `/invoices` | Create invoice |
| PATCH | `/invoices/:id` | Update invoice |
| DELETE | `/invoices/:id` | Delete invoice |
| GET | `/dashboard` | Financial summary + charts data |
| GET | `/reports/monthly?month=2026-10` | AI monthly summary |
| GET | `/reports/export?month=2026-10` | Download CSV |

---

## Privacy

- Uploaded files are stored in `backend/uploads/` on your machine
- OCR runs locally via Tesseract
- AI inference runs locally via Ollama — no API keys, no cloud calls
- SQLite database is a local file (`backend/freelanceflow.db`)
- No analytics, no telemetry, no external requests (except to `localhost:11434`)

---

## License

MIT
