from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from backend.core.database import get_db
from backend.models.job import Job
from backend.models.history import HistoryEntry
from backend.schemas.job import JobCreate, JobRead

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/", response_model=list[JobRead])
async def list_jobs(
    hide_hidden: bool = True,
    hide_ausbildung: bool = True,
    city: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(Job)
    if hide_hidden:
        q = q.where(Job.is_hidden == False)  # noqa
    if hide_ausbildung:
        q = q.where(Job.job_type != "ausbildung")
    if city:
        q = q.where(Job.city.ilike(f"%{city}%"))
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{job_id}", response_model=JobRead)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Stelle nicht gefunden")
    return job


@router.post("/", response_model=JobRead, status_code=201)
async def create_job(data: JobCreate, db: AsyncSession = Depends(get_db)):
    job = Job(**data.model_dump())
    db.add(job)
    await db.commit()
    await db.refresh(job)
    db.add(HistoryEntry(event_type="job_created", description=f"Stelle '{job.title}' bei '{job.company}' hinzugefügt"))
    await db.commit()
    return job


@router.patch("/{job_id}/hide", response_model=JobRead)
async def hide_job(job_id: int, db: AsyncSession = Depends(get_db)):
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Stelle nicht gefunden")
    job.is_hidden = True
    await db.commit()
    await db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: int, db: AsyncSession = Depends(get_db)):
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Stelle nicht gefunden")
    await db.delete(job)
    await db.commit()
