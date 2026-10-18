import io
import csv
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from routes.reports import _filter_by_month, _generate_ai_summary


# ── _filter_by_month ──────────────────────────────────────

class _FakeExpense:
    def __init__(self, date_str):
        self.date = date_str


def test_filter_by_month_matches():
    items = [_FakeExpense("2026-10-01"), _FakeExpense("2026-10-15"), _FakeExpense("2026-11-01")]
    result = _filter_by_month(items, "2026-10", "date")
    assert len(result) == 2


def test_filter_by_month_empty():
    items = [_FakeExpense("2026-09-01")]
    result = _filter_by_month(items, "2026-10", "date")
    assert result == []


def test_filter_by_month_all_match():
    items = [_FakeExpense("2026-10-01"), _FakeExpense("2026-10-31")]
    result = _filter_by_month(items, "2026-10", "date")
    assert len(result) == 2


# ── _generate_ai_summary fallback ────────────────────────

def test_summary_fallback_no_overdue():
    summary = _generate_ai_summary("2026-10", 50000.0, 9922.0, [("Software", 5197.0), ("Marketing", 3500.0)], 0)
    assert "2026-10" in summary
    assert "50,000" in summary
    assert "Software" in summary
    assert "overdue" not in summary.lower()


def test_summary_fallback_with_overdue():
    summary = _generate_ai_summary("2026-10", 0.0, 1000.0, [], 2)
    assert "2" in summary
    assert "overdue" in summary.lower()


def test_summary_positive_net():
    summary = _generate_ai_summary("2026-10", 10000.0, 5000.0, [], 0)
    assert "5,000" in summary


# ── CSV structure ─────────────────────────────────────────

def test_csv_headers():
    expected = ["id", "merchant", "date", "amount", "currency", "category", "tax", "review_status"]
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(expected)
    buf.seek(0)
    reader = csv.reader(buf)
    headers = next(reader)
    assert headers == expected
