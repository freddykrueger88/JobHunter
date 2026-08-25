"""Ollama KI-Service: Anschreiben generieren, Coach-Chat, Modelle auflisten."""
import httpx
from backend.core.config import settings

TONE_PROMPTS = {
    "formell": "Schreibe in einem professionellen, formellen Stil. Siez-Form. Klare Struktur.",
    "direkt": "Schreibe direkt und auf den Punkt. Keine F\u00fcllw\u00f6rter. Selbstbewusst.",
    "modern": "Schreibe modern und zeitgem\u00e4\u00df. Du-Form ist ok. Frisch und authentisch.",
    "kreativ": "Schreibe kreativ und einpr\u00e4gsam. Hebe dich von der Masse ab. Originell.",
}

STATUS_LABELS = {
    "interessant": "Interessant (noch nicht beworben)",
    "beworben": "Beworben (wartet auf Antwort)",
    "interview": "Interview vereinbart",
    "angenommen": "Angenommen",
    "absage": "Absage erhalten",
}


async def list_ollama_models() -> list[str]:
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5)
            r.raise_for_status()
            return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        return []


async def coach_chat(
    messages: list[dict],
    model: str,
    tone: str = "formell",
    job_title: str | None = None,
    company: str | None = None,
    status: str | None = None,
    cover_letter_snippet: str | None = None,
) -> str:
    """Bewerbungscoach-Chat mit optionalem Bewerbungskontext."""
    context_lines = [
        "Du bist ein erfahrener Bewerbungscoach. Du hilfst Nutzern bei allen Fragen rund um die Jobsuche und Bewerbung.",
        "Antworte auf Deutsch, klar und praxisorientiert. Keine langen Einleitungen.",
    ]
    if job_title or company:
        context_lines.append(f"\nAktuelle Bewerbung: {job_title or 'unbekannte Stelle'} bei {company or 'unbekannter Firma'}.")
    if status:
        label = STATUS_LABELS.get(status, status)
        context_lines.append(f"Status: {label}")
    if cover_letter_snippet:
        context_lines.append(f"Anschreiben-Ausschnitt:\n{cover_letter_snippet[:400]}")

    system_prompt = "\n".join(context_lines)

    # Baue Prompt aus Chat-Verlauf
    conversation = ""
    for msg in messages:
        role_label = "Nutzer" if msg["role"] == "user" else "Coach"
        conversation += f"{role_label}: {msg['content']}\n"
    conversation += "Coach:"

    full_prompt = f"{system_prompt}\n\n{conversation}"

    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={"model": model, "prompt": full_prompt, "stream": False},
                timeout=120,
            )
            r.raise_for_status()
            return r.json().get("response", "").strip()
    except Exception as e:
        return f"Fehler: KI nicht erreichbar ({e}). Ist Ollama gestartet?"


async def generate_cover_letter(
    job_title: str,
    company: str,
    contact_person: str | None,
    job_description: str | None,
    cv_summary: str,
    tone: str,
    model: str,
    template_text: str | None = None,
    profile_summary: str | None = None,
) -> str:
    tone_instruction = TONE_PROMPTS.get(tone, TONE_PROMPTS["formell"])
    contact_line = f"An: {contact_person}" if contact_person else "Kein Ansprechpartner bekannt"
    profile_block = f"\n\n{profile_summary}" if profile_summary else ""

    if template_text:
        prompt = f"""Du bist ein Experte f\u00fcr Bewerbungsschreiben.
{tone_instruction}

F\u00fclle die folgende Anschreiben-Vorlage aus. Ersetze alle Platzhalter durch passende Inhalte.
Gib NUR das fertige Anschreiben zur\u00fcck, keine Erkl\u00e4rungen.

Vorlage:
{template_text}

Stelleninformationen:
- Position: {job_title}
- Unternehmen: {company}
- {contact_line}
- Stellenbeschreibung: {(job_description or 'Keine Beschreibung')[:1000]}

Bewerber-Profil:
{cv_summary}{profile_block}
"""
    else:
        prompt = f"""Du bist ein Experte f\u00fcr Bewerbungsschreiben.
{tone_instruction}

Schreibe ein vollst\u00e4ndiges Anschreiben f\u00fcr folgende Stelle.
Gib NUR das fertige Anschreiben zur\u00fcck, keine Erkl\u00e4rungen.

Stelleninformationen:
- Position: {job_title}
- Unternehmen: {company}
- {contact_line}
- Stellenbeschreibung: {(job_description or 'Keine Beschreibung')[:1000]}

Bewerber-Profil:
{cv_summary}{profile_block}

Struktur: Datum, Empf\u00e4nger, Betreff, Anrede, 3 Abs\u00e4tze (Einleitung/Hauptteil/Schluss), Gru\u00df.
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
