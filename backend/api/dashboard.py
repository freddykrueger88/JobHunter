from fastapi import APIRouter

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_stats():
    return {
        "beworben": 0,
        "absagen": 0,
        "angenommen": 0,
        "interview": 0,
        "offen": 0,
    }
