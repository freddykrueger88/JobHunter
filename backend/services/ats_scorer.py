"""ATS-Score-Checker: Keyword-Matching CV vs. Stellenbeschreibung.

Vollstaendig lokal, kein Cloud-Dienst.
Erkennt ausserdem ATS-feindliche Formatierungen.
"""
from __future__ import annotations
import re
import json
from collections import Counter
from typing import List

# Haeufige Stop-Woerter DE+EN (wird vor Keyword-Analyse entfernt)
STOPWORDS = {
    'und', 'oder', 'die', 'der', 'das', 'ein', 'eine', 'in', 'an', 'mit',
    'fuer', 'von', 'zu', 'ist', 'sind', 'wird', 'werden', 'haben', 'hat',
    'the', 'and', 'or', 'for', 'to', 'in', 'of', 'a', 'an', 'is', 'are',
    'you', 'we', 'our', 'your', 'be', 'will', 'with', 'that', 'this',
    'sie', 'wir', 'ihr', 'ihre', 'seinen', 'ihren', 'auch', 'als', 'bei',
    'sich', 'auf', 'aus', 'durch', 'nach', 'ueber', 'unter', 'vor', 'wie',
}

# ATS-feindliche Muster in Dateinamen / MIME-Typen
ATS_HOSTILE_PATTERNS = [
    (r'<table', 'Tabellen-Layout erschwert ATS-Parsing'),
    (r'text-align:\s*center.*column', 'Mehrspalter-Layout erkannt'),
    (r'<svg|<img', 'Grafiken/Icons koennen nicht von ATS gelesen werden'),
    (r'font-size:\s*[5-7]pt', 'Schriftgroesse unter 8pt – ATS ueberliest Inhalt'),
]


def _tokenize(text: str) -> List[str]:
    words = re.findall(r'[a-zA-Z\u00c0-\u024f]{3,}', text.lower())
    return [w for w in words if w not in STOPWORDS]


def score_ats(cv_text: str, job_description: str) -> dict:
    """Berechnet ATS-Score und gibt fehlende Keywords zurueck."""
    cv_tokens = set(_tokenize(cv_text))
    job_tokens = _tokenize(job_description)

    # Haeufigste Begriffe in der Stellenbeschreibung als 'Keywords'
    freq = Counter(job_tokens)
    # Top-30 als relevante Keywords
    top_keywords = [word for word, _ in freq.most_common(30)]

    matched = [kw for kw in top_keywords if kw in cv_tokens]
    missing = [kw for kw in top_keywords if kw not in cv_tokens]

    match_ratio = len(matched) / max(len(top_keywords), 1)
    score = round(match_ratio * 100)

    # Ampel
    if score >= 70:
        ampel = 'gruen'
        ampel_emoji = '\U0001f7e2'
    elif score >= 50:
        ampel = 'gelb'
        ampel_emoji = '\U0001f7e1'
    else:
        ampel = 'rot'
        ampel_emoji = '\U0001f534'

    # Kontext-Hinweise fuer fehlende Keywords
    suggestions = []
    for kw in missing[:8]:  # max. 8 konkrete Hinweise
        suggestions.append({
            'keyword': kw,
            'hinweis': f'Erwaehne \'{kw}\' in deinem Erfahrungs- oder Skills-Abschnitt',
        })

    return {
        'score': score,
        'ampel': ampel,
        'ampel_emoji': ampel_emoji,
        'matched_keywords': matched,
        'missing_keywords': missing,
        'suggestions': suggestions,
        'top_keywords': top_keywords,
    }


def check_ats_formatting(html_or_text: str) -> list[dict]:
    """Prueft auf ATS-feindliche Formatierungen."""
    warnings = []
    for pattern, message in ATS_HOSTILE_PATTERNS:
        if re.search(pattern, html_or_text, re.IGNORECASE):
            warnings.append({'typ': 'formatierung', 'meldung': message})
    return warnings


async def full_ats_check(cv_text: str, job_description: str, ai_client=None) -> dict:
    """Vollstaendiger ATS-Check: Score + Formatierung + optionale KI-Erklaerung."""
    score_result = score_ats(cv_text, job_description)
    format_warnings = check_ats_formatting(cv_text)

    result = {**score_result, 'format_warnings': format_warnings}

    # Optionale KI-Zusammenfassung
    if ai_client and score_result['score'] < 70:
        prompt = f"""Ein Lebenslauf hat einen ATS-Score von {score_result['score']}/100.
Fehlende Keywords: {', '.join(score_result['missing_keywords'][:10])}

Gib 3 kurze, konkrete Verbesserungsvorschlaege als JSON-Array:
["Vorschlag 1", "Vorschlag 2", "Vorschlag 3"]"""
        try:
            response = await ai_client.generate(prompt)
            start = response.index('[')
            end = response.rindex(']') + 1
            result['ki_vorschlaege'] = json.loads(response[start:end])
        except Exception:
            pass

    return result
