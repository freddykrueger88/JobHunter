"""#70 – Interview-Simulator: KI generiert Fragen + bewertet Antworten."""
import httpx
from backend.core.config import settings


async def generate_interview_questions(
    job_title: str,
    job_description: str | None,
    model: str = "mistral",
    num_questions: int = 8,
) -> list[dict]:
    """Generiert Interviewfragen für eine Stelle. Gibt Liste mit {question, category} zurück."""
    prompt = f"""Du bist ein erfahrener HR-Manager und führst ein Vorstellungsgespräch für die Stelle "{job_title}".

Stellenbeschreibung (Auszug):
{(job_description or 'Keine Beschreibung vorhanden.')[:800]}

Erstelle genau {num_questions} typische Interviewfragen.
Mix: 3 Fachfragen, 3 Soft-Skill-Fragen, 2 Situative Fragen (\"Stellen Sie sich vor...\").

Gib die Antwort als JSON-Array zurück, genau dieses Format:
[
  {{"question": "Fragetext", "category": "fachlich"}},
  {{"question": "Fragetext", "category": "soft_skill"}},
  {{"question": "Fragetext", "category": "situativ"}}
]

Nur das JSON, keine Erklärungen."""

    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=90,
            )
            r.raise_for_status()
            raw = r.json().get("response", "[]").strip()
            # JSON aus Antwort extrahieren
            import re, json
            match = re.search(r"\[.*\]", raw, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return [{"question": raw, "category": "allgemein"}]
    except Exception as e:
        return [{"question": f"KI nicht erreichbar: {e}", "category": "fehler"}]


async def evaluate_answer(
    question: str,
    answer: str,
    job_title: str,
    model: str = "mistral",
) -> dict:
    """Bewertet eine Interview-Antwort. Gibt {score, feedback, tip} zurück."""
    prompt = f"""Du bist ein HR-Coach und bewertest die folgende Interview-Antwort.

Stelle: {job_title}
Frage: {question}
Antwort des Bewerbers: {answer}

Bewerte die Antwort nach diesen Kriterien:
- Struktur (klar, logisch aufgebaut?)
- Relevanz (beantwortet die Frage?)
- Vollständigkeit (genügend Detail?)

Gib deine Bewertung als JSON zurück:
{{"score": <1-10>, "feedback": "<2-3 Sätze konstruktives Feedback>", "tip": "<1 konkreter Verbesserungshinweis>"}}

Nur das JSON, keine Erklärungen."""

    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=60,
            )
            r.raise_for_status()
            import re, json
            raw = r.json().get("response", "{}").strip()
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return {"score": 5, "feedback": raw, "tip": ""}
    except Exception as e:
        return {"score": 0, "feedback": f"KI-Fehler: {e}", "tip": "Ollama prüfen"}
