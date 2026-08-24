from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.core.database import get_db
from backend.models.application import Application
from backend.models.history import HistoryEntry
from backend.models.reminder import Reminder
from datetime import datetime, timezone

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    statuses = ["interessant", "beworben", "interview", "angenommen", "absage"]
    counts = {}
    for status in statuses:
        result = await db.execute(
            select(func.count()).select_from(Application).where(Application.status == status)
        )
        counts[status] = result.scalar_one()

    # Letzte 10 Aktivitäten
    recent_result = await db.execute(
        select(HistoryEntry).order_by(HistoryEntry.created_at.desc()).limit(10)
    )
    recent = recent_result.scalars().all()

    # Fällige Erinnerungen
    now = datetime.now(timezone.utc)
    reminders_result = await db.execute(
        select(Reminder)
        .where(Reminder.is_done == False, Reminder.remind_at <= now)  # noqa
        .order_by(Reminder.remind_at)
        .limit(5)
    )
    due_reminders = reminders_result.scalars().all()

    return {
        "counts": counts,
        "total": sum(counts.values()),
        "recent_activity": [
            {"id": e.id, "type": e.event_type, "description": e.description,
             "meta": e.meta, "at": e.created_at}
            for e in recent
        ],
        "due_reminders": [
            {"id": r.id, "message": r.message, "remind_at": r.remind_at,
             "application_id": r.application_id}
            for r in due_reminders
        ],
    }
