from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok", "product": "Giraffe JP — Merchant-Owned C-B-M Backend Package"}
