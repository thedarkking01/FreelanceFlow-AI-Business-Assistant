import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import date

from database import get_db, Expense
from models import ExpenseCreate, ExpenseOut
from services.ocr import extract_text
from services.ai_extractor import extract_receipt_fields
from services.categorizer import suggest_category

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}


@router.post("/upload")
async def upload_receipt(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use JPG, PNG, or PDF.")

    ext = os.path.splitext(file.filename or "receipt")[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    raw_text = extract_text(file_path, file.content_type)

    if not raw_text:
        return {
            "merchant": "", "date": str(date.today()), "amount": None,
            "currency": "INR", "category": "Other", "tax": None,
            "review_status": "needs_review", "receipt_path": filename,
            "raw_text": "",
        }

    extracted = extract_receipt_fields(raw_text)

    # Override category with keyword-based suggestion if AI returned "Other"
    if extracted["category"] == "Other":
        extracted["category"] = suggest_category(extracted.get("merchant", ""), raw_text)

    extracted["receipt_path"] = filename
    return extracted


@router.post("/confirm", response_model=ExpenseOut)
def confirm_receipt(expense: ExpenseCreate, db: Session = Depends(get_db)):
    # Duplicate check: same merchant + date + amount
    existing = db.query(Expense).filter(
        Expense.merchant == expense.merchant,
        Expense.date == expense.date,
        Expense.amount == expense.amount,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Duplicate expense detected.")

    db_expense = Expense(**expense.model_dump())
    db_expense.review_status = "confirmed"
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return _serialize(db_expense)


@router.get("/")
def list_expenses(db: Session = Depends(get_db)):
    expenses = db.query(Expense).order_by(Expense.date.desc()).all()
    return {"expenses": [_serialize(e) for e in expenses]}


def _serialize(e: Expense) -> dict:
    return {
        "id": e.id,
        "merchant": e.merchant,
        "date": str(e.date),
        "amount": e.amount,
        "currency": e.currency,
        "category": e.category,
        "tax": e.tax,
        "receipt_path": e.receipt_path,
        "review_status": e.review_status,
        "created_at": str(e.created_at),
    }
