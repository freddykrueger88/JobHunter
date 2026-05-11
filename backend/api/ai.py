from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from backend.core.database import get_db
from backend.models.job import Job
from backend.models.cv import CVData
from backend.models.settings import UserSettings
from backend.models.cover_letter import CoverLetter
from backend.models.application import Application
from backend.models.history import HistoryEntry
from backend.services.ai_service import generate_cover_letter, list_ollama_models
import json

router = APIRouter(prefix="/ai", tags=["KI"])


class CoverLetterRequest(BaseModel):
    job_id: int
    application_id: int | None = None
    cv_id: int | None = None
    tone: str = "formell"
    template_text: str | None = None


@router.get("/models")
async def get_models():
    models = await list_ollama_models()
    return {"models": models or ["mistral", "llama3", "phi3"]}


@router.post("/generate-cover-letter")
async def api_generate_cover_letter(
    data: CoverLetterRequest,
    db: AsyncSession = Depends(get_db),
):
    job = await db.get(Job, data.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Stelle nicht gefunden")

    # CV-Zusammenfassung
    cv_summary = "Kein Lebenslauf vorhanden."
    if data.cv_id:
        cv = await db.get(CVData, data.cv_id)
        if cv:
            parts = []
            if cv.full_name: parts.append(f"Name: {cv.full_name}")
            if cv.skills: parts.append(f"Skills: {', '.join(cv.skills[:15])}")
            if cv.work_experience:
                exp = cv.work_experience[:3]
                parts.append("Erfahrung: " + "; ".join(
                    f"{e.get('role','')} bei {e.get('company','')}" for e in exp
                ))
            if cv.education:
                edu = cv.education[:2]
                parts.append("Ausbildung: " + "; ".join(
                    f"{e.get('degree','')} ({e.get('institution','')})" for e in edu
                ))
            cv_summary = "\n".join(parts)

    # KI-Modell aus Settings
    result = await db.execute(select(UserSettings).where(UserSettings.id == 1))
    s = result.scalar_one_or_none()
    model = s.ai_model if s else "mistral"
    tone = data.tone or (s.ai_tone if s else "formell")

    text = await generate_cover_letter(
        job_title=job.title,
        company=job.company,
        contact_person=job.contact_person,
        job_description=job.description,
        cv_summary=cv_summary,
        tone=tone,
        model=model,
        template_text=data.template_text,
    )

    cl = CoverLetter(
        application_id=data.application_id,
        content=text,
        tone_used=tone,
        model_used=model,
    )
    db.add(cl)
    db.add(HistoryEntry(
        event_type="cover_letter_generated",
        description=f"Anschreiben für '{job.title}' bei '{job.company}' generiert",
        meta={"job_id": job.id, "tone": tone, "model": model},
    ))
    await db.commit()
    await db.refresh(cl)
    return {"id": cl.id, "content": text, "tone": tone, "model": model}
