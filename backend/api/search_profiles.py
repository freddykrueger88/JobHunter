from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from backend.core.database import get_db
from backend.models.search_profile import SearchProfile
from backend.services.scheduler import schedule_profile, run_search_profile
from backend.models.history import HistoryEntry

router = APIRouter(prefix="/api/search-profiles", tags=["Suchprofile"])


class ProfileCreate(BaseModel):
    name: str
    keywords: str
    location: str
    radius_km: int = 25
    schedule: str = "daily"


@router.get("/")
async def list_profiles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SearchProfile).order_by(SearchProfile.created_at.desc()))
    return result.scalars().all()


@router.post("/", status_code=201)
async def create_profile(data: ProfileCreate, db: AsyncSession = Depends(get_db)):
    profile = SearchProfile(**data.model_dump())
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    schedule_profile(profile)
    db.add(HistoryEntry(event_type="search_profile_created",
                        description=f"Suchprofil '{profile.name}' angelegt ({profile.schedule})"))
    await db.commit()
    return profile


@router.patch("/{pid}/toggle")
async def toggle_profile(pid: int, db: AsyncSession = Depends(get_db)):
    p = await db.get(SearchProfile, pid)
    if not p:
        raise HTTPException(status_code=404, detail="Profil nicht gefunden")
    p.is_active = not p.is_active
    await db.commit()
    await db.refresh(p)
    schedule_profile(p)
    return p


@router.post("/{pid}/run-now")
async def run_now(pid: int, db: AsyncSession = Depends(get_db)):
    p = await db.get(SearchProfile, pid)
    if not p:
        raise HTTPException(status_code=404, detail="Profil nicht gefunden")
    await run_search_profile(pid)
    await db.refresh(p)
    return {"message": "Suche ausgeführt", "new_results": p.last_result_count}


@router.delete("/{pid}", status_code=204)
async def delete_profile(pid: int, db: AsyncSession = Depends(get_db)):
    p = await db.get(SearchProfile, pid)
    if not p:
        raise HTTPException(404, "Profil nicht gefunden")
    from backend.services.scheduler import scheduler
    job_id = f"search_profile_{pid}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    await db.delete(p)
    await db.commit()
