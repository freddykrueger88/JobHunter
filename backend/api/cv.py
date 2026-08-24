import os, shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.core.database import get_db
from backend.core.config import settings
from backend.models.cv import CVData
from backend.models.history import HistoryEntry
from backend.services.cv_parser import extract_text, parse_cv_with_ai

router = APIRouter(prefix="/api/cv", tags=["Lebenslauf"])
UPLOAD_DIR = "/app/uploads"


async def _parse_and_save(cv_id: int, filepath: str, db: AsyncSession):
    """Läuft im Hintergrund: Text extrahieren, KI aufrufen, DB updaten."""
    try:
        raw = extract_text(filepath)
        parsed = parse_cv_with_ai(raw, settings.OLLAMA_BASE_URL)
        cv = await db.get(CVData, cv_id)
        if cv:
            cv.raw_text = raw
            cv.full_name = parsed.get("full_name")
            cv.email = parsed.get("email")
            cv.phone = parsed.get("phone")
            cv.address = parsed.get("address")
            cv.skills = parsed.get("skills", [])
            cv.work_experience = parsed.get("work_experience", [])
            cv.education = parsed.get("education", [])
            await db.commit()
    except Exception as e:
        pass  # Fehler werden in der CV-Liste als fehlend sichtbar


@router.post("/upload", status_code=201)
async def upload_cv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    allowed = [".pdf", ".docx", ".doc"]
    # Nur den Dateinamen ohne Pfadanteile uebernehmen - schuetzt vor
    # Path Traversal ueber einen praeparierten Client-Dateinamen
    # (z.B. "../../app/irgendwas.pdf"), siehe
    # docs/analysis/REPOSITORY_AUDIT_DE.md Abschnitt 1.6.
    safe_filename = os.path.basename(file.filename)
    ext = os.path.splitext(safe_filename)[1].lower()
    if not safe_filename or ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Nur {allowed} erlaubt")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    dest = os.path.join(UPLOAD_DIR, safe_filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    cv = CVData(filename=safe_filename)
    db.add(cv)
    await db.commit()
    await db.refresh(cv)
    db.add(HistoryEntry(event_type="cv_uploaded", description=f"Lebenslauf '{safe_filename}' hochgeladen, Parsing gestartet"))
    await db.commit()
    background_tasks.add_task(_parse_and_save, cv.id, dest, db)
    return {"id": cv.id, "filename": cv.filename, "status": "parsing_started"}


@router.get("/")
async def list_cvs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CVData).order_by(CVData.uploaded_at.desc()))
    cvs = result.scalars().all()
    return [{
        "id": c.id,
        "filename": c.filename,
        "full_name": c.full_name,
        "email": c.email,
        "skills": c.skills,
        "uploaded_at": c.uploaded_at,
        "parsed": c.full_name is not None,
    } for c in cvs]


@router.get("/{cv_id}")
async def get_cv(cv_id: int, db: AsyncSession = Depends(get_db)):
    cv = await db.get(CVData, cv_id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV nicht gefunden")
    return {
        "id": cv.id, "filename": cv.filename, "full_name": cv.full_name,
        "email": cv.email, "phone": cv.phone, "address": cv.address,
        "skills": cv.skills, "work_experience": cv.work_experience,
        "education": cv.education, "uploaded_at": cv.uploaded_at,
    }


@router.delete("/{cv_id}", status_code=204)
async def delete_cv(cv_id: int, db: AsyncSession = Depends(get_db)):
    cv = await db.get(CVData, cv_id)
    if not cv:
        raise HTTPException(status_code=404, detail="CV nicht gefunden")
    filepath = os.path.join(UPLOAD_DIR, os.path.basename(cv.filename))
    if os.path.exists(filepath):
        os.remove(filepath)
    await db.delete(cv)
    await db.commit()
