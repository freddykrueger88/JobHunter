from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.services.ai_client import get_ai_client
from backend.services.salary_negotiation import generate_negotiation_strategy

router = APIRouter(prefix="/api/salary", tags=["Gehalt"])


class NegotiationRequest(BaseModel):
    stelle: str
    ort: str | None = None
    erfahrung_jahre: int = 0
    gehalt_wunsch: float
    gehalt_anzeige_min: float | None = None
    gehalt_anzeige_max: float | None = None


@router.post("/negotiate")
async def negotiate(data: NegotiationRequest, ai_client=Depends(get_ai_client)):
    """KI-Gehaltsverhandlungs-Coach: 3 Szenarien + Formulierungen."""
    return await generate_negotiation_strategy(
        stelle=data.stelle,
        ort=data.ort or "",
        erfahrung_jahre=data.erfahrung_jahre,
        gehalt_wunsch=data.gehalt_wunsch,
        gehalt_anzeige_min=data.gehalt_anzeige_min,
        gehalt_anzeige_max=data.gehalt_anzeige_max,
        ai_client=ai_client,
    )
