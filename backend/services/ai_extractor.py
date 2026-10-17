import httpx
import json
from datetime import date

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:4b"

SCHEMA = {
    "merchant": "string (company or store name)",
    "date": "string in YYYY-MM-DD format",
    "amount": "number (total amount paid)",
    "currency": "string (INR, USD, EUR, etc.)",
    "category": "one of: Software, Hardware, Travel, Food, Office Supplies, Marketing, Other",
    "tax": "number or null",
}

PROMPT_TEMPLATE = """You are a receipt data extractor. Extract the following fields from the receipt text below and return ONLY a valid JSON object with no extra text.

Fields to extract:
- merchant: company or store name
- date: transaction date in YYYY-MM-DD format
- amount: total amount as a number (no currency symbols)
- currency: currency code (INR, USD, EUR, etc.)
- category: one of [Software, Hardware, Travel, Food, Office Supplies, Marketing, Other]
- tax: tax amount as a number, or null if not shown

Receipt text:
{text}

Return only JSON, no explanation."""


def extract_receipt_fields(raw_text: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(text=raw_text[:3000])

    try:
        response = httpx.post(
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": False, "format": "json"},
            timeout=60.0,
        )
        response.raise_for_status()
        raw = response.json().get("response", "{}")
        data = json.loads(raw)
    except (httpx.RequestError, httpx.HTTPStatusError):
        # Ollama not running — return empty scaffold for manual entry
        data = {}
    except json.JSONDecodeError:
        data = {}

    return {
        "merchant": data.get("merchant", ""),
        "date": _safe_date(data.get("date", "")),
        "amount": _safe_float(data.get("amount")),
        "currency": data.get("currency", "INR"),
        "category": _safe_category(data.get("category", "Other")),
        "tax": _safe_float(data.get("tax")),
        "review_status": "needs_review",
    }


VALID_CATEGORIES = {"Software", "Hardware", "Travel", "Food", "Office Supplies", "Marketing", "Other"}


def _safe_date(val: str) -> str:
    try:
        date.fromisoformat(str(val))
        return str(val)
    except Exception:
        return str(date.today())


def _safe_float(val) -> float | None:
    try:
        f = float(val)
        return f if f > 0 else None
    except (TypeError, ValueError):
        return None


def _safe_category(val: str) -> str:
    return val if val in VALID_CATEGORIES else "Other"
