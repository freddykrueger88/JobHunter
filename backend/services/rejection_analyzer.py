"""Absage-Analyse: KI bewertet Absage und gibt Verbesserungsvorschlaege."""
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models import Application, CoverLetter
from backend.services.ai_prompts import detect_language


async def analyze_rejection(application_id: int, rejection_text: str, db: AsyncSession, ai_client) -> dict:
    """Analysiert eine Absage im Kontext des zuletzt generierten Anschreibens.

    JobHunter trackt keinen eigenen Absage-Text (kein Feld dafuer im
    Datenmodell) - der Text wird bei jeder Analyse frisch vom Nutzer
    eingegeben statt persistiert (analog zum Kultur-Match: zustandslos,
    keine neue Migration noetig)."""
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
    cover_letter_text = cover_letter.content if cover_letter else ''

    lang = detect_language(rejection_text)
    language_instruction = (
        "Schreibe die Analyse auf Deutsch." if lang == "de"
        else "Write the analysis in English."
    )
    prompt = f"""Du bist ein erfahrener Karriereberater. Analysiere diese Absage
im Kontext des Anschreibens und gib konkrete Verbesserungsvorschlaege.
{language_instruction}

Anschreiben:
{cover_letter_text or '(kein Anschreiben vorhanden)'}

Absage:
{rejection_text}

Gib NUR valides JSON zurueck, genau dieses Format (Schluessel immer englisch):
{{
  "strengths": ["..."],
  "weaknesses": ["..."],
  "improvement_suggestions": ["..."],
  "summary": "Ein bis zwei Saetze Fazit"
}}"""

    response = await ai_client.generate(prompt)
    try:
        start = response.index('{')
        end = response.rindex('}') + 1
        return json.loads(response[start:end])
    except (ValueError, json.JSONDecodeError):
        return {'raw': response}
