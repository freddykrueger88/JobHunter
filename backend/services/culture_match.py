"""#75/G.3.10 - Kulturelles Matching: KI schaetzt die Unternehmenskultur aus
der Stellenbeschreibung ein und vergleicht sie mit dem bereits vorhandenen
KI-Hintergrundprofil (Phase H: arbeitsstil/werte) statt eines eigenen
Setup-Fragebogens - siehe docs/analysis/BACKLOG.md Phase H.4."""
import json
import re

import httpx

from backend.core.config import settings

ARBEITSSTIL_LABELS = {
    "startup": "Startup",
    "mittelstand": "Mittelstand",
    "konzern": "Konzern",
    "behoerde": "Behörde",
    "egal": "keine Präferenz",
}

_FALLBACK: dict = {
    "score": 0,
    "unternehmenstyp_erkannt": "unbekannt",
    "passende_punkte": [],
    "abweichende_punkte": [],
    "kurzfazit": "Konnte anhand der Stellenbeschreibung nicht zuverlässig eingeschätzt werden.",
}


async def analyze_culture_match(
    job_description: str,
    company: str,
    arbeitsstil: str | None,
    werte: str | None,
    model: str = "mistral",
) -> dict:
    """Vergleicht die aus der Stellenbeschreibung geschätzte Unternehmenskultur
    mit den Bewerber-Präferenzen. Liefert bei KI-Fehlern/Fehlformat einen
    neutralen Fallback statt eines 500ers (gleiches Muster wie
    interview_simulator.generate_interview_questions, Nutzerentscheidung
    'strikt mit Fallback', siehe Backlog Phase B.6)."""
    arbeitsstil_text = ARBEITSSTIL_LABELS.get(arbeitsstil or "", "keine Angabe")
    werte_text = werte or "keine Angabe"

    prompt = f"""Du bist ein Experte für Unternehmenskultur und Recruiting.

Stellenbeschreibung von "{company}":
{(job_description or 'Keine Beschreibung vorhanden.')[:1800]}

Bewerber-Präferenzen:
- Bevorzugtes Arbeitsumfeld: {arbeitsstil_text}
- Was dem Bewerber im Job wichtig ist: {werte_text}

Schätze anhand der Stellenbeschreibung die Unternehmenskultur ein (Typ:
startup/mittelstand/konzern/behoerde/unbekannt) und vergleiche sie mit den
Bewerber-Präferenzen. Gib eine Match-Einschätzung als JSON zurück, genau
dieses Format:
{{
  "score": 0-100,
  "unternehmenstyp_erkannt": "startup|mittelstand|konzern|behoerde|unbekannt",
  "passende_punkte": ["Punkt 1", "Punkt 2"],
  "abweichende_punkte": ["Punkt 1"],
  "kurzfazit": "Ein Satz Fazit"
}}

Nur das JSON, keine Erklärungen."""

    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=180,
            )
            r.raise_for_status()
            raw = r.json().get("response", "").strip()
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                    # Mistral liefert "score" manchmal als JSON-String statt Zahl
                    # (z.B. "20" statt 20) - haeufige, harmlose LLM-Formatierungs-
                    # Variante, kein Grund fuer den Fallback.
                    score_raw = parsed.get("score")
                    if isinstance(score_raw, str) and score_raw.strip().lstrip("-").isdigit():
                        score_raw = int(score_raw)
                    if (
                        isinstance(parsed, dict)
                        and isinstance(score_raw, (int, float))
                        and isinstance(parsed.get("unternehmenstyp_erkannt"), str)
                        and isinstance(parsed.get("passende_punkte"), list)
                        and all(isinstance(p, str) for p in parsed["passende_punkte"])
                        and isinstance(parsed.get("abweichende_punkte"), list)
                        and all(isinstance(p, str) for p in parsed["abweichende_punkte"])
                        and isinstance(parsed.get("kurzfazit"), str)
                    ):
                        parsed["score"] = max(0, min(100, int(score_raw)))
                        return parsed
                except (ValueError, TypeError):
                    pass
    except Exception:
        pass
    return dict(_FALLBACK)
