from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from backend.core.database import get_db
from backend.models.history import HistoryEntry

router = APIRouter(prefix="/history", tags=["Verlauf"])


@router.get("/")
async def get_history(
    event_type: str | None = None,
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(HistoryEntry).order_by(HistoryEntry.created_at.desc()).limit(limit)
    if event_type:
        q = q.where(HistoryEntry.event_type == event_type)
    result = await db.execute(q)
    entries = result.scalars().all()
    return [{"id": e.id, "type": e.event_type, "description": e.description,
             "meta": e.meta, "at": e.created_at} for e in entries]


@router.delete("/{entry_id}", status_code=204)
async def delete_history_entry(entry_id: int, db: AsyncSession = Depends(get_db)):
    entry = await db.get(HistoryEntry, entry_id)
    if entry:
        await db.delete(entry)
        await db.commit()
