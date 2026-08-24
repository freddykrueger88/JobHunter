"""#71 – Firmen-Dossier Endpoint.

Vereint api/company.py (geloescht, Nutzerentscheidung 2026-08-24) und
diese Datei - beide riefen denselben Service auf und lieferten identisches
Format (Audit REPOSITORY_AUDIT_DE.md 1.6, Rework-Plan Backlog). Die
Job-ID-basierte Variante aus company.py wurde hierher uebernommen.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.models.job import Job
from backend.services.company_research import fetch_company_dossier
from backend.schemas.company import CompanyDossier

router = APIRouter(prefix="/api/company", tags=["company"])


@router.get("/dossier/{job_id}", response_model=CompanyDossier)
async def get_company_dossier_by_job(job_id: int, db: AsyncSession = Depends(get_db)):
    """Dossier zur Firma einer bestehenden Bewerbung/Stelle (ehem. api/company.py)."""
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job nicht gefunden")
    if not job.company:
        raise HTTPException(status_code=400, detail="Job hat keinen Firmennamen")
    return await fetch_company_dossier(job.company)


@router.get("/dossier", response_model=CompanyDossier)
async def get_company_dossier(name: str = Query(..., min_length=2, description="Firmenname")):
    """Gibt öffentliche Infos zur Firma zurück (Wikipedia, Logo, Warnung)."""
    if not name.strip():
        raise HTTPException(status_code=400, detail="Firmenname darf nicht leer sein")
    data = await fetch_company_dossier(name.strip())
    return data
