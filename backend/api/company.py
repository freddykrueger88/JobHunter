"""#71 – Firmen-Dossier API."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.models.job import Job
from backend.services.company_research import fetch_company_dossier
from backend.schemas.company import CompanyDossier

router = APIRouter(prefix="/company", tags=["Firmen-Dossier"])


@router.get("/dossier/{job_id}", response_model=CompanyDossier)
async def get_company_dossier(job_id: int, db: AsyncSession = Depends(get_db)):
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job nicht gefunden")
    if not job.company:
        raise HTTPException(status_code=400, detail="Job hat keinen Firmennamen")
    dossier = await fetch_company_dossier(job.company)
    return dossier


@router.get("/dossier", response_model=CompanyDossier)
async def get_dossier_by_name(name: str):
    if not name or len(name) < 2:
        raise HTTPException(status_code=400, detail="Firmenname zu kurz")
    return await fetch_company_dossier(name)
