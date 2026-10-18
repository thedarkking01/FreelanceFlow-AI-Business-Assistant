from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from database import get_db, Invoice
from models import InvoiceCreate

router = APIRouter()


def _serialize(inv: Invoice, today: date) -> dict:
    due = inv.due_date if isinstance(inv.due_date, date) else date.fromisoformat(str(inv.due_date))
    # Auto-escalate unpaid past due_date to overdue
    status = inv.status
    if status == "unpaid" and due < today:
        status = "overdue"
    return {
        "id": inv.id,
        "invoice_number": inv.invoice_number,
        "client": inv.client,
        "amount": inv.amount,
        "currency": inv.currency,
        "issue_date": str(inv.issue_date),
        "due_date": str(inv.due_date),
        "status": status,
        "created_at": str(inv.created_at),
    }


@router.get("/")
def list_invoices(db: Session = Depends(get_db)):
    today = date.today()
    invoices = db.query(Invoice).order_by(Invoice.due_date.asc()).all()
    return {"invoices": [_serialize(i, today) for i in invoices]}


@router.post("/", status_code=201)
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db)):
    if payload.due_date < payload.issue_date:
        raise HTTPException(status_code=400, detail="due_date cannot be before issue_date.")
    existing = db.query(Invoice).filter(Invoice.invoice_number == payload.invoice_number).first()
    if existing:
        raise HTTPException(status_code=409, detail="Invoice number already exists.")
    inv = Invoice(**payload.model_dump())
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return _serialize(inv, date.today())


@router.patch("/{invoice_id}")
def update_invoice(invoice_id: int, payload: dict, db: Session = Depends(get_db)):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    allowed = {"status", "amount", "due_date", "client"}
    for key, val in payload.items():
        if key in allowed:
            setattr(inv, key, val)
    db.commit()
    db.refresh(inv)
    return _serialize(inv, date.today())


@router.delete("/{invoice_id}", status_code=204)
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    db.delete(inv)
    db.commit()
