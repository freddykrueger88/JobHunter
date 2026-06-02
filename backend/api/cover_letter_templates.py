"""API-Router für DOCX-Anschreiben-Vorlagen (Issue #89).

Endpoints:
    POST   /upload           – DOCX hochladen, Platzhalter extrahieren
    GET    /                 – Alle Vorlagen auflisten
    GET    /{id}             – Einzelne Vorlage abrufen
    DELETE /{id}             – Vorlage löschen
    POST   /{id}/generate    – Vorlage mit Job-Daten befüllen & DOCX zurückgeben
    GET    /placeholders     – Liste aller bekannten Platzhalter
"""

import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from backend.core.database import get_db
from backend.models.cover_letter_template import CoverLetterTemplate
from backend.models.job import Job
from backend.models.cv import CVData
from backend.models.history import HistoryEntry
from backend.services.docx_template_service import (
    extract_placeholders,
    fill_template,
    build_replacements_from_job,
    generate_cover_letter_text,
    KNOWN_PLACEHOLDERS,
)

router = APIRouter(prefix="/cover-letter-templates", tags=["Anschreiben-Vorlagen"])

TEMPLATE_DIR = "/app/uploads/templates"


# ─── Pydantic-Schemas ────────────────────────────────────────────

class TemplateResponse(BaseModel):
    id: int
    name: str
    filename: str
    placeholders: list[str]
    is_active: bool
    created_at: str
    updated_at: str


class GenerateRequest(BaseModel):
    job_id: int
    cv_id: int | None = None
    tone: str = "formell"
    model: str = "mistral"


class PlaceholderInfo(BaseModel):
    name: str
    description: str


# ─── Endpoints ───────────────────────────────────────────────────

@router.get("/placeholders", response_model=list[PlaceholderInfo])
async def list_placeholders():
    """Gibt alle bekannten Platzhalter mit Beschreibung zurück."""
    return [
        PlaceholderInfo(name=k, description=v)
        for k, v in KNOWN_PLACEHOLDERS.items()
    ]


@router.post("/upload", status_code=201)
async def upload_template(
    file: UploadFile = File(...),
    name: str = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """DOCX-Vorlage hochladen. Platzhalter werden automatisch extrahiert."""
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Nur .docx-Dateien erlaubt")

    os.makedirs(TEMPLATE_DIR, exist_ok=True)

    # Eindeutiger Dateiname
    template_name = name or os.path.splitext(file.filename)[0]
    dest = os.path.join(TEMPLATE_DIR, file.filename)

    # Falls Dateiname existiert, Suffix anhängen
    counter = 1
    base, ext = os.path.splitext(dest)
    while os.path.exists(dest):
        dest = f"{base}_{counter}{ext}"
        counter += 1

    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Platzhalter extrahieren
    try:
        placeholders = extract_placeholders(dest)
    except Exception as e:
        os.remove(dest)
        raise HTTPException(
            status_code=400,
            detail=f"DOCX konnte nicht gelesen werden: {e}",
        )

    # In DB speichern
    template = CoverLetterTemplate(
        name=template_name,
        filename=os.path.basename(dest),
        file_path=dest,
        placeholders=placeholders,
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)

    # History-Eintrag
    db.add(HistoryEntry(
        event_type="template_uploaded",
        description=f"Anschreiben-Vorlage '{template_name}' hochgeladen ({len(placeholders)} Platzhalter)",
    ))
    await db.commit()

    return {
        "id": template.id,
        "name": template.name,
        "filename": template.filename,
        "placeholders": template.placeholders,
        "is_active": template.is_active,
        "created_at": str(template.created_at),
        "updated_at": str(template.updated_at),
    }


@router.get("/")
async def list_templates(db: AsyncSession = Depends(get_db)):
    """Alle gespeicherten Vorlagen auflisten."""
    result = await db.execute(
        select(CoverLetterTemplate).order_by(CoverLetterTemplate.created_at.desc())
    )
    templates = result.scalars().all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "filename": t.filename,
            "placeholders": t.placeholders or [],
            "is_active": t.is_active,
            "created_at": str(t.created_at),
            "updated_at": str(t.updated_at),
        }
        for t in templates
    ]


@router.get("/{template_id}")
async def get_template(template_id: int, db: AsyncSession = Depends(get_db)):
    """Einzelne Vorlage abrufen."""
    template = await db.get(CoverLetterTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Vorlage nicht gefunden")
    return {
        "id": template.id,
        "name": template.name,
        "filename": template.filename,
        "placeholders": template.placeholders or [],
        "is_active": template.is_active,
        "created_at": str(template.created_at),
        "updated_at": str(template.updated_at),
    }


@router.delete("/{template_id}", status_code=204)
async def delete_template(template_id: int, db: AsyncSession = Depends(get_db)):
    """Vorlage aus DB und Dateisystem löschen."""
    template = await db.get(CoverLetterTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Vorlage nicht gefunden")

    # Datei löschen
    if os.path.exists(template.file_path):
        os.remove(template.file_path)

    db.add(HistoryEntry(
        event_type="template_deleted",
        description=f"Anschreiben-Vorlage '{template.name}' gelöscht",
    ))

    await db.delete(template)
    await db.commit()


@router.post("/{template_id}/generate")
async def generate_from_template(
    template_id: int,
    request: GenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Befüllt eine Vorlage mit Job-Daten und KI-Text, gibt DOCX zurück.

    1. Lade Vorlage und Job-Daten
    2. Optional: CV-Daten für Bewerbername und KI-Kontext
    3. KI generiert den Anschreiben-Fließtext
    4. Platzhalter in DOCX ersetzen
    5. Fertiges DOCX als Download zurückgeben
    """
    # Vorlage laden
    template = await db.get(CoverLetterTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Vorlage nicht gefunden")
    if not os.path.exists(template.file_path):
        raise HTTPException(status_code=404, detail="Vorlagen-Datei nicht gefunden")

    # Job laden
    job = await db.get(Job, request.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Stelle nicht gefunden")

    # Optional: CV laden
    cv_name = None
    cv_summary = None
    if request.cv_id:
        cv = await db.get(CVData, request.cv_id)
        if cv:
            cv_name = cv.full_name
            # Zusammenfassung für KI aus CV-Daten bauen
            parts = []
            if cv.full_name:
                parts.append(f"Name: {cv.full_name}")
            if cv.skills:
                parts.append(f"Skills: {', '.join(cv.skills[:15])}")
            if cv.work_experience:
                exp_strs = [
                    e if isinstance(e, str) else str(e)
                    for e in cv.work_experience[:5]
                ]
                parts.append(f"Erfahrung: {'; '.join(exp_strs)}")
            if cv.education:
                edu_strs = [
                    e if isinstance(e, str) else str(e)
                    for e in cv.education[:3]
                ]
                parts.append(f"Ausbildung: {'; '.join(edu_strs)}")
            cv_summary = "\n".join(parts)

    # KI-Text generieren (für {{ANSCHREIBEN_TEXT}})
    ai_text = await generate_cover_letter_text(
        job_title=job.title,
        company=job.company,
        contact_person=job.contact_person,
        job_description=job.description,
        cv_summary=cv_summary,
        tone=request.tone,
        model=request.model,
    )

    # Job-Dict bauen
    job_dict = {
        "title": job.title,
        "company": job.company,
        "address": job.address,
        "city": job.city,
        "postal_code": job.postal_code,
        "contact_person": job.contact_person,
    }

    # Replacements bauen
    replacements = build_replacements_from_job(
        job=job_dict,
        cv_name=cv_name,
        ai_text=ai_text,
    )

    # DOCX befüllen
    output_dir = os.path.join(TEMPLATE_DIR, "generated")
    os.makedirs(output_dir, exist_ok=True)

    safe_company = "".join(c for c in job.company if c.isalnum() or c in " _-")[:30].strip()
    safe_title = "".join(c for c in job.title if c.isalnum() or c in " _-")[:30].strip()
    output_filename = f"Anschreiben_{safe_company}_{safe_title}.docx"
    output_path = os.path.join(output_dir, output_filename)

    try:
        fill_template(template.file_path, replacements, output_path)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Befüllen der Vorlage: {e}",
        )

    # History-Eintrag
    db.add(HistoryEntry(
        event_type="template_generated",
        description=f"Anschreiben aus Vorlage '{template.name}' für '{job.title}' bei '{job.company}' generiert",
    ))
    await db.commit()

    return FileResponse(
        path=output_path,
        filename=output_filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
