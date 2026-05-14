from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime, timezone
from backend.core.database import get_db
from backend.models.application import Application
from backend.models.job import Job
from backend.models.history import HistoryEntry
from backend.services.auto_apply import build_application_zip
import io

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
    applied_at: datetime | None = None
    interview_at: datetime | None = None
    kanban_position: int | None = None


class FollowUpUpdate(BaseModel):
    followup_at: datetime | None = None


@router.get("/")
async def list_applications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application).order_by(Application.created_at.desc()))
    apps = result.scalars().all()
    out = []
    for a in apps:
        job = await db.get(Job, a.job_id)
        d = {c.name: getattr(a, c.name) for c in a.__table__.columns}
        d["job"] = {"title": job.title, "company": job.company, "location": job.location} if job else None
        out.append(d)
    return out


@router.post("/")
async def create_application(data: ApplicationCreate, db: AsyncSession = Depends(get_db)):
    app = Application(**data.model_dump())
    db.add(app)
    db.add(HistoryEntry(
        event_type="application_created",
        description=f"Bewerbung f\u00fcr Job-ID {data.job_id} angelegt",
        meta={"job_id": data.job_id, "status": data.status},
    ))
    await db.commit()
    await db.refresh(app)
    return app


@router.get("/{app_id}")
async def get_application(app_id: int, db: AsyncSession = Depends(get_db)):
    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Nicht gefunden")
    job = await db.get(Job, app.job_id)
    d = {c.name: getattr(app, c.name) for c in app.__table__.columns}
    d["job"] = {"title": job.title, "company": job.company, "location": job.location} if job else None
    return d


@router.patch("/{app_id}")
async def update_application(app_id: int, data: ApplicationUpdate, db: AsyncSession = Depends(get_db)):
    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Nicht gefunden")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(app, k, v)
    db.add(HistoryEntry(
        event_type="application_updated",
        description=f"Bewerbung {app_id} aktualisiert",
        meta=data.model_dump(exclude_none=True),
    ))
    await db.commit()
    await db.refresh(app)
    return app


@router.patch("/{app_id}/followup")
async def set_followup(app_id: int, data: FollowUpUpdate, db: AsyncSession = Depends(get_db)):
    """#64 – Wiedervorlage-Datum setzen."""
    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Nicht gefunden")
    # followup_at als notes-JSON-Feld speichern (kein Migration-Aufwand)
    import json as _json
    notes_data = {}
    try:
        notes_data = _json.loads(app.notes or "{}")
    except Exception:
        notes_data = {"text": app.notes or ""}
    notes_data["followup_at"] = data.followup_at.isoformat() if data.followup_at else None
    app.notes = _json.dumps(notes_data, ensure_ascii=False)
    await db.commit()
    return {"followup_at": data.followup_at}


@router.delete("/{app_id}")
async def delete_application(app_id: int, db: AsyncSession = Depends(get_db)):
    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Nicht gefunden")
    await db.delete(app)
    await db.commit()
    return {"deleted": app_id}


@router.get("/{app_id}/zip")
async def download_application_zip(app_id: int, db: AsyncSession = Depends(get_db)):
    """#63 – 1-Klick-ZIP: Anschreiben-PDF + Metadaten."""
    try:
        zip_bytes, filename = await build_application_zip(app_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return StreamingResponse(
        io.BytesIO(zip_bytes),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
