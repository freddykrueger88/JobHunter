"""Endpoint fuer Foto-Upload von Stellenanzeigen."""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.services.ocr import extract_text_from_image, parse_job_from_text
from backend.services.ai_client import get_ai_client
from backend.models import Job
from datetime import datetime

router = APIRouter(prefix='/api/jobs', tags=['jobs'])

ALLOWED_TYPES = {'image/jpeg', 'image/png', 'image/webp'}

@router.post('/from-image')
async def create_job_from_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    ai=Depends(get_ai_client),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f'Nicht unterstuetzter Dateityp: {file.content_type}')

    image_bytes = await file.read()

    try:
        text = await extract_text_from_image(image_bytes)
    except ValueError as e:
        raise HTTPException(422, str(e))

    parsed = await parse_job_from_text(text, ai)

    if not parsed.get('titel') and not parsed.get('firma'):
        raise HTTPException(422, 'Mindestens Titel oder Firma konnten nicht erkannt werden.')

    # Bewerbungsfrist parsen
    frist = None
    if parsed.get('bewerbungsfrist'):
        try:
            frist = datetime.fromisoformat(parsed['bewerbungsfrist'])
        except ValueError:
            pass

    job = Job(
        titel=parsed.get('titel', ''),
        firma=parsed.get('firma', ''),
        ort=parsed.get('ort', ''),
        beschreibung=parsed.get('beschreibung', text),
        quelle='foto-upload',
        gehalt_min=parsed.get('gehalt_min'),
        gehalt_max=parsed.get('gehalt_max'),
        bewerbungsfrist=frist,
        ist_remote=parsed.get('ist_remote', False),
        ist_hybrid=parsed.get('ist_hybrid', False),
        tags=str(parsed.get('tags', [])),
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    return {
        'job': job,
        'ocr_text': text,
        'ocr_engine': 'easyocr_or_pytesseract',
        'message': 'Stelle aus Foto angelegt. Bitte fehlende Felder ergaenzen.',
    }
