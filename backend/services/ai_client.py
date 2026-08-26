"""Duenner Ollama-Client fuer Services, die eine ai_client.generate(prompt)-
Schnittstelle erwarten (job_analyzer, skill_gap, cover_letter_evaluator,
rejection_analyzer, interview_prep). Das urspruenglich importierte Modul
existierte nie - jeder dieser Services war dadurch komplett unbenutzbar
(ImportError). Andere KI-Features im Projekt (ai_service.py, culture_match.py,
ocr.py) rufen Ollama jeweils direkt per httpx auf; dieser duenne Wrapper
macht dasselbe, nur mit einer Klassen-Schnittstelle, damit die bestehenden
Aufrufstellen (ai_client.generate(...)) unveraendert bleiben koennen."""
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from backend.core.config import settings
from backend.core.database import get_db
from backend.models.settings import UserSettings


class OllamaClient:
    def __init__(self, model: str = "mistral"):
        self.model = model

    async def generate(self, prompt: str, timeout: float = 180) -> str:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=timeout,
            )
            r.raise_for_status()
            return r.json().get("response", "")


async def get_ai_client(db: AsyncSession = Depends(get_db)) -> OllamaClient:
    """FastAPI-Dependency: nutzt das in UserSettings konfigurierte KI-Modell."""
    result = await db.execute(select(UserSettings).where(UserSettings.id == 1))
    s = result.scalar_one_or_none()
    model = s.ai_model if s else "mistral"
    return OllamaClient(model=model)
