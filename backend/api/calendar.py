"""Kalender-Export Endpoints (.ics)."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.services.calendar_export import get_ical, get_all_ical

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


@router.get("/{application_id}/ics", response_class=Response)
async def export_single_ics(
    application_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Einzelnen Vorstellungsgespraech-Termin als .ics herunterladen."""
    try:
        ical_content = await get_ical(application_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return Response(
        content=ical_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f"attachment; filename=gespraech_{application_id}.ics"
        },
    )


@router.get("/feed.ics", response_class=Response)
async def export_feed_ics(db: AsyncSession = Depends(get_db)):
    """Abonnierbarer Kalender-Feed mit allen Terminen."""
    ical_content = await get_all_ical(db)
    return Response(
        content=ical_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": "attachment; filename=jobhunter_feed.ics"
        },
    )
