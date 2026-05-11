"""Bewerbungs-Ziele und Streak-Tracking."""
from datetime import datetime, timedelta, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.models import Application

async def get_weekly_progress(db: AsyncSession, wochenziel: int = 5) -> dict:
    """Fortschritt fuer die aktuelle Woche."""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    result = await db.execute(
        select(func.count()).select_from(Application).where(
            Application.bewerbungsdatum >= datetime.combine(week_start, datetime.min.time()),
            Application.bewerbungsdatum <= datetime.combine(week_end, datetime.max.time()),
        )
    )
    count = result.scalar() or 0
    return {
        'wochenziel': wochenziel,
        'diese_woche': count,
        'prozent': min(round(count / wochenziel * 100), 100),
        'woche_start': week_start.isoformat(),
        'woche_ende': week_end.isoformat(),
    }

async def get_streak(db: AsyncSession) -> dict:
    """Berechnet den aktuellen Streak (aufeinanderfolgende Tage mit mind. 1 Bewerbung)."""
    result = await db.execute(
        select(func.date(Application.bewerbungsdatum))
        .group_by(func.date(Application.bewerbungsdatum))
        .order_by(func.date(Application.bewerbungsdatum).desc())
    )
    days_with_apps = [row[0] for row in result.all()]

    if not days_with_apps:
        return {'streak': 0, 'letzte_aktivitaet': None}

    streak = 1
    for i in range(1, len(days_with_apps)):
        diff = (days_with_apps[i-1] - days_with_apps[i]).days
        if diff == 1:
            streak += 1
        else:
            break

    return {
        'streak': streak,
        'letzte_aktivitaet': str(days_with_apps[0]),
    }

async def get_stats(db: AsyncSession) -> dict:
    """Aggregierte Statistiken fuer das Dashboard."""
    total = (await db.execute(select(func.count()).select_from(Application))).scalar() or 0

    status_result = await db.execute(
        select(Application.status, func.count()).group_by(Application.status)
    )
    by_status = {row[0]: row[1] for row in status_result.all()}

    return {
        'gesamt': total,
        'nach_status': by_status,
        'einladungsrate': round(
            (by_status.get('eingeladen', 0) + by_status.get('gespraech', 0)) / max(total, 1) * 100, 1
        ),
        'zusagerate': round(by_status.get('zusage', 0) / max(total, 1) * 100, 1),
    }
