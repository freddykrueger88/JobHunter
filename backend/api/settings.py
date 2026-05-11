from fastapi import APIRouter

router = APIRouter(prefix="/settings", tags=["Einstellungen"])


@router.get("/")
async def get_settings():
    return {"message": "Einstellungen – coming soon (Issue #13)"}
