from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from collections import defaultdict

from database import get_db, Expense, Invoice

router = APIRouter()


@router.get("/")
def get_dashboard(db: Session = Depends(get_db)):
    # ── Expenses ──────────────────────────────────────────
    expenses = db.query(Expense).filter(Expense.review_status == "confirmed").all()

    total_expenses = sum(e.amount for e in expenses)

    category_breakdown: dict[str, float] = defaultdict(float)
    monthly_expenses: dict[str, float] = defaultdict(float)
    for e in expenses:
        category_breakdown[e.category] += e.amount
        month_key = e.date.strftime("%Y-%m") if isinstance(e.date, date) else str(e.date)[:7]
        monthly_expenses[month_key] += e.amount

    # ── Invoices ──────────────────────────────────────────
    invoices = db.query(Invoice).all()
    today = date.today()

    total_income = 0.0
    unpaid_count = 0
    overdue_count = 0
    monthly_income: dict[str, float] = defaultdict(float)

    for inv in invoices:
        due = inv.due_date if isinstance(inv.due_date, date) else date.fromisoformat(str(inv.due_date))
        if inv.status == "paid":
            total_income += inv.amount
            month_key = inv.issue_date.strftime("%Y-%m") if isinstance(inv.issue_date, date) else str(inv.issue_date)[:7]
            monthly_income[month_key] += inv.amount
        elif inv.status == "unpaid":
            if due < today:
                overdue_count += 1
            else:
                unpaid_count += 1

    # ── Monthly trend (merge income + expenses) ───────────
    all_months = sorted(set(list(monthly_expenses.keys()) + list(monthly_income.keys())))
    monthly_trend = [
        {
            "month": m,
            "expenses": round(monthly_expenses.get(m, 0), 2),
            "income": round(monthly_income.get(m, 0), 2),
        }
        for m in all_months
    ]

    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_cash_flow": round(total_income - total_expenses, 2),
        "category_breakdown": {k: round(v, 2) for k, v in category_breakdown.items()},
        "monthly_trend": monthly_trend,
        "invoice_summary": {
            "total": len(invoices),
            "unpaid": unpaid_count,
            "overdue": overdue_count,
        },
    }
