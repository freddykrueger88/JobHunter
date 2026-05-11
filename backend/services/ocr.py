"""OCR-Service fuer Foto-Upload von Stellenanzeigen.

Verwendet easyocr (bevorzugt) oder pytesseract als Fallback.
Beide laufen vollstaendig lokal, kein Cloud-Dienst.
"""
from __future__ import annotations
import io
import json
from pathlib import Path
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


async def parse_job_from_text(text: str, ai_client) -> dict:
    """Laedt erkannten OCR-Text in die KI und gibt strukturiertes Job-Objekt zurueck."""
    from backend.services.ai_prompts import detect_language, analyze_job_prompt
    lang = detect_language(text)
    prompt = f"""Extrahiere aus diesem Stellenanzeigen-Text ein strukturiertes Job-Objekt.

Text:
{text}

Gib NUR valides JSON zurueck (keine Erklaerungen):
{{
  "titel": "...",
  "firma": "...",
  "ort": "...",
  "beschreibung": "...",
  "gehalt_min": null,
  "gehalt_max": null,
  "bewerbungsfrist": null,
  "ist_remote": false,
  "ist_hybrid": false,
  "kontakt_email": null,
  "kontakt_telefon": null,
  "tags": []
}}"""
    response = await ai_client.generate(prompt)
    try:
        start = response.index('{')
        end = response.rindex('}') + 1
        return json.loads(response[start:end])
    except (ValueError, json.JSONDecodeError):
        return {
            'titel': '',
            'firma': '',
            'ort': '',
            'beschreibung': text,
            'tags': [],
        }
