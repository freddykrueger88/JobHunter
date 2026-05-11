"""KI-gestuetzte Stellenbeschreibungs-Analyse."""
from __future__ import annotations
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models import Job
from backend.services.ai_prompts import detect_language, analyze_job_prompt


async def analyze_job(job_id: int, db: AsyncSession, ai_client) -> dict:
    """Analysiert eine Stellenbeschreibung und speichert extrahierte Daten."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise ValueError(f'Job {job_id} nicht gefunden')

    if not job.beschreibung:
        raise ValueError('Keine Stellenbeschreibung vorhanden')

    lang = detect_language(job.beschreibung)
    prompt = analyze_job_prompt(job.beschreibung, lang=lang)
    response = await ai_client.generate(prompt)

    try:
        start = response.index('{')
        end = response.rindex('}') + 1
        data = json.loads(response[start:end])
    except (ValueError, json.JSONDecodeError):
        return {'error': 'KI-Antwort konnte nicht geparst werden', 'raw': response}

    # Tags und Felder in DB schreiben
    if data.get('tags'):
        job.tags = json.dumps(data['tags'], ensure_ascii=False)
    if data.get('gehalt_min') and not job.gehalt_min:
        job.gehalt_min = data['gehalt_min']
    if data.get('gehalt_max') and not job.gehalt_max:
        job.gehalt_max = data['gehalt_max']
    if data.get('arbeitsmodell') == 'remote':
        job.ist_remote = True
    if data.get('arbeitsmodell') == 'hybrid':
        job.ist_hybrid = True
    if data.get('sprache'):
        job.sprache = data['sprache']

    await db.commit()
    return data
