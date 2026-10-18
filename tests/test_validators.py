import pytest
from datetime import date
from pydantic import ValidationError
from models import ExpenseCreate, InvoiceCreate


# ── ExpenseCreate ─────────────────────────────────────────

def test_expense_valid():
    e = ExpenseCreate(merchant="Acme", date=date(2026, 10, 1), amount=500.0)
    assert e.merchant == "Acme"
    assert e.currency == "INR"
    assert e.category == "Other"
    assert e.review_status == "needs_review"


def test_expense_negative_amount():
    with pytest.raises(ValidationError):
        ExpenseCreate(merchant="Acme", date=date(2026, 10, 1), amount=-100.0)


def test_expense_zero_amount():
    with pytest.raises(ValidationError):
        ExpenseCreate(merchant="Acme", date=date(2026, 10, 1), amount=0)


def test_expense_invalid_category():
    with pytest.raises(ValidationError):
        ExpenseCreate(merchant="Acme", date=date(2026, 10, 1), amount=100.0, category="Groceries")


def test_expense_valid_categories():
    for cat in ["Software", "Hardware", "Travel", "Food", "Office Supplies", "Marketing", "Other"]:
        e = ExpenseCreate(merchant="X", date=date(2026, 10, 1), amount=1.0, category=cat)
        assert e.category == cat


# ── InvoiceCreate ─────────────────────────────────────────

def test_invoice_valid():
    inv = InvoiceCreate(
        invoice_number="INV-001", client="Client A", amount=10000.0,
        issue_date=date(2026, 10, 1), due_date=date(2026, 10, 31),
    )
    assert inv.status == "unpaid"
    assert inv.currency == "INR"


def test_invoice_negative_amount():
    with pytest.raises(ValidationError):
        InvoiceCreate(
            invoice_number="INV-002", client="Client B", amount=-500.0,
            issue_date=date(2026, 10, 1), due_date=date(2026, 10, 31),
        )


def test_invoice_invalid_status():
    with pytest.raises(ValidationError):
        InvoiceCreate(
            invoice_number="INV-003", client="Client C", amount=100.0,
            issue_date=date(2026, 10, 1), due_date=date(2026, 10, 31),
            status="pending",
        )


def test_invoice_valid_statuses():
    for status in ["paid", "unpaid", "overdue"]:
        inv = InvoiceCreate(
            invoice_number=f"INV-{status}", client="X", amount=1.0,
            issue_date=date(2026, 10, 1), due_date=date(2026, 10, 31),
            status=status,
        )
        assert inv.status == status
