from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime, timezone
from backend.core.database import get_db
from backend.models.application import Application
from backend.models.application_status_log import ApplicationStatusLog
from backend.models.job import Job
from backend.models.cover_letter import CoverLetter
from backend.models.history import HistoryEntry
from backend.schemas.application import ApplicationBase, ApplicationRead
from backend.services.auto_apply import build_application_zip
from backend.services.ai_client import get_ai_client
import io

router = APIRouter(prefix="/api/applications", tags=["Bewerbungen"])


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


@router.get("/", response_model=list[ApplicationRead])
async def list_applications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application).order_by(Application.created_at.desc()))
    apps = result.scalars().all()
    cl_result = await db.execute(select(CoverLetter.application_id).distinct())
    app_ids_with_cover_letter = {row[0] for row in cl_result.all()}
    out = []
    for a in apps:
        job = await db.get(Job, a.job_id)
        d = {c.name: getattr(a, c.name) for c in a.__table__.columns}
        d["job"] = {"title": job.title, "company": job.company, "city": job.city} if job else None
        d["has_cover_letter"] = a.id in app_ids_with_cover_letter
        out.append(d)
    return out


@router.post("/", response_model=ApplicationBase)
async def create_application(data: ApplicationCreate, db: AsyncSession = Depends(get_db)):
    app = Application(**data.model_dump())
    db.add(app)
    db.add(HistoryEntry(
        event_type="application_created",
        description=f"Bewerbung f\u00fcr Job-ID {data.job_id} angelegt",
        meta={"job_id": data.job_id, "status": data.status},
    ))
    await db.flush()
    db.add(ApplicationStatusLog(application_id=app.id, status=data.status))
    await db.commit()
    await db.refresh(app)
    return app


@router.get("/{app_id}", response_model=ApplicationRead)
async def get_application(app_id: int, db: AsyncSession = Depends(get_db)):
    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Nicht gefunden")
    job = await db.get(Job, app.job_id)
    cl_result = await db.execute(select(CoverLetter.id).where(CoverLetter.application_id == app_id).limit(1))
    d = {c.name: getattr(app, c.name) for c in app.__table__.columns}
    d["job"] = {"title": job.title, "company": job.company, "city": job.city} if job else None
    d["has_cover_letter"] = cl_result.scalar_one_or_none() is not None
    return d


@router.patch("/{app_id}", response_model=ApplicationBase)
async def update_application(app_id: int, data: ApplicationUpdate, db: AsyncSession = Depends(get_db)):
    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Nicht gefunden")
    status_changed = data.status is not None and data.status != app.status
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(app, k, v)
    db.add(HistoryEntry(
        event_type="application_updated",
        description=f"Bewerbung {app_id} aktualisiert",
        # mode="json": model_dump() liefert sonst native datetime-Objekte
        # zurueck, die beim Schreiben in die JSON-Spalte "meta" mit
        # "Object of type datetime is not JSON serializable" crashen -
        # betraf jedes Setzen von interview_at/applied_at ueber Kanban.
        meta=data.model_dump(exclude_none=True, mode="json"),
    ))
    if status_changed:
        db.add(ApplicationStatusLog(application_id=app_id, status=data.status))
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


@router.post("/{app_id}/evaluate-cover-letter")
async def evaluate_cover_letter_endpoint(
    app_id: int,
    ai_client=Depends(get_ai_client),
    db: AsyncSession = Depends(get_db),
):
    """KI bewertet das zuletzt generierte Anschreiben dieser Bewerbung."""
    from backend.services.cover_letter_evaluator import evaluate_cover_letter

    try:
        return await evaluate_cover_letter(app_id, db, ai_client)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


class RejectionAnalysisRequest(BaseModel):
    rejection_text: str


@router.post("/{app_id}/analyze-rejection")
async def analyze_rejection_endpoint(
    app_id: int,
    data: RejectionAnalysisRequest,
    ai_client=Depends(get_ai_client),
    db: AsyncSession = Depends(get_db),
):
    """KI analysiert eine eingefuegte Absage im Kontext des Anschreibens."""
    from backend.services.rejection_analyzer import analyze_rejection

    try:
        return await analyze_rejection(app_id, data.rejection_text, db, ai_client)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{app_id}/ats-check")
async def ats_check_endpoint(
    app_id: int,
    ai_client=Depends(get_ai_client),
    db: AsyncSession = Depends(get_db),
):
    """ATS-Score: Keyword-Match des zuletzt hochgeladenen Lebenslaufs gegen
    die Stellenbeschreibung dieser Bewerbung."""
    from backend.models.cv import CVData
    from backend.services.ats_scorer import full_ats_check

    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Bewerbung nicht gefunden")

    job = await db.get(Job, app.job_id)
    if not job or not job.description:
        raise HTTPException(status_code=400, detail="Keine Stellenbeschreibung vorhanden")

    cv_result = await db.execute(select(CVData).order_by(CVData.uploaded_at.desc()).limit(1))
    cv = cv_result.scalar_one_or_none()
    if not cv or not cv.raw_text:
        raise HTTPException(status_code=400, detail="Kein Lebenslauf mit Originaltext vorhanden - bitte zuerst einen CV hochladen.")

    result = await full_ats_check(cv.raw_text, job.description, ai_client)
    # Zwischenspeichern fuer application_quality.py (Gesamt-Qualitaetsscore),
    # damit nicht bei jedem Checklisten-Aufruf neu gerechnet werden muss.
    app.ats_score = result.get("score")
    await db.commit()
    return result


@router.get("/{app_id}/timeline")
async def get_application_timeline(app_id: int, db: AsyncSession = Depends(get_db)):
    """Status-Verlauf einer Bewerbung fuer die Timeline im Kanban-Detail-
    Modal. War bisher ein reiner 404 - das Frontend rief den Endpoint
    seit jeher auf, es gab ihn nie (application_status_logs existierte
    als Modell, aber ohne Migration und ohne dass je etwas hineingeschrieben
    wurde)."""
    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Nicht gefunden")
    result = await db.execute(
        select(ApplicationStatusLog)
        .where(ApplicationStatusLog.application_id == app_id)
        .order_by(ApplicationStatusLog.changed_at.asc())
    )
    return [
        {"status": entry.status, "changed_at": entry.changed_at}
        for entry in result.scalars().all()
    ]


@router.get("/{app_id}/quality-score")
async def get_quality_score_endpoint(app_id: int, db: AsyncSession = Depends(get_db)):
    """Gewichteter Gesamt-Qualitaetsscore ueber alle KI-Tools hinweg."""
    from backend.services.application_quality import get_quality_score

    try:
        return await get_quality_score(app_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


class MarketAnalysisRequest(BaseModel):
    job_title: str
    firma: str
    job_description: str


@router.post("/{app_id}/market-analysis")
async def market_analysis_endpoint(
    app_id: int,
    data: MarketAnalysisRequest,
    ai_client=Depends(get_ai_client),
    db: AsyncSession = Depends(get_db),
):
    """KI schaetzt Wettbewerb, optimalen Bewerbungszeitpunkt und Strategie."""
    from backend.services.market_analyzer import analyze_market

    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Bewerbung nicht gefunden")

    return await analyze_market(
        job_title=data.job_title,
        job_description=data.job_description,
        firma=data.firma,
        ai_client=ai_client,
    )
