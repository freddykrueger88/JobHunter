"""#71 – Firmen-Dossier Endpoint."""
from fastapi import APIRouter, HTTPException, Query
from backend.services.company_research import fetch_company_dossier
from backend.schemas.company import CompanyDossier

router = APIRouter(prefix="/api/company", tags=["company"])


@router.get("/dossier", response_model=CompanyDossier)
async def get_company_dossier(name: str = Query(..., min_length=2, description="Firmenname")):
    """Gibt öffentliche Infos zur Firma zurück (Wikipedia, Logo, Warnung)."""
    if not name.strip():
        raise HTTPException(status_code=400, detail="Firmenname darf nicht leer sein")
    data = await fetch_company_dossier(name.strip())
    return data
