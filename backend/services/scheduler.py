"""APScheduler – automatische Stellensuche per Cron."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.core.database import async_session_factory
from backend.models.search_profile import SearchProfile
from backend.models.job import Job
from backend.models.reminder import Reminder
from backend.models.history import HistoryEntry
from backend.models.settings import UserSettings
from backend.services.job_search.aggregator import search_all_sources
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def run_search_profile(profile_id: int):
    """Führt ein Suchprofil aus und speichert neue Treffer."""
    async with async_session_factory() as db:
        profile = await db.get(SearchProfile, profile_id)
        if not profile or not profile.is_active:
            return

        result = await db.execute(select(UserSettings).where(UserSettings.id == 1))
        settings_row = result.scalar_one_or_none() or UserSettings(id=1)

        raw_jobs = await search_all_sources(
            profile.keywords, profile.location, profile.radius_km, settings_row
        )

        new_count = 0
        for rj in raw_jobs:
            if rj.external_id:
                exists = await db.execute(
                    select(Job).where(Job.external_id == rj.external_id, Job.source_portal == rj.source_portal)
                )
                if exists.scalar_one_or_none():
                    continue
            job = Job(
                title=rj.title, company=rj.company, city=rj.city,
                description=rj.description, url=rj.url,
                job_type=rj.job_type, source_portal=rj.source_portal,
                external_id=rj.external_id, published_at=rj.published_at,
            )
            db.add(job)
            new_count += 1

        if new_count > 0:
            db.add(Reminder(
                remind_at=datetime.now(timezone.utc) + timedelta(minutes=5),
                message=f"🔍 Suchprofil '{profile.name}': {new_count} neue Stelle(n) gefunden!",
            ))
            db.add(HistoryEntry(
                event_type="auto_search",
                description=f"Automatische Suche '{profile.name}': {new_count} neue Stellen",
                meta={"profile_id": profile_id, "keywords": profile.keywords, "new": new_count},
            ))

        profile.last_run = datetime.now(timezone.utc)
        profile.last_result_count = new_count
        await db.commit()
        logger.info(f"Suchprofil '{profile.name}': {new_count} neue Stellen")


def schedule_profile(profile: "SearchProfile"):
    """Registriert oder aktualisiert einen Job im Scheduler."""
    job_id = f"search_profile_{profile.id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    if not profile.is_active:
        return
    # schedule: "daily", "weekly" oder cron-string
    if profile.schedule == "daily":
        trigger = CronTrigger(hour=8, minute=0)
    elif profile.schedule == "weekly":
        trigger = CronTrigger(day_of_week="mon", hour=8, minute=0)
    else:
        trigger = CronTrigger.from_crontab(profile.schedule)
    scheduler.add_job(run_search_profile, trigger, args=[profile.id], id=job_id, replace_existing=True)


async def init_scheduler():
    """Startet den Scheduler und lädt alle aktiven Suchprofile."""
    async with async_session_factory() as db:
        result = await db.execute(select(SearchProfile).where(SearchProfile.is_active == True))  # noqa
        profiles = result.scalars().all()
        for p in profiles:
            schedule_profile(p)
    scheduler.start()
    logger.info(f"Scheduler gestartet mit {len(scheduler.get_jobs())} Jobs")
