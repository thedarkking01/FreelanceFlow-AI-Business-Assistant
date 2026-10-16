from fastapi import APIRouter

router = APIRouter()


@router.post("/upload")
def upload_receipt():
    # Phase 2: OCR + AI extraction
    return {"message": "Receipt upload — coming in Phase 2"}


@router.post("/confirm")
def confirm_receipt():
    # Phase 2: Save confirmed expense to DB
    return {"message": "Confirm receipt — coming in Phase 2"}


@router.get("/")
def list_expenses():
    # Phase 3: Return paginated expense list
    return {"expenses": []}
