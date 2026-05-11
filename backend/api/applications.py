from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from backend.core.database import get_db
from backend.models.application import Application
from backend.models.application_status_log import ApplicationStatusLog
from backend.models.history import HistoryEntry
from datetime import datetime, timezone

router = APIRouter(prefix="/applications", tags=["Bewerbungen"])


class ApplicationCreate(BaseModel):
    job_id: int
    status: str = "interessant"
    notes: str | None = None
    applied_at: datetime | None = None
    interview_at: datetime | None = None


class ApplicationUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None
    kanban_position: int | None = None
    applied_at: datetime | None = None
    interview_at: datetime | None = None


@router.get("/")
async def list_applications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application).order_by(Application.kanban_position))
    return result.scalars().all()


@router.post("/", status_code=201)
async def create_application(data: ApplicationCreate, db: AsyncSession = Depends(get_db)):
    app = Application(**data.model_dump())
    db.add(app)
    await db.flush()
    db.add(ApplicationStatusLog(application_id=app.id, status=app.status))
    db.add(HistoryEntry(event_type="application_created", description=f"Bewerbung angelegt (Status: {app.status})", meta={"job_id": app.job_id}))
    await db.commit()
    await db.refresh(app)
    return app


@router.patch("/{app_id}")
async def update_application(app_id: int, data: ApplicationUpdate, db: AsyncSession = Depends(get_db)):
    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Bewerbung nicht gefunden")
    old_status = app.status
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(app, field, value)
    if data.status and data.status != old_status:
        db.add(ApplicationStatusLog(application_id=app.id, status=data.status))
        db.add(HistoryEntry(
            event_type="status_changed",
            description=f"Status geändert: {old_status} → {data.status}",
            meta={"app_id": app_id, "from": old_status, "to": data.status},
        ))
    await db.commit()
    await db.refresh(app)
    return app


@router.get("/{app_id}/timeline")
async def get_timeline(app_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ApplicationStatusLog)
        .where(ApplicationStatusLog.application_id == app_id)
        .order_by(ApplicationStatusLog.changed_at)
    )
    return [{"status": e.status, "changed_at": e.changed_at} for e in result.scalars().all()]


@router.delete("/{app_id}", status_code=204)
async def delete_application(app_id: int, db: AsyncSession = Depends(get_db)):
    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Bewerbung nicht gefunden")
    await db.delete(app)
    await db.commit()
