import csv
import io
import httpx
import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date
from collections import defaultdict

from database import get_db, Expense, Invoice

router = APIRouter()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:4b"


def _expenses_for_month(db: Session, month: str) -> list[Expense]:
    year, mon = int(month[:4]), int(month[5:7])
    return (
        db.query(Expense)
        .filter(Expense.review_status == "confirmed")
        .all()
    )


def _filter_by_month(items, month: str, date_attr: str) -> list:
    prefix = month[:7]
    return [i for i in items if str(getattr(i, date_attr))[:7] == prefix]


@router.get("/monthly")
def monthly_report(month: str = "2026-10", db: Session = Depends(get_db)):
    expenses = _filter_by_month(
        db.query(Expense).filter(Expense.review_status == "confirmed").all(),
        month, "date"
    )
    invoices = _filter_by_month(db.query(Invoice).all(), month, "issue_date")

    total_expenses = sum(e.amount for e in expenses)
    total_income = sum(i.amount for i in invoices if i.status == "paid")
    overdue = [i for i in db.query(Invoice).all() if i.status in ("unpaid", "overdue") and str(i.due_date)[:7] <= month]

    category_totals: dict[str, float] = defaultdict(float)
    for e in expenses:
        category_totals[e.category] += e.amount
    top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:3]

    summary = _generate_ai_summary(month, total_income, total_expenses, top_categories, len(overdue))

    return {
        "month": month,
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net": round(total_income - total_expenses, 2),
        "top_categories": [{"category": c, "amount": round(a, 2)} for c, a in top_categories],
        "overdue_count": len(overdue),
        "expense_count": len(expenses),
        "summary": summary,
    }


@router.get("/export")
def export_csv(month: str = "2026-10", db: Session = Depends(get_db)):
    expenses = _filter_by_month(
        db.query(Expense).filter(Expense.review_status == "confirmed").all(),
        month, "date"
    )

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "merchant", "date", "amount", "currency", "category", "tax", "review_status"])
    for e in expenses:
        writer.writerow([e.id, e.merchant, e.date, e.amount, e.currency, e.category, e.tax or "", e.review_status])

    buf.seek(0)
    filename = f"freelanceflow_{month}.csv"
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def _generate_ai_summary(month: str, income: float, expenses: float, top_cats: list, overdue: int) -> str:
    net = income - expenses
    prompt = f"""You are a financial assistant. Write a concise 3-4 sentence monthly summary for a freelancer.

Month: {month}
Total Income: ₹{income:,.2f}
Total Expenses: ₹{expenses:,.2f}
Net Cash Flow: ₹{net:,.2f}
Top Expense Categories: {', '.join(f'{c} (₹{a:,.0f})' for c, a in top_cats) or 'None'}
Overdue Invoices: {overdue}

Write a professional, helpful summary. Mention the net position, biggest spending areas, and any overdue invoice concern."""

    try:
        response = httpx.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False},
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception:
        # Fallback: rule-based summary when Ollama is unavailable
        lines = [f"In {month}, total income was ₹{income:,.2f} and total expenses were ₹{expenses:,.2f}, resulting in a net cash flow of ₹{net:,.2f}."]
        if top_cats:
            lines.append(f"The biggest spending categories were {', '.join(c for c, _ in top_cats)}.")
        if overdue:
            lines.append(f"There {'is' if overdue == 1 else 'are'} {overdue} overdue invoice{'s' if overdue > 1 else ''} that require attention.")
        return " ".join(lines)
