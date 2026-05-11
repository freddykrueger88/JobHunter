"""Mehrsprachige KI-Prompt-Bibliothek fuer JobHunter."""
from typing import Literal

Lang = Literal['de', 'en']

TONE_DE = {
    'formell': 'Schreibe in einem professionellen, hoeflichen und formellen Stil.',
    'direkt': 'Schreibe direkt und klar, ohne Umschweife.',
    'modern': 'Schreibe in einem modernen, lockeren aber professionellen Stil.',
    'kreativ': 'Schreibe kreativ und einpraegam, hebe dich von Standard-Anschreiben ab.',
}
TONE_EN = {
    'formell': 'Write in a professional, polite and formal style.',
    'direkt': 'Write directly and concisely, no filler words.',
    'modern': 'Write in a modern, slightly casual but still professional tone.',
    'kreativ': 'Write creatively and memorably, stand out from standard cover letters.',
}

def detect_language(text: str) -> Lang:
    """Einfache Spracherkennung anhand haeufiger Woerter."""
    de_words = {'die', 'der', 'das', 'und', 'ist', 'wir', 'sie', 'ihr', 'mit', 'fuer'}
    en_words = {'the', 'and', 'for', 'with', 'our', 'you', 'are', 'will', 'we', 'your'}
    words = set(text.lower().split())
    de_score = len(words & de_words)
    en_score = len(words & en_words)
    return 'en' if en_score > de_score else 'de'

def cover_letter_prompt(
    job_title: str,
    company: str,
    job_description: str,
    cv_text: str,
    tone: str = 'formell',
    lang: Lang = 'de',
) -> str:
    tone_instruction = (TONE_DE if lang == 'de' else TONE_EN).get(tone, '')

    if lang == 'de':
        return f"""Du bist ein erfahrener Karriereberater. Schreibe ein Anschreiben fuer folgende Stelle.

{tone_instruction}

Stelle: {job_title} bei {company}
Stellenbeschreibung:
{job_description}

Lebenslauf des Bewerbers:
{cv_text}

Anforderungen:
- Maximal 4 Abschnitte (Einleitung, Motivation, Qualifikation, Abschluss)
- Keine Floskeln wie 'hiermit bewerbe ich mich'
- Konkrete Bezuege zur Stellenbeschreibung
- Auf Deutsch, Laenge ca. 250-350 Woerter"""
    else:
        return f"""You are an experienced career coach. Write a cover letter for the following position.

{tone_instruction}

Position: {job_title} at {company}
Job description:
{job_description}

Applicant's CV:
{cv_text}

Requirements:
- Maximum 4 paragraphs (intro, motivation, qualifications, closing)
- No clichés like 'I am writing to apply'
- Concrete references to the job description
- In English, approximately 250-350 words"""

def analyze_job_prompt(job_description: str, lang: Lang = 'de') -> str:
    if lang == 'de':
        return f"""Analysiere diese Stellenbeschreibung und extrahiere strukturierte Informationen.

Stellenbeschreibung:
{job_description}

Gib das Ergebnis als JSON zurueck:
{{
  "must_haves": ["..."],
  "nice_to_haves": ["..."],
  "gehalt_min": null,
  "gehalt_max": null,
  "arbeitsmodell": "remote|hybrid|vor-ort|unbekannt",
  "vertragsart": "vollzeit|teilzeit|befristet|unbefristet|unbekannt",
  "sprache": "de|en",
  "tags": ["..."]
}}"""
    else:
        return f"""Analyze this job description and extract structured information.

Job description:
{job_description}

Return JSON:
{{
  "must_haves": ["..."],
  "nice_to_haves": ["..."],
  "salary_min": null,
  "salary_max": null,
  "work_model": "remote|hybrid|on-site|unknown",
  "contract_type": "full-time|part-time|fixed-term|permanent|unknown",
  "language": "de|en",
  "tags": ["..."]
}}"""

def skill_gap_prompt(cv_text: str, job_description: str, lang: Lang = 'de') -> str:
    if lang == 'de':
        return f"""Vergleiche diesen Lebenslauf mit der Stellenbeschreibung.

Lebenslauf:
{cv_text}

Stellenbeschreibung:
{job_description}

Gib das Ergebnis als JSON zurueck:
{{
  "match_score": 75,
  "vorhandene_skills": ["..."],
  "fehlende_skills": ["..."],
  "lernempfehlungen": ["..."]
}}"""
    else:
        return f"""Compare this CV with the job description.

CV:
{cv_text}

Job description:
{job_description}

Return JSON:
{{
  "match_score": 75,
  "existing_skills": ["..."],
  "missing_skills": ["..."],
  "learning_recommendations": ["..."]
}}"""

def interview_prep_prompt(job_title: str, job_description: str, cv_text: str, lang: Lang = 'de') -> str:
    if lang == 'de':
        return f"""Erstelle Interview-Vorbereitungsfragen fuer diese Stelle.

Stelle: {job_title}
Beschreibung: {job_description}
Lebenslauf: {cv_text}

Gib 10 Fragen als JSON zurueck:
{{
  "fachlich": [{{"frage": "...", "muster_antwort": "..."}}],
  "persoenlich": [{{"frage": "...", "muster_antwort": "..."}}],
  "gehalt": [{{"frage": "...", "muster_antwort": "..."}}]
}}"""
    else:
        return f"""Create interview preparation questions for this position.

Position: {job_title}
Description: {job_description}
CV: {cv_text}

Return 10 questions as JSON:
{{
  "technical": [{{"question": "...", "sample_answer": "..."}}],
  "personal": [{{"question": "...", "sample_answer": "..."}}],
  "salary": [{{"question": "...", "sample_answer": "..."}}]
}}"""

def rejection_analysis_prompt(cover_letter: str, rejection_text: str, job_description: str, lang: Lang = 'de') -> str:
    if lang == 'de':
        return f"""Analysiere diese Absage und gib Verbesserungsvorschlaege.

Anschreiben:
{cover_letter}

Absage:
{rejection_text}

Stellenbeschreibung:
{job_description}

JSON:
{{
  "staerken": ["..."],
  "schwaechen": ["..."],
  "verbesserungsvorschlaege": ["..."],
  "zusammenfassung": "..."
}}"""
    else:
        return f"""Analyze this rejection and provide improvement suggestions.

Cover letter: {cover_letter}
Rejection: {rejection_text}
Job description: {job_description}

JSON:
{{
  "strengths": ["..."],
  "weaknesses": ["..."],
  "improvement_suggestions": ["..."],
  "summary": "..."
}}"""
