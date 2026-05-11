"""Absage-Analyse: KI bewertet Absage und gibt Verbesserungsvorschlaege."""
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models import Application, Job
from backend.services.ai_prompts import rejection_analysis_prompt, detect_language

async def analyze_rejection(application_id: int, db: AsyncSession, ai_client) -> dict:
    result = await db.execute(select(Application).where(Application.id == application_id))
    app = result.scalar_one_or_none()
    if not app:
        raise ValueError('Bewerbung nicht gefunden')
    job_result = await db.execute(select(Job).where(Job.id == app.job_id))
    job = job_result.scalar_one_or_none()
    lang = detect_language(app.absage_text or '')
    prompt = rejection_analysis_prompt(
        cover_letter=app.anschreiben or '',
        rejection_text=app.absage_text or '',
        job_description=job.beschreibung if job else '',
        lang=lang,
    )
    response = await ai_client.generate(prompt)
    try:
        start = response.index('{')
        end = response.rindex('}') + 1
        return json.loads(response[start:end])
    except (ValueError, json.JSONDecodeError):
        return {'raw': response}
