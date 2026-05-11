"""Skill-Gap-Analyse: CV vs. Stellenbeschreibung."""
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models import Job
from backend.services.ai_prompts import skill_gap_prompt, detect_language

async def analyze_skill_gap(job_id: int, cv_text: str, db: AsyncSession, ai_client) -> dict:
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise ValueError('Job nicht gefunden')
    lang = detect_language(job.beschreibung or '')
    prompt = skill_gap_prompt(cv_text=cv_text, job_description=job.beschreibung or '', lang=lang)
    response = await ai_client.generate(prompt)
    try:
        start = response.index('{')
        end = response.rindex('}') + 1
        data = json.loads(response[start:end])
    except (ValueError, json.JSONDecodeError):
        return {'raw': response}
    # Score in DB cachen
    job.skill_gap_score = data.get('match_score')
    job.skill_gap_json = json.dumps(data, ensure_ascii=False)
    await db.commit()
    return data
