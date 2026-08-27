"""Statistik-Endpunkte fuer StatsChart.tsx und WeeklyGoalWidget.tsx.

Beide Komponenten waren fertig gebaut, aber ohne jeden Backend-Anschluss
(kein /api/stats-Router existierte) und griffen auf ein veraltetes
Status-Vokabular zu (eingeladen/gespraech/zusage/zurueckgezogen statt
der tatsaechlichen interessant/beworben/interview/angenommen/absage).
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.core.database import get_db
from backend.models.application import Application
from backend.models.settings import UserSettings

router = APIRouter(prefix="/api/stats", tags=["Statistik"])

STATUSES = ["interessant", "beworben", "interview", "angenommen", "absage"]


@router.get("/")
async def get_overview_stats(db: AsyncSession = Depends(get_db)):
    nach_status = {}
    for status in STATUSES:
        result = await db.execute(
            select(func.count()).select_from(Application).where(Application.status == status)
        )
        nach_status[status] = result.scalar_one()
    total_result = await db.execute(select(func.count()).select_from(Application))
    return {"gesamt": total_result.scalar_one(), "nach_status": nach_status}


@router.get("/weekly")
async def get_weekly_stats(db: AsyncSession = Depends(get_db)):
    """Bewerbungen pro ISO-Kalenderwoche, letzte 8 Wochen (auch mit 0)."""
    result = await db.execute(select(Application.created_at))
    counts: dict[str, int] = {}
    for (created_at,) in result.all():
        if not created_at:
            continue
        iso_year, iso_week, _ = created_at.isocalendar()
        key = f"{iso_year}-W{iso_week:02d}"
        counts[key] = counts.get(key, 0) + 1

    today = datetime.now(timezone.utc).date()
    weeks = []
    for i in range(7, -1, -1):
        d = today - timedelta(weeks=i)
        iso_year, iso_week, _ = d.isocalendar()
        key = f"{iso_year}-W{iso_week:02d}"
        weeks.append({"woche": key, "anzahl": counts.get(key, 0)})
    return weeks


@router.get("/weekly-goal")
async def get_weekly_goal(db: AsyncSession = Depends(get_db)):
    settings_result = await db.execute(select(UserSettings).where(UserSettings.id == 1))
    s = settings_result.scalar_one_or_none()
    goal = s.weekly_goal if s else 5

    today = datetime.now(timezone.utc).date()
    monday = today - timedelta(days=today.weekday())
    week_start = datetime(monday.year, monday.month, monday.day, tzinfo=timezone.utc)

    count_result = await db.execute(
        select(func.count()).select_from(Application).where(Application.created_at >= week_start)
    )
    diese_woche = count_result.scalar() or 0
    prozent = min(100, round(diese_woche / goal * 100)) if goal > 0 else 0
    return {"wochenziel": goal, "diese_woche": diese_woche, "prozent": prozent}


@router.get("/streak")
async def get_streak(db: AsyncSession = Depends(get_db)):
    """Aktueller Tage-Streak (aufeinanderfolgende Tage mit >=1 Bewerbung),
    abreissend sobald ein ganzer Tag ausgelassen wird."""
    result = await db.execute(select(Application.created_at))
    dates = sorted({row[0].date() for row in result.all() if row[0]}, reverse=True)
    if not dates:
        return {"streak": 0, "letzte_aktivitaet": None}

    today = datetime.now(timezone.utc).date()
    if dates[0] < today - timedelta(days=1):
        return {"streak": 0, "letzte_aktivitaet": dates[0].isoformat()}

    streak = 0
    expected = dates[0]
    for d in dates:
        if d == expected:
            streak += 1
            expected -= timedelta(days=1)
        else:
            break

    return {"streak": streak, "letzte_aktivitaet": dates[0].isoformat()}
