"""KI-gestuetzte Stellenbeschreibungs-Analyse."""
from __future__ import annotations
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models import Job
from backend.services.ai_prompts import detect_language


async def analyze_job(job_id: int, db: AsyncSession, ai_client) -> dict:
    """Analysiert eine Stellenbeschreibung und speichert extrahierte Daten
    (Gehaltsspanne, Arbeitsmodell, Tags) auf dem Job."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise ValueError(f'Job {job_id} nicht gefunden')

    if not job.description:
        raise ValueError('Keine Stellenbeschreibung vorhanden')

    lang = detect_language(job.description)
    language_instruction = (
        "Schreibe die must_haves/nice_to_haves auf Deutsch." if lang == "de"
        else "Write must_haves/nice_to_haves in English."
    )
    prompt = f"""Analysiere diese Stellenbeschreibung und extrahiere strukturierte Informationen.
{language_instruction}

Stellenbeschreibung:
{job.description}

Gib NUR valides JSON zurueck, genau dieses Format (Schluessel immer englisch):
{{
  "must_haves": ["..."],
  "nice_to_haves": ["..."],
  "salary_min": null,
  "salary_max": null,
  "work_model": "remote|hybrid|vor-ort|unbekannt",
  "tags": ["..."]
}}"""
    response = await ai_client.generate(prompt)

    try:
        start = response.index('{')
        end = response.rindex('}') + 1
        data = json.loads(response[start:end])
    except (ValueError, json.JSONDecodeError):
        return {'error': 'KI-Antwort konnte nicht geparst werden', 'raw': response}

    if data.get('tags'):
        job.tags = json.dumps(data['tags'], ensure_ascii=False)
    if data.get('salary_min') and not job.salary_min:
        job.salary_min = data['salary_min']
    if data.get('salary_max') and not job.salary_max:
        job.salary_max = data['salary_max']
    if data.get('work_model') in ('remote', 'hybrid', 'vor-ort'):
        job.work_model = data['work_model']

    await db.commit()
    return data
