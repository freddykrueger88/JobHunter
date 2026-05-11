"""Interview-Vorbereitung: KI generiert Fragen + Musterantworten."""
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models import Application, Job
from backend.services.ai_prompts import interview_prep_prompt, detect_language

async def generate_interview_prep(application_id: int, cv_text: str, db: AsyncSession, ai_client) -> dict:
    result = await db.execute(select(Application).where(Application.id == application_id))
    app = result.scalar_one_or_none()
    if not app:
        raise ValueError('Bewerbung nicht gefunden')
    job_result = await db.execute(select(Job).where(Job.id == app.job_id))
    job = job_result.scalar_one_or_none()
    lang = detect_language(job.beschreibung if job else '')
    prompt = interview_prep_prompt(
        job_title=job.titel if job else '',
        job_description=job.beschreibung if job else '',
        cv_text=cv_text,
        lang=lang,
    )
    response = await ai_client.generate(prompt)
    try:
        start = response.index('{')
        end = response.rindex('}') + 1
        return json.loads(response[start:end])
    except (ValueError, json.JSONDecodeError):
        return {'raw': response}
