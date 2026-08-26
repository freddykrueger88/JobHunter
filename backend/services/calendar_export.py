"""iCal-Export fuer Vorstellungsgespraeche."""
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models import Application, Job

def _ical_datetime(dt: datetime) -> str:
    return dt.strftime('%Y%m%dT%H%M%SZ')

def build_ical_event(app, job) -> str:
    start = app.interview_at or datetime.utcnow()
    end = start + timedelta(hours=1)
    job_title = job.title if job else "Stelle"
    job_company = job.company if job else ""
    title = f'Vorstellungsgespraech: {job_title} @ {job_company}'
    return (
        'BEGIN:VCALENDAR\r\n'
        'VERSION:2.0\r\n'
        'PRODID:-//JobHunter//DE\r\n'
        'BEGIN:VEVENT\r\n'
        f'UID:{app.id}@jobhunter\r\n'
        f'DTSTAMP:{_ical_datetime(datetime.utcnow())}\r\n'
        f'DTSTART:{_ical_datetime(start)}\r\n'
        f'DTEND:{_ical_datetime(end)}\r\n'
        f'SUMMARY:{title}\r\n'
        f'DESCRIPTION:Bewerbungs-ID {app.id}\r\n'
        'END:VEVENT\r\n'
        'END:VCALENDAR\r\n'
    )

async def get_ical(application_id: int, db: AsyncSession) -> str:
    result = await db.execute(select(Application).where(Application.id == application_id))
    app = result.scalar_one_or_none()
    if not app:
        raise ValueError('Bewerbung nicht gefunden')
    job_result = await db.execute(select(Job).where(Job.id == app.job_id))
    job = job_result.scalar_one_or_none()
    return build_ical_event(app, job)

async def get_all_ical(db: AsyncSession) -> str:
    """Gibt alle Gespraechstermine als abonnierbaren Kalender-Feed zurueck."""
    result = await db.execute(
        select(Application).where(Application.interview_at.isnot(None))
    )
    apps = result.scalars().all()
    events = []
    for app in apps:
        job_result = await db.execute(select(Job).where(Job.id == app.job_id))
        job = job_result.scalar_one_or_none()
        # Nur VEVENT-Block extrahieren
        ical = build_ical_event(app, job)
        start = ical.index('BEGIN:VEVENT')
        end = ical.index('END:VEVENT') + len('END:VEVENT') + 2
        events.append(ical[start:end])
    return (
        'BEGIN:VCALENDAR\r\n'
        'VERSION:2.0\r\n'
        'PRODID:-//JobHunter//DE\r\n'
        + ''.join(events) +
        'END:VCALENDAR\r\n'
    )
