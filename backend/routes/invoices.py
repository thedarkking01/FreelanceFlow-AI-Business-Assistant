from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_invoices():
    # Phase 4: Return all invoices
    return {"invoices": []}


@router.post("/")
def create_invoice():
    # Phase 4: Create invoice
    return {"message": "Create invoice — coming in Phase 4"}


@router.patch("/{invoice_id}")
def update_invoice(invoice_id: int):
    # Phase 4: Update invoice status
    return {"message": f"Update invoice {invoice_id} — coming in Phase 4"}
