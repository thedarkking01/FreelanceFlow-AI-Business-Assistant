from fastapi import APIRouter

router = APIRouter()


@router.get("/monthly")
def monthly_report(month: str = "2026-10"):
    # Phase 5: AI-generated monthly summary
    return {"month": month, "summary": "Monthly report — coming in Phase 5"}


@router.get("/export")
def export_csv(month: str = "2026-10"):
    # Phase 5: CSV export
    return {"message": "CSV export — coming in Phase 5"}
