from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date


# ── Expense ──────────────────────────────────────────────
class ExpenseCreate(BaseModel):
    merchant: str
    date: date
    amount: float
    currency: str = "INR"
    category: str = "Other"
    tax: Optional[float] = None
    receipt_path: Optional[str] = None
    review_status: str = "needs_review"

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v

    @field_validator("category")
    @classmethod
    def valid_category(cls, v):
        allowed = {"Software", "Hardware", "Travel", "Food", "Office Supplies", "Marketing", "Other"}
        if v not in allowed:
            raise ValueError(f"Category must be one of {allowed}")
        return v


class ExpenseOut(ExpenseCreate):
    id: int
    created_at: str

    class Config:
        from_attributes = True


# ── Invoice ───────────────────────────────────────────────
class InvoiceCreate(BaseModel):
    invoice_number: str
    client: str
    amount: float
    currency: str = "INR"
    issue_date: date
    due_date: date
    status: str = "unpaid"

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v

    @field_validator("status")
    @classmethod
    def valid_status(cls, v):
        if v not in {"paid", "unpaid", "overdue"}:
            raise ValueError("Status must be paid, unpaid, or overdue")
        return v


class InvoiceOut(InvoiceCreate):
    id: int
    created_at: str

    class Config:
        from_attributes = True
