"""Lebenslauf-Optimierung per KI."""
import json
from backend.services.ai_prompts import detect_language

async def optimize_cv(cv_text: str, job_description: str | None, ai_client) -> dict:
    lang = detect_language(cv_text)
    if lang == 'de':
        context = f'\nZielstelle:\n{job_description}' if job_description else ''
        prompt = f"""Analysiere diesen Lebenslauf und gib konkrete Verbesserungsvorschlaege.{context}\n\nLebenslauf:\n{cv_text}\n\nJSON:\n{{\n  \"score\": 72,\n  \"staerken\": [\"...\"],\n  \"schwaechen\": [\"...\"],\n  \"vorschlaege\": [{{\"abschnitt\": \"...\", \"vorschlag\": \"...\"}}]\n}}"""
    else:
        context = f'\nTarget position:\n{job_description}' if job_description else ''
        prompt = f"""Analyze this CV and provide improvement suggestions.{context}\n\nCV:\n{cv_text}\n\nJSON:\n{{\n  \"score\": 72,\n  \"strengths\": [\"...\"],\n  \"weaknesses\": [\"...\"],\n  \"suggestions\": [{{\"section\": \"...\", \"suggestion\": \"...\"}}]\n}}"""
    response = await ai_client.generate(prompt)
    try:
        start = response.index('{')
        end = response.rindex('}') + 1
        return json.loads(response[start:end])
    except (ValueError, json.JSONDecodeError):
        return {'raw': response}
