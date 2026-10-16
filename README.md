# FreelanceFlow — AI Business Assistant

A local-first AI receipt and expense manager for freelancers. Upload receipts, let AI extract the details, track invoices, and generate monthly financial reports — all running on your machine.

## Tech Stack

- **Frontend**: Vite + React + TailwindCSS
- **Backend**: Python FastAPI
- **AI**: Ollama + Gemma (local inference)
- **OCR**: Tesseract
- **Database**: SQLite

## Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Backend runs on http://localhost:8000  
Frontend runs on http://localhost:5173

## Project Structure

```
freelanceflow/
├── frontend/        # Vite + React
├── backend/         # FastAPI + SQLite
├── tests/           # Validation and report tests
├── sample_data/     # Synthetic sample transactions
└── docs/            # Architecture and screenshots
```

## Features

- Smart receipt scanner (OCR + AI extraction)
- AI expense categorization
- Financial dashboard
- Invoice tracker
- Monthly report generator + CSV export

## Privacy

All document processing, AI inference, and data storage happen locally on your machine. No receipt data is uploaded to external servers.

## License

MIT
