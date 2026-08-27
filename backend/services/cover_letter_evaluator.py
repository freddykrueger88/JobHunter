"""Anschreiben-Bewertung per KI mit Score."""
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models import Application, CoverLetter, Job
from backend.services.ai_prompts import detect_language


async def evaluate_cover_letter(application_id: int, db: AsyncSession, ai_client) -> dict:
    """Bewertet das (zuletzt generierte) Anschreiben einer Bewerbung.

    Anschreiben liegen in einer eigenen Tabelle (cover_letters, per
    application_id verknuepft) - nicht als Feld auf Application, wie der
    urspruengliche Code (app.anschreiben) annahm."""
    result = await db.execute(select(Application).where(Application.id == application_id))
    app = result.scalar_one_or_none()
    if not app:
        raise ValueError('Bewerbung nicht gefunden')

    cl_result = await db.execute(
        select(CoverLetter)
        .where(CoverLetter.application_id == application_id)
        .order_by(CoverLetter.created_at.desc())
    )
    cover_letter = cl_result.scalars().first()
    if not cover_letter:
        raise ValueError('Kein Anschreiben vorhanden')

    job_result = await db.execute(select(Job).where(Job.id == app.job_id))
    job = job_result.scalar_one_or_none()
    lang = detect_language(cover_letter.content)

    # Antwort-JSON-Schluessel bleiben unabhaengig von der erkannten Sprache
    # immer identisch (Englisch) - nur die Bewertungstexte selbst sollen in
    # der Sprache des Anschreibens sein. Sonst haette das Frontend zwei
    # unterschiedliche Response-Formen behandeln muessen (bereits bestehende
    # Schwaeche in mehreren der bilingualen ai_prompts.py-Funktionen).
    language_instruction = (
        "Schreibe die Bewertungstexte auf Deutsch." if lang == "de"
        else "Write the evaluation texts in English."
    )
    prompt = f"""Du bist ein erfahrener Karriereberater und bewertest Anschreiben.
{language_instruction}

Anschreiben:
{cover_letter.content}

Stellenbeschreibung:
{job.description if job else ''}

Gib NUR valides JSON zurueck, genau dieses Format (Schluessel immer englisch):
{{
  "overall_score": 0-100,
  "relevance": 0-100,
  "tone": 0-100,
  "structure": 0-100,
  "strengths": ["..."],
  "improvements": ["..."],
  "summary": "Ein bis zwei Saetze Fazit"
}}"""

    response = await ai_client.generate(prompt)
    try:
        start = response.index('{')
        end = response.rindex('}') + 1
        data = json.loads(response[start:end])
    except (ValueError, json.JSONDecodeError):
        return {'raw': response}

    # Zwischenspeichern fuer application_quality.py (Gesamt-Qualitaetsscore
    # ueber alle KI-Tools hinweg), damit nicht bei jedem Checklisten-Aufruf
    # neu bewertet werden muss.
    if isinstance(data.get('overall_score'), (int, float)):
        cover_letter.quality_score = int(data['overall_score'])
        await db.commit()

    return data
