from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.core.database import get_db
from backend.models.cv import CVData
from backend.models.history import HistoryEntry
import shutil, os

router = APIRouter(prefix="/cv", tags=["Lebenslauf"])
UPLOAD_DIR = "/app/uploads"


@router.post("/upload", status_code=201)
async def upload_cv(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    allowed = [".pdf", ".docx", ".doc"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Nur {allowed} erlaubt")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    dest = os.path.join(UPLOAD_DIR, file.filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    cv = CVData(filename=file.filename)
    db.add(cv)
    await db.commit()
    await db.refresh(cv)
    db.add(HistoryEntry(event_type="cv_uploaded", description=f"Lebenslauf '{file.filename}' hochgeladen"))
    await db.commit()
    return {"id": cv.id, "filename": cv.filename, "message": "Upload erfolgreich – Parsing folgt in Issue #05"}


@router.get("/")
async def list_cvs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CVData).order_by(CVData.uploaded_at.desc()))
    return [{"id": c.id, "filename": c.filename, "uploaded_at": c.uploaded_at} for c in result.scalars().all()]
