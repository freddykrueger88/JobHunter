"""Daten-Export und -Import (DSGVO Art. 20 – Datenportabilität)."""
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.core.database import get_db
from backend.models.application import Application
from backend.models.job import Job
from backend.models.cv import CVData
from backend.models.history import HistoryEntry
from backend.models.reminder import Reminder
from backend.models.settings import UserSettings
import io

router = APIRouter(prefix="/export", tags=["Export/Import"])

EXPORT_VERSION = "1.1"


async def _serialize(obj) -> dict:
    d = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
    for k, v in d.items():
        if isinstance(v, datetime):
            d[k] = v.isoformat()
    return d


@router.get("/")
async def export_all(db: AsyncSession = Depends(get_db)):
    """Exportiert alle Daten als JSON-Download."""
    data = {
        "version": EXPORT_VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "jobs": [await _serialize(r) for r in (await db.execute(select(Job))).scalars().all()],
        "applications": [await _serialize(r) for r in (await db.execute(select(Application))).scalars().all()],
        "reminders": [await _serialize(r) for r in (await db.execute(select(Reminder))).scalars().all()],
        "history": [await _serialize(r) for r in (await db.execute(select(HistoryEntry))).scalars().all()],
        "cvs": [await _serialize(r) for r in (await db.execute(select(CVData))).scalars().all()],
    }
    json_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    filename = f"jobhunter_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return StreamingResponse(
        io.BytesIO(json_bytes),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/import")
async def import_data(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Importiert einen JobHunter-Export. Bestehende Daten werden nicht überschrieben."""
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Nur .json-Dateien erlaubt")
    raw = await file.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Ungültiges JSON")

    version = data.get("version", "unknown")
    stats = {"jobs": 0, "applications": 0, "reminders": 0, "history": 0}

    # Jobs importieren (Duplikat-Check per external_id oder Titel+Firma)
    for item in data.get("jobs", []):
        existing = None
        if item.get("external_id"):
            res = await db.execute(select(Job).where(Job.external_id == item["external_id"]))
            existing = res.scalar_one_or_none()
        if not existing:
            job = Job(**{k: v for k, v in item.items() if k != "id" and hasattr(Job, k)})
            db.add(job)
            stats["jobs"] += 1

    # Erinnerungen
    for item in data.get("reminders", []):
        r = Reminder(**{k: v for k, v in item.items() if k != "id" and hasattr(Reminder, k)})
        db.add(r)
        stats["reminders"] += 1

    # Verlauf
    for item in data.get("history", []):
        h = HistoryEntry(**{k: v for k, v in item.items() if k != "id" and hasattr(HistoryEntry, k)})
        db.add(h)
        stats["history"] += 1

    await db.commit()
    db.add(HistoryEntry(
        event_type="data_imported",
        description=f"Import aus Version {version}: {stats['jobs']} Stellen, {stats['reminders']} Erinnerungen",
        meta=stats,
    ))
    await db.commit()
    return {"imported": stats, "source_version": version}
