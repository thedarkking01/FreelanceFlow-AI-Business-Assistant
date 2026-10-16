from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_dashboard():
    # Phase 3: Return totals, category breakdown, monthly trend
    return {
        "total_income": 0,
        "total_expenses": 0,
        "net_cash_flow": 0,
        "category_breakdown": {},
        "monthly_trend": [],
    }
