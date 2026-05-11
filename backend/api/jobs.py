from fastapi import APIRouter

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/")
async def list_jobs():
    return {"jobs": [], "message": "Job-Suche – coming soon (Issue #06)"}
