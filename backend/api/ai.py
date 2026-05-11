from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/ai", tags=["KI"])


class CoverLetterRequest(BaseModel):
    job_id: int
    cv_id: int | None = None
    tone: str = "formell"  # formell, direkt, modern, kreativ
    template_text: str | None = None


@router.post("/generate-cover-letter")
async def generate_cover_letter(data: CoverLetterRequest):
    # Vollständige Implementierung in Issue #11
    return {
        "message": "Anschreiben-Generator wird in Issue #11 implementiert",
        "job_id": data.job_id,
        "tone": data.tone,
    }


@router.get("/models")
async def list_models():
    # Ruft verfügbare Ollama-Modelle ab – vollständig in Issue #10
    return {"models": ["mistral", "llama3", "phi3"], "message": "Ollama-Integration folgt in Issue #10"}
