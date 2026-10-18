"""
Seed the database with sample transactions and invoices for demo/testing.
Run from the backend directory:
    python seed.py
"""
import sys
import os
import csv
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from database import init_db, SessionLocal, Expense, Invoice

SAMPLE_CSV = os.path.join(os.path.dirname(__file__), "..", "sample_data", "sample_transactions.csv")

SAMPLE_INVOICES = [
    {"invoice_number": "INV-2026-001", "client": "Acme Corp",      "amount": 25000.0, "issue_date": "2026-10-01", "due_date": "2026-10-31", "status": "paid"},
    {"invoice_number": "INV-2026-002", "client": "Beta Startup",   "amount": 15000.0, "issue_date": "2026-10-05", "due_date": "2026-11-05", "status": "unpaid"},
    {"invoice_number": "INV-2026-003", "client": "Gamma Solutions", "amount": 8000.0,  "issue_date": "2026-09-01", "due_date": "2026-09-30", "status": "unpaid"},
]


def seed():
    init_db()
    db = SessionLocal()

    try:
        # ── Expenses from CSV ──────────────────────────────
        if not db.query(Expense).first():
            with open(SAMPLE_CSV, newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    db.add(Expense(
                        merchant=row["merchant"],
                        date=date.fromisoformat(row["date"]),
                        amount=float(row["amount"]),
                        currency=row["currency"],
                        category=row["category"],
                        tax=float(row["tax"]) if row["tax"] else None,
                        review_status=row["review_status"],
                    ))
            print(f"[OK] Seeded expenses from {SAMPLE_CSV}")
        else:
            print("  Expenses already exist — skipping.")

        # ── Invoices ──────────────────────────────────────
        if not db.query(Invoice).first():
            for inv in SAMPLE_INVOICES:
                db.add(Invoice(
                    invoice_number=inv["invoice_number"],
                    client=inv["client"],
                    amount=inv["amount"],
                    issue_date=date.fromisoformat(inv["issue_date"]),
                    due_date=date.fromisoformat(inv["due_date"]),
                    status=inv["status"],
                ))
            print(f"[OK] Seeded {len(SAMPLE_INVOICES)} sample invoices.")
        else:
            print("  Invoices already exist — skipping.")

        db.commit()
        print("[OK] Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
