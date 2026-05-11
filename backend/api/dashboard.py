from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.core.database import get_db
from backend.models.application import Application
from backend.models.history import HistoryEntry

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    statuses = ["interessant", "beworben", "interview", "angenommen", "absage"]
    counts = {}
    for status in statuses:
        result = await db.execute(
            select(func.count()).where(Application.status == status)
        )
        counts[status] = result.scalar_one()
    result = await db.execute(
        select(HistoryEntry).order_by(HistoryEntry.created_at.desc()).limit(10)
    )
    recent = result.scalars().all()
    return {
        "counts": counts,
        "recent_activity": [
            {"type": e.event_type, "description": e.description, "at": e.created_at}
            for e in recent
        ],
    }
