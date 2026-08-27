"""Lebenslauf-Optimierung per KI."""
import json
from backend.services.ai_prompts import detect_language


async def optimize_cv(cv_text: str, job_description: str | None, ai_client) -> dict:
    """Analysiert einen Lebenslauf und gibt konkrete Verbesserungsvorschlaege.

    Antwort-JSON-Schluessel bleiben unabhaengig von der erkannten Sprache
    immer identisch (Englisch) - nur die Vorschlagstexte selbst sollen in
    der Sprache des Lebenslaufs sein, damit das Frontend nicht zwei
    unterschiedliche Response-Formen behandeln muss (gleiches Muster wie
    cover_letter_evaluator.py)."""
    lang = detect_language(cv_text)
    context = f'\nZielstelle:\n{job_description}' if job_description else ''
    language_instruction = (
        'Schreibe die Texte auf Deutsch.' if lang == 'de' else 'Write the texts in English.'
    )
    prompt = f"""Du bist ein erfahrener Karriereberater und optimierst Lebenslaeufe.
{language_instruction}

Analysiere diesen Lebenslauf und gib konkrete Verbesserungsvorschlaege.{context}

Lebenslauf:
{cv_text}

Gib NUR valides JSON zurueck, genau dieses Format (Schluessel immer englisch):
{{
  "score": 0-100,
  "strengths": ["..."],
  "weaknesses": ["..."],
  "suggestions": [{{"section": "...", "suggestion": "..."}}]
}}"""
    response = await ai_client.generate(prompt)
    try:
        start = response.index('{')
        end = response.rindex('}') + 1
        return json.loads(response[start:end])
    except (ValueError, json.JSONDecodeError):
        return {'raw': response}
