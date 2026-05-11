from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime
from backend.core.database import get_db
from backend.models.reminder import Reminder

router = APIRouter(prefix="/reminders", tags=["Erinnerungen"])


class ReminderCreate(BaseModel):
    application_id: int | None = None
    remind_at: datetime
    message: str | None = None


class ReminderRead(BaseModel):
    id: int
    application_id: int | None
    remind_at: datetime
    message: str | None
    is_done: bool
    model_config = {"from_attributes": True}


@router.get("/", response_model=list[ReminderRead])
async def list_reminders(only_pending: bool = True, db: AsyncSession = Depends(get_db)):
    q = select(Reminder).order_by(Reminder.remind_at)
    if only_pending:
        q = q.where(Reminder.is_done == False)  # noqa
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/", response_model=ReminderRead, status_code=201)
async def create_reminder(data: ReminderCreate, db: AsyncSession = Depends(get_db)):
    reminder = Reminder(**data.model_dump())
    db.add(reminder)
    await db.commit()
    await db.refresh(reminder)
    return reminder


@router.patch("/{reminder_id}/done", response_model=ReminderRead)
async def mark_done(reminder_id: int, db: AsyncSession = Depends(get_db)):
    reminder = await db.get(Reminder, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Erinnerung nicht gefunden")
    reminder.is_done = True
    await db.commit()
    await db.refresh(reminder)
    return reminder


@router.delete("/{reminder_id}", status_code=204)
async def delete_reminder(reminder_id: int, db: AsyncSession = Depends(get_db)):
    reminder = await db.get(Reminder, reminder_id)
    if reminder:
        await db.delete(reminder)
        await db.commit()
