"""Anschreiben-Bewertung per KI mit Score."""
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models import Application, Job
from backend.services.ai_prompts import detect_language

async def evaluate_cover_letter(application_id: int, db: AsyncSession, ai_client) -> dict:
    result = await db.execute(select(Application).where(Application.id == application_id))
    app = result.scalar_one_or_none()
    if not app or not app.anschreiben:
        raise ValueError('Kein Anschreiben vorhanden')
    job_result = await db.execute(select(Job).where(Job.id == app.job_id))
    job = job_result.scalar_one_or_none()
    lang = detect_language(app.anschreiben)
    if lang == 'de':
        prompt = f"""Bewerte dieses Anschreiben.

Anschreiben:
{app.anschreiben}

Stellenbeschreibung:
{job.beschreibung if job else ''}

JSON:
{{
  "gesamt_score": 78,
  "relevanz": 80,
  "ton": 75,
  "struktur": 80,
  "staerken": ["..."],
  "verbesserungen": ["..."],
  "zusammenfassung": "..."
}}"""
    else:
        prompt = f"""Evaluate this cover letter.

Cover letter:
{app.anschreiben}

Job description:
{job.beschreibung if job else ''}

JSON:
{{
  "overall_score": 78,
  "relevance": 80,
  "tone": 75,
  "structure": 80,
  "strengths": ["..."],
  "improvements": ["..."],
  "summary": "..."
}}"""
    response = await ai_client.generate(prompt)
    try:
        start = response.index('{')
        end = response.rindex('}') + 1
        data = json.loads(response[start:end])
    except (ValueError, json.JSONDecodeError):
        return {'raw': response}
    app.anschreiben_score = data.get('gesamt_score') or data.get('overall_score')
    await db.commit()
    return data
