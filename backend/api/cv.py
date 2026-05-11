from fastapi import APIRouter

router = APIRouter(prefix="/cv", tags=["Lebenslauf"])


@router.post("/upload")
async def upload_cv():
    return {"message": "CV-Upload – coming soon (Issue #05)"}
