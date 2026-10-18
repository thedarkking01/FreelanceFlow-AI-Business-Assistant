import sys
import os
from datetime import date
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


# ── Pure aggregation logic (mirrors dashboard.py) ─────────

def _compute_totals(expenses, invoices, today=None):
    today = today or date.today()
    total_expenses = sum(e["amount"] for e in expenses)

    category_breakdown = defaultdict(float)
    for e in expenses:
        category_breakdown[e["category"]] += e["amount"]

    total_income = 0.0
    unpaid = overdue = 0
    for inv in invoices:
        due = date.fromisoformat(inv["due_date"])
        if inv["status"] == "paid":
            total_income += inv["amount"]
        elif inv["status"] == "unpaid":
            if due < today:
                overdue += 1
            else:
                unpaid += 1

    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net": round(total_income - total_expenses, 2),
        "category_breakdown": dict(category_breakdown),
        "unpaid": unpaid,
        "overdue": overdue,
    }


# ── Tests ─────────────────────────────────────────────────

SAMPLE_EXPENSES = [
    {"amount": 2499.0, "category": "Software"},
    {"amount": 999.0,  "category": "Software"},
    {"amount": 450.0,  "category": "Office Supplies"},
    {"amount": 320.0,  "category": "Travel"},
    {"amount": 180.0,  "category": "Food"},
    {"amount": 1699.0, "category": "Software"},
    {"amount": 275.0,  "category": "Office Supplies"},
    {"amount": 3500.0, "category": "Marketing"},
]

SAMPLE_INVOICES = [
    {"amount": 25000.0, "status": "paid",   "due_date": "2026-10-15"},
    {"amount": 15000.0, "status": "unpaid", "due_date": "2026-11-30"},
    {"amount": 8000.0,  "status": "unpaid", "due_date": "2026-09-01"},  # overdue
]


def test_total_expenses():
    result = _compute_totals(SAMPLE_EXPENSES, [])
    assert result["total_expenses"] == 9922.0


def test_total_income_paid_only():
    result = _compute_totals([], SAMPLE_INVOICES)
    assert result["total_income"] == 25000.0


def test_net_cash_flow():
    result = _compute_totals(SAMPLE_EXPENSES, SAMPLE_INVOICES)
    assert result["net"] == round(25000.0 - 9922.0, 2)


def test_category_breakdown():
    result = _compute_totals(SAMPLE_EXPENSES, [])
    assert result["category_breakdown"]["Software"] == 2499.0 + 999.0 + 1699.0
    assert result["category_breakdown"]["Marketing"] == 3500.0
    assert result["category_breakdown"]["Office Supplies"] == 450.0 + 275.0


def test_overdue_detection():
    today = date(2026, 10, 16)
    result = _compute_totals([], SAMPLE_INVOICES, today=today)
    assert result["overdue"] == 1
    assert result["unpaid"] == 1


def test_all_paid_no_overdue():
    invoices = [{"amount": 1000.0, "status": "paid", "due_date": "2026-10-01"}]
    result = _compute_totals([], invoices)
    assert result["overdue"] == 0
    assert result["unpaid"] == 0


def test_empty_data():
    result = _compute_totals([], [])
    assert result["total_expenses"] == 0
    assert result["total_income"] == 0
    assert result["net"] == 0
