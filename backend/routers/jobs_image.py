"""Endpoint fuer Foto-Upload von Stellenanzeigen."""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from backend.core.database import get_db
from backend.services.ocr import extract_text_from_image, parse_job_from_text, OCR_ENGINE
from backend.models.job import Job
from backend.models.settings import UserSettings
from backend.models.history import HistoryEntry
from backend.schemas.job import JobRead

router = APIRouter(prefix='/api/jobs', tags=['jobs'])

ALLOWED_TYPES = {'image/jpeg', 'image/png', 'image/webp'}


class FromImageResponse(BaseModel):
    job: JobRead
    ocr_text: str
    ocr_engine: str
    message: str


@router.post('/from-image', response_model=FromImageResponse)
async def create_job_from_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f'Nicht unterstuetzter Dateityp: {file.content_type}')

    image_bytes = await file.read()

    try:
        text = await extract_text_from_image(image_bytes)
    except ValueError as e:
        raise HTTPException(422, str(e))
    except RuntimeError as e:
        raise HTTPException(500, str(e))

    settings_result = await db.execute(select(UserSettings).where(UserSettings.id == 1))
    s = settings_result.scalar_one_or_none()
    model = s.ai_model if s else "mistral"

    parsed = await parse_job_from_text(text, model=model)

    if not parsed.get('title') and not parsed.get('company'):
        raise HTTPException(422, 'Mindestens Titel oder Firma konnten nicht erkannt werden.')

    job = Job(
        title=parsed.get('title') or '(ohne Titel)',
        company=parsed.get('company') or '(unbekannt)',
        city=parsed.get('city') or None,
        description=parsed.get('description') or text,
        source_portal='foto-upload',
    )
    db.add(job)
    db.add(HistoryEntry(
        event_type="job_created",
        description=f"Stelle '{job.title}' per Foto-Upload erkannt",
        meta={"source": "foto-upload"},
    ))
    await db.commit()
    await db.refresh(job)

    return {
        'job': job,
        'ocr_text': text,
        'ocr_engine': OCR_ENGINE,
        'message': 'Stelle aus Foto angelegt. Bitte fehlende Felder ergaenzen.',
    }
