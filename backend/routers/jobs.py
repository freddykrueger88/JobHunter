from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from backend.core.database import get_db
from backend.models.job import Job
from backend.models.settings import UserSettings
from backend.models.user_profile import UserProfile
from backend.models.history import HistoryEntry
from backend.schemas.job import JobCreate, JobRead
from backend.schemas.culture_match import CultureMatchResult
from backend.services.job_search.aggregator import search_all_sources
from backend.services.culture_match import analyze_culture_match
from backend.services.ai_client import get_ai_client
from backend.models.cv import CVData
import re

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])

PLZ_RE = re.compile(r"^\d{5}$")


def _normalize_location(location: str) -> str:
    """Gibt den Ort unveraendert zurueck. PLZ wird akzeptiert und direkt weitergegeben."""
    return location.strip()


def _parse_keywords(raw: str | None) -> list[str]:
    """Komma-getrennte Freitext-Begriffe -> bereinigte Liste (Leerzeichen
    getrimmt, leere Eintraege verworfen)."""
    if not raw:
        return []
    return [kw.strip() for kw in raw.split(",") if kw.strip()]


@router.get("/", response_model=list[JobRead])
async def list_jobs(
    hide_hidden: bool = True,
    hide_ausbildung: bool = Query(default=None),
    city: str | None = None,
    postal_code: str | None = None,
    benefit_keywords: str | None = Query(
        default=None,
        description="Komma-getrennte Begriffe (#88) - nur Stellen zeigen, die mindestens einen davon in Titel/Beschreibung enthalten",
    ),
    blacklist_keywords: str | None = Query(
        default=None,
        description="Komma-getrennte Begriffe (#88) - Stellen mit einem dieser Begriffe in Titel/Beschreibung ausblenden",
    ),
    db: AsyncSession = Depends(get_db),
):
    q = select(Job)
    if hide_hidden:
        q = q.where(Job.is_hidden == False)  # noqa
    if hide_ausbildung is True:
        q = q.where(Job.job_type != "ausbildung")
    if city:
        q = q.where(Job.city.ilike(f"%{city}%"))
    if postal_code:
        q = q.where(Job.postal_code.ilike(f"%{postal_code}%"))

    benefits = _parse_keywords(benefit_keywords)
    if benefits:
        q = q.where(or_(*[
            or_(Job.title.ilike(f"%{kw}%"), Job.description.ilike(f"%{kw}%"))
            for kw in benefits
        ]))

    blacklist = _parse_keywords(blacklist_keywords)
    if blacklist:
        q = q.where(and_(*[
            and_(
                ~Job.title.ilike(f"%{kw}%"),
                or_(Job.description.is_(None), ~Job.description.ilike(f"%{kw}%")),
            )
            for kw in blacklist
        ]))

    q = q.order_by(Job.created_at.desc())
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/eures-countries")
async def list_eures_countries():
    """Von EURES unterstuetzte Laender (Code + deutscher Name) fuers Land-
    Dropdown der Stellensuche - #72/Phase I.1. Muss vor /{job_id} stehen,
    sonst faengt die dynamische Route den Aufruf ab und versucht
    "eures-countries" als job_id zu parsen (404/422 statt der Liste)."""
    from backend.services.job_search.eures_scraper import EURES_COUNTRIES

    return [{"code": code, "name": name} for code, name in sorted(EURES_COUNTRIES.items(), key=lambda kv: kv[1])]


@router.get("/search")
async def search_jobs(
    keywords: str = Query(..., description="Suchbegriff, z.B. 'IT-Support'"),
    location: str = Query(
        ...,
        description="Ort oder PLZ, z.B. 'Bremen' oder '28195'",
        min_length=2,
    ),
    radius_km: int = Query(default=25, ge=0, le=200),
    country_code: str = Query(default="DE", min_length=2, max_length=2, description="EU-Land fuer die EURES-Suche, z.B. 'DE', 'AT', 'FR'"),
    save: bool = Query(default=True, description="Ergebnisse in DB speichern"),
    db: AsyncSession = Depends(get_db),
):
    """Sucht Stellen ueber alle konfigurierten Portale und speichert sie optional."""
    location = _normalize_location(location)
    is_plz = bool(PLZ_RE.match(location))

    result = await db.execute(select(UserSettings).where(UserSettings.id == 1))
    settings_row = result.scalar_one_or_none()
    if not settings_row:
        settings_row = UserSettings(id=1)

    raw_jobs = await search_all_sources(keywords, location, radius_km, settings_row, country_code=country_code.upper())

    new_count = 0
    if save:
        for rj in raw_jobs:
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
            label = f"PLZ {location}" if is_plz else f"'{location}'"
            db.add(HistoryEntry(
                event_type="job_search",
                description=f"Suche '{keywords}' in {label}: {new_count} neue Stellen gefunden",
                meta={"keywords": keywords, "location": location, "is_plz": is_plz, "new": new_count},
            ))
        await db.commit()

    return {
        "found": len(raw_jobs),
        "saved_new": new_count if save else 0,
        "location_type": "plz" if is_plz else "city",
        "jobs": [
            {"title": j.title, "company": j.company, "city": j.city,
             "postal_code": j.postal_code, "portal": j.source_portal, "url": j.url}
            for j in raw_jobs
        ],
    }


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
    db.add(HistoryEntry(event_type="job_created", description=f"Stelle '{job.title}' manuell hinzugef\u00fcgt"))
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


@router.post("/{job_id}/culture-match", response_model=CultureMatchResult)
async def culture_match(job_id: int, db: AsyncSession = Depends(get_db)):
    """#75/G.3.10 - vergleicht die aus der Stellenbeschreibung geschaetzte
    Unternehmenskultur mit dem KI-Hintergrundprofil (arbeitsstil/werte)."""
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Stelle nicht gefunden")

    profile_result = await db.execute(select(UserProfile).where(UserProfile.id == 1))
    profile = profile_result.scalar_one_or_none()
    if not profile or (not profile.arbeitsstil and not profile.werte):
        raise HTTPException(
            status_code=400,
            detail="Profil unvollstaendig: bitte zuerst 'Bevorzugtes Arbeitsumfeld' oder "
                   "'Werte' unter /profile ausfuellen.",
        )

    settings_result = await db.execute(select(UserSettings).where(UserSettings.id == 1))
    s = settings_result.scalar_one_or_none()
    model = s.ai_model if s else "mistral"

    return await analyze_culture_match(
        job_description=job.description or "",
        company=job.company,
        arbeitsstil=profile.arbeitsstil,
        werte=profile.werte,
        model=model,
    )


@router.get("/{job_id}/duplicates")
async def job_duplicates(job_id: int, db: AsyncSession = Depends(get_db)):
    """Findet aehnliche/moeglicherweise doppelte Stellen (Fuzzy-Matching)."""
    from backend.services.duplicate_detection import find_duplicates

    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Stelle nicht gefunden")
    return await find_duplicates(job_id, db)


@router.post("/{job_id}/analyze", response_model=JobRead)
async def analyze_job_endpoint(
    job_id: int,
    ai_client=Depends(get_ai_client),
    db: AsyncSession = Depends(get_db),
):
    """KI extrahiert Gehaltsspanne/Arbeitsmodell/Tags aus der Stellenbeschreibung."""
    from backend.services.job_analyzer import analyze_job

    try:
        await analyze_job(job_id, db, ai_client)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return await db.get(Job, job_id)


@router.post("/{job_id}/skill-gap")
async def skill_gap_endpoint(
    job_id: int,
    ai_client=Depends(get_ai_client),
    db: AsyncSession = Depends(get_db),
):
    """KI vergleicht den zuletzt hochgeladenen Lebenslauf mit der Stellenbeschreibung."""
    from backend.services.skill_gap import analyze_skill_gap

    cv_result = await db.execute(select(CVData).order_by(CVData.uploaded_at.desc()).limit(1))
    cv = cv_result.scalar_one_or_none()
    if not cv or not cv.raw_text:
        raise HTTPException(status_code=400, detail="Kein Lebenslauf mit Originaltext vorhanden - bitte zuerst einen CV hochladen.")

    try:
        return await analyze_skill_gap(job_id, cv.raw_text, db, ai_client)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
