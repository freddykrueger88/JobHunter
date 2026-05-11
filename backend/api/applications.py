from fastapi import APIRouter

router = APIRouter(prefix="/applications", tags=["Bewerbungen"])


@router.get("/")
async def list_applications():
    return {"applications": [], "message": "Bewerbungen – coming soon (Issue #08)"}
