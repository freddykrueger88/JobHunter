"""#72 – EURES-Stellensuche API."""
from fastapi import APIRouter, Query
from backend.services.job_search.eures_scraper import search_eures

router = APIRouter(prefix="/eures", tags=["EURES"])


@router.get("/search")
async def eures_search(
    q: str = Query(..., description="Suchbegriff (z.B. IT-Support)"),
    country: str = Query("DE", description="Ländercode (DE, EU, SE, NO, ...)"),
    lang: str = Query("de", description="Sprache der Ergebnisse"),
    page: int = Query(0, ge=0),
    page_size: int = Query(20, ge=1, le=100),
):
    return await search_eures(keywords=q, country_code=country, lang=lang, page=page, page_size=page_size)
