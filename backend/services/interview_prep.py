"""Interview-Vorbereitung: KI generiert Fragen + Musterantworten.

Nimmt (anders als urspruenglich) job_id statt application_id entgegen -
Vorbereitung bezieht sich auf die Stelle, nicht auf eine konkrete
Bewerbungs-Trackingzeile, analog zum bereits bestehenden Uebungsmodus
(backend/services/interview_simulator.py, /api/interview/questions/{job_id})."""
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models import Job
from backend.services.ai_prompts import detect_language


async def generate_interview_prep(job_id: int, cv_text: str, db: AsyncSession, ai_client) -> dict:
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise ValueError('Job nicht gefunden')

    lang = detect_language(job.description or '')
    language_instruction = (
        "Schreibe Fragen und Musterantworten auf Deutsch." if lang == "de"
        else "Write questions and sample answers in English."
    )
    prompt = f"""Erstelle Interview-Vorbereitungsfragen mit Musterantworten fuer diese Stelle.
{language_instruction}

Stelle: {job.title}
Beschreibung: {job.description or ''}
Lebenslauf des Bewerbers: {cv_text}

Gib NUR valides JSON zurueck, genau dieses Format (Schluessel immer englisch,
je Kategorie genau 2 kurze Fragen mit kurzen Musterantworten (max. 2 Saetze)):
{{
  "technical": [{{"question": "...", "sample_answer": "..."}}],
  "personal": [{{"question": "...", "sample_answer": "..."}}],
  "salary": [{{"question": "...", "sample_answer": "..."}}]
}}"""
    response = await ai_client.generate(prompt)
    try:
        start = response.index('{')
        end = response.rindex('}') + 1
        return json.loads(response[start:end])
    except (ValueError, json.JSONDecodeError):
        return {'raw': response}
