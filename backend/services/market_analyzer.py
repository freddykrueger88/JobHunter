"""Marktlage-Analyse: KI bewertet Wettbewerb und optimalen Bewerbungszeitpunkt."""
from __future__ import annotations
import json
from backend.services.ai_prompts import detect_language

# Heuristiken fuer Dringlichkeits-Signale
URGENT_SIGNALS = [
    r'sofort',
    r'ab sofort',
    r'immediately',
    r'asap',
    r'dringend',
    r'schnellstm.glich',
]

GROWTH_SIGNALS = [
    r'wachsendes team',
    r'growing team',
    r'wir erweitern',
    r'we are expanding',
    r'neue stelle',
    r'neu geschaffene',
]

FLUCTUATION_SIGNALS = [
    r'nachfolge',
    r'nachfolger',
    r'succession',
    r'wiederbeset',
    r'elternzeit',
    r'leaving',
]

import re

def _count_signals(text: str, patterns: list) -> int:
    return sum(1 for p in patterns if re.search(p, text, re.IGNORECASE))


async def analyze_market(
    job_title: str,
    job_description: str,
    firma: str,
    ai_client,
) -> dict:
    """Analysiert Wettbewerb und empfiehlt Bewerbungsstrategie."""
    lang = detect_language(job_description)

    urgent = _count_signals(job_description, URGENT_SIGNALS)
    growth = _count_signals(job_description, GROWTH_SIGNALS)
    fluctuation = _count_signals(job_description, FLUCTUATION_SIGNALS)

    # Vorab-Heuristik fuer Kontext
    heuristik = {
        'dringlichkeit': urgent > 0,
        'team_wachstum': growth > 0,
        'fluktuation': fluctuation > 0,
    }

    prompt = f"""Analysiere diese Stellenanzeige und schaetze die Marktlage ein.

Stelle: {job_title}
Firma: {firma}
Beschreibung (Auszug):
{job_description[:1200]}

Hinweise: Dringlichkeit={urgent}, Wachstum={growth}, Fluktuation={fluctuation}

JSON:
{{
  "wettbewerb": "niedrig|mittel|hoch",
  "wettbewerb_begruendung": "...",
  "optimaler_zeitpunkt": "sofort|1 Woche|2 Wochen",
  "zeitpunkt_begruendung": "...",
  "unternehmenstyp": "startup|kmu|konzern|behoerde|unbekannt",
  "strategie": "Direkt bewerben|Erst LinkedIn-Kontakt suchen|Auf Empfehlung warten",
  "strategie_begruendung": "...",
  "chancen": ["..."],
  "risiken": ["..."]
}}"""

    response = await ai_client.generate(prompt)
    try:
        start = response.index('{')
        end = response.rindex('}') + 1
        data = json.loads(response[start:end])
    except (ValueError, json.JSONDecodeError):
        return {'raw': response, 'heuristik': heuristik}

    return {**data, 'heuristik': heuristik}
