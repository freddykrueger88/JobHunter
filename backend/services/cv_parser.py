"""CV-Parser: extrahiert strukturierte Daten aus PDF, DOCX, DOC via lokaler KI."""
import os
from pathlib import Path


def extract_text_from_pdf(filepath: str) -> str:
    from pdfminer.high_level import extract_text
    return extract_text(filepath) or ""


def extract_text_from_docx(filepath: str) -> str:
    from docx import Document
    doc = Document(filepath)
    return "\n".join(p.text for p in doc.paragraphs)


def extract_text(filepath: str) -> str:
    ext = Path(filepath).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(filepath)
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(filepath)
    raise ValueError(f"Nicht unterstütztes Format: {ext}")


def parse_cv_with_ai(raw_text: str, ollama_base_url: str, model: str = "mistral") -> dict:
    """Sendet den Rohtext an Ollama und extrahiert strukturierte CV-Felder."""
    import httpx, json

    prompt = f"""Analysiere den folgenden Lebenslauf und extrahiere die Daten als JSON.
Gib NUR valides JSON zurück, kein Text darum herum.
Format:
{{
  "full_name": "...",
  "email": "...",
  "phone": "...",
  "address": "...",
  "skills": ["skill1", "skill2"],
  "work_experience": [
    {{"company": "...", "role": "...", "from": "...", "to": "...", "description": "..."}}
  ],
  "education": [
    {{"institution": "...", "degree": "...", "from": "...", "to": "..."}}
  ]
}}

Lebenslauf:
{raw_text[:4000]}
"""
    try:
        response = httpx.post(
            f"{ollama_base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=120,
        )
        response.raise_for_status()
        text = response.json().get("response", "{}")
        # JSON aus Antwort extrahieren
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end]) if start != -1 else {}
    except Exception as e:
        return {"error": str(e)}
