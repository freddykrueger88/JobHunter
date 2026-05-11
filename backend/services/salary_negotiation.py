"""Gehaltsnegotiations-Coach: KI-generierte Verhandlungsstrategie."""
from __future__ import annotations
import json
from backend.services.ai_prompts import detect_language

async def generate_negotiation_strategy(
    stelle: str,
    ort: str,
    erfahrung_jahre: int,
    gehalt_wunsch: float,
    gehalt_anzeige_min: float | None,
    gehalt_anzeige_max: float | None,
    ai_client,
) -> dict:
    """Generiert 3 Verhandlungsszenarien + konkrete Formulierungen."""
    gehalt_band = ''
    if gehalt_anzeige_min and gehalt_anzeige_max:
        gehalt_band = f'{gehalt_anzeige_min:,.0f}\u2013{gehalt_anzeige_max:,.0f} EUR'
    elif gehalt_anzeige_min:
        gehalt_band = f'ab {gehalt_anzeige_min:,.0f} EUR'
    elif gehalt_anzeige_max:
        gehalt_band = f'bis {gehalt_anzeige_max:,.0f} EUR'
    else:
        gehalt_band = 'nicht angegeben'

    prompt = f"""Du bist ein erfahrener Karrierecoach.

Bewerbungssituation:
- Stelle: {stelle}
- Ort: {ort}
- Berufserfahrung: {erfahrung_jahre} Jahre
- Gehaltswunsch des Bewerbers: {gehalt_wunsch:,.0f} EUR brutto/Jahr
- Gehaltsband der Anzeige: {gehalt_band}

Erstelle eine Gehaltsnegotiations-Strategie mit 3 Szenarien.

JSON:
{{
  "analyse": "Kurze Einschaetzung der Verhandlungsposition",
  "szenarien": [
    {{
      "typ": "konservativ",
      "betrag": 48000,
      "begruendung": "...",
      "formulierung_email": "...",
      "formulierung_telefonat": "..."
    }},
    {{
      "typ": "realistisch",
      "betrag": 52000,
      "begruendung": "...",
      "formulierung_email": "...",
      "formulierung_telefonat": "..."
    }},
    {{
      "typ": "optimistisch",
      "betrag": 56000,
      "begruendung": "...",
      "formulierung_email": "...",
      "formulierung_telefonat": "..."
    }}
  ],
  "tipps": ["Tipp 1", "Tipp 2", "Tipp 3"]
}}"""

    response = await ai_client.generate(prompt)
    try:
        start = response.index('{')
        end = response.rindex('}') + 1
        return json.loads(response[start:end])
    except (ValueError, json.JSONDecodeError):
        return {'raw': response}
