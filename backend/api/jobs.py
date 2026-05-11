from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.core.database import get_db
from backend.models.job import Job
from backend.models.settings import UserSettings
from backend.models.history import HistoryEntry
from backend.schemas.job import JobCreate, JobRead
from backend.services.job_search.aggregator import search_all_sources

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/", response_model=list[JobRead])
async def list_jobs(
    hide_hidden: bool = True,
    hide_ausbildung: bool = Query(default=None),
    city: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(Job)
    if hide_hidden:
        q = q.where(Job.is_hidden == False)  # noqa
    if hide_ausbildung is True:
        q = q.where(Job.job_type != "ausbildung")
    if city:
        q = q.where(Job.city.ilike(f"%{city}%"))
    q = q.order_by(Job.created_at.desc())
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/search")
async def search_jobs(
    keywords: str = Query(..., description="Suchbegriff, z.B. 'IT-Support'"),
    location: str = Query(..., description="Ort, z.B. 'Bremen'"),
    radius_km: int = Query(default=25),
    save: bool = Query(default=True, description="Ergebnisse in DB speichern"),
    db: AsyncSession = Depends(get_db),
):
    """Sucht Stellen über alle konfigurierten Portale und speichert sie optional."""
    result = await db.execute(select(UserSettings).where(UserSettings.id == 1))
    settings_row = result.scalar_one_or_none()
    if not settings_row:
        settings_row = UserSettings(id=1)

    raw_jobs = await search_all_sources(keywords, location, radius_km, settings_row)

    if save:
        new_count = 0
        for rj in raw_jobs:
            # Duplikatcheck per external_id
            if rj.external_id:
                exists = await db.execute(
                    select(Job).where(Job.external_id == rj.external_id, Job.source_portal == rj.source_portal)
                )
                if exists.scalar_one_or_none():
                    continue
            job = Job(
                title=rj.title, company=rj.company, city=rj.city,
                postal_code=rj.postal_code, address=rj.address,
                contact_person=rj.contact_person, description=rj.description,
                url=rj.url, job_type=rj.job_type, source_portal=rj.source_portal,
                external_id=rj.external_id, published_at=rj.published_at,
                latitude=rj.latitude, longitude=rj.longitude,
            )
            db.add(job)
            new_count += 1
        if new_count:
            db.add(HistoryEntry(
                event_type="job_search",
                description=f"Suche '{keywords}' in '{location}': {new_count} neue Stellen gefunden",
                meta={"keywords": keywords, "location": location, "new": new_count},
            ))
        await db.commit()

    return {"found": len(raw_jobs), "saved_new": new_count if save else 0, "jobs": [
        {"title": j.title, "company": j.company, "city": j.city,
         "portal": j.source_portal, "url": j.url} for j in raw_jobs
    ]}


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
    db.add(HistoryEntry(event_type="job_created", description=f"Stelle '{job.title}' manuell hinzugefügt"))
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
