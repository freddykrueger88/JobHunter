"""OCR-Service fuer Foto-Upload von Stellenanzeigen.

Verwendet easyocr (bevorzugt) oder pytesseract als Fallback.
Beide laufen vollstaendig lokal, kein Cloud-Dienst.
"""
from __future__ import annotations
import io
import json
from typing import Optional

try:
    import easyocr
    _READER: Optional[easyocr.Reader] = None
    def _get_reader() -> easyocr.Reader:
        global _READER
        if _READER is None:
            _READER = easyocr.Reader(['de', 'en'], gpu=False)
        return _READER
    def _ocr(image_bytes: bytes) -> str:
        reader = _get_reader()
        result = reader.readtext(image_bytes, detail=0, paragraph=True)
        return '\n'.join(result)
    OCR_ENGINE = 'easyocr'
except ImportError:
    try:
        import pytesseract
        from PIL import Image
        def _ocr(image_bytes: bytes) -> str:
            image = Image.open(io.BytesIO(image_bytes))
            return pytesseract.image_to_string(image, lang='deu+eng')
        OCR_ENGINE = 'pytesseract'
    except ImportError:
        def _ocr(image_bytes: bytes) -> str:
            raise RuntimeError(
                'Kein OCR-Backend gefunden. '
                'Installiere easyocr oder pytesseract+pillow im Docker-Image.'
            )
        OCR_ENGINE = 'none'


async def extract_text_from_image(image_bytes: bytes) -> str:
    """Extrahiert Text aus einem Bild (JPEG/PNG/WEBP)."""
    if len(image_bytes) > 10 * 1024 * 1024:
        raise ValueError('Bild zu gross (max. 10 MB)')
    text = _ocr(image_bytes)
    if not text or len(text.strip()) < 20:
        raise ValueError(
            'Kein ausreichender Text erkannt. '
            'Bitte ein scharfes, gut beleuchtetes Foto verwenden.'
        )
    return text.strip()


async def parse_job_from_text(text: str, model: str = "mistral") -> dict:
    """Laedt erkannten OCR-Text in die lokale KI (Ollama) und gibt ein
    strukturiertes Job-Objekt zurueck - Feldnamen wie backend/models/job.py
    (title/company/city/description), damit das Ergebnis direkt in ein
    Job-Objekt uebernommen werden kann."""
    import httpx
    from backend.core.config import settings

    prompt = f"""Extrahiere aus diesem Stellenanzeigen-Text die wichtigsten Angaben.

Text:
{text}

Gib NUR valides JSON zurueck (keine Erklaerungen), genau dieses Format:
{{
  "title": "Stellenbezeichnung",
  "company": "Firmenname",
  "city": "Ort",
  "description": "Kurze Zusammenfassung der Stellenbeschreibung"
}}"""

    fallback = {'title': '', 'company': '', 'city': '', 'description': text}

    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=90,
            )
            r.raise_for_status()
            response = r.json().get("response", "")
            start = response.index('{')
            end = response.rindex('}') + 1
            parsed = json.loads(response[start:end])
            if not isinstance(parsed, dict):
                return fallback
            return {
                'title': parsed.get('title') or '',
                'company': parsed.get('company') or '',
                'city': parsed.get('city') or '',
                'description': parsed.get('description') or text,
            }
    except Exception:
        return fallback
