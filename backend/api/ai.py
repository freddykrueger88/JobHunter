from fastapi import APIRouter

router = APIRouter(prefix="/ai", tags=["KI"])


@router.post("/generate-cover-letter")
async def generate_cover_letter():
    return {"message": "Anschreiben-Generator – coming soon (Issue #11)"}
