"""Ollama KI-Service: Anschreiben generieren, Modelle auflisten."""
import httpx, json
from backend.core.config import settings

TONE_PROMPTS = {
    "formell": "Schreibe in einem professionellen, formellen Stil. Siez-Form. Klare Struktur.",
    "direkt": "Schreibe direkt und auf den Punkt. Keine Füllwörter. Selbstbewusst.",
    "modern": "Schreibe modern und zeitgemäß. Du-Form ist ok. Frisch und authentisch.",
    "kreativ": "Schreibe kreativ und einprägsam. Hebe dich von der Masse ab. Originell.",
}


async def list_ollama_models() -> list[str]:
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5)
            r.raise_for_status()
            return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        return []


async def generate_cover_letter(
    job_title: str,
    company: str,
    contact_person: str | None,
    job_description: str | None,
    cv_summary: str,
    tone: str,
    model: str,
    template_text: str | None = None,
) -> str:
    tone_instruction = TONE_PROMPTS.get(tone, TONE_PROMPTS["formell"])
    contact_line = f"An: {contact_person}" if contact_person else "Kein Ansprechpartner bekannt"

    if template_text:
        prompt = f"""Du bist ein Experte für Bewerbungsschreiben.
{tone_instruction}

Fülle die folgende Anschreiben-Vorlage aus. Ersetze alle Platzhalter durch passende Inhalte.
Gib NUR das fertige Anschreiben zurück, keine Erklärungen.

Vorlage:
{template_text}

Stelleninformationen:
- Position: {job_title}
- Unternehmen: {company}
- {contact_line}
- Stellenbeschreibung: {(job_description or 'Keine Beschreibung')[:1000]}

Bewerber-Profil:
{cv_summary}
"""
    else:
        prompt = f"""Du bist ein Experte für Bewerbungsschreiben.
{tone_instruction}

Schreibe ein vollständiges Anschreiben für folgende Stelle.
Gib NUR das fertige Anschreiben zurück, keine Erklärungen.

Stelleninformationen:
- Position: {job_title}
- Unternehmen: {company}
- {contact_line}
- Stellenbeschreibung: {(job_description or 'Keine Beschreibung')[:1000]}

Bewerber-Profil:
{cv_summary}

Struktur: Datum, Empfänger, Betreff, Anrede, 3 Absätze (Einleitung/Hauptteil/Schluss), Gruß.
"""

    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=180,
            )
            r.raise_for_status()
            return r.json().get("response", "").strip()
    except Exception as e:
        return f"Fehler bei KI-Generierung: {e}"
