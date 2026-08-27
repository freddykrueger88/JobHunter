"""
Tests fuer backend/routers/stats.py.

Bugfix-Sweep 2026-08-27: StatsChart.tsx (GET /api/stats/, GET /api/stats/
weekly) und WeeklyGoalWidget.tsx (GET /api/stats/weekly-goal, GET /api/
stats/streak) waren fertig gebaut, aber ohne jeden Backend-Anschluss -
kein /api/stats-Router existierte im gesamten Projekt. StatsChart.tsx
griff ausserdem auf ein veraltetes Status-Vokabular zu (eingeladen/
gespraech/zusage statt interview/angenommen).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.application import Application
from backend.models.job import Job
from backend.models.settings import UserSettings

pytestmark = pytest.mark.asyncio


async def _job(db: AsyncSession) -> Job:
    job = Job(title="Backend Engineer", company="Beispiel GmbH")
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


class TestOverviewStats:
    async def test_counts_by_real_status_vocabulary(self, client: httpx.AsyncClient, db: AsyncSession):
        job = await _job(db)
        db.add_all([
            Application(job_id=job.id, status="beworben"),
            Application(job_id=job.id, status="interview"),
            Application(job_id=job.id, status="angenommen"),
        ])
        await db.commit()

        res = await client.get("/api/stats/")

        assert res.status_code == 200, res.text
        body = res.json()
        assert body["gesamt"] == 3
        assert body["nach_status"]["beworben"] == 1
        assert body["nach_status"]["interview"] == 1
        assert body["nach_status"]["angenommen"] == 1


class TestWeeklyGoal:
    async def test_default_goal_is_five(self, client: httpx.AsyncClient):
        res = await client.get("/api/stats/weekly-goal")

        assert res.status_code == 200, res.text
        assert res.json()["wochenziel"] == 5

    async def test_configured_goal_and_progress(self, client: httpx.AsyncClient, db: AsyncSession):
        db.add(UserSettings(id=1, weekly_goal=2))
        await db.commit()
        job = await _job(db)
        db.add(Application(job_id=job.id, status="beworben"))
        await db.commit()

        res = await client.get("/api/stats/weekly-goal")

        body = res.json()
        assert body["wochenziel"] == 2
        assert body["diese_woche"] == 1
        assert body["prozent"] == 50

    async def test_progress_capped_at_100_percent(self, client: httpx.AsyncClient, db: AsyncSession):
        db.add(UserSettings(id=1, weekly_goal=1))
        job = await _job(db)
        db.add_all([Application(job_id=job.id, status="beworben") for _ in range(5)])
        await db.commit()

        res = await client.get("/api/stats/weekly-goal")

        assert res.json()["prozent"] == 100


class TestStreak:
    async def test_no_applications_returns_zero(self, client: httpx.AsyncClient):
        res = await client.get("/api/stats/streak")

        assert res.status_code == 200, res.text
        assert res.json() == {"streak": 0, "letzte_aktivitaet": None}

    async def test_three_consecutive_days_ending_today(self, client: httpx.AsyncClient, db: AsyncSession):
        job = await _job(db)
        today = datetime.now(timezone.utc)
        db.add_all([
            Application(job_id=job.id, status="interessant", created_at=today),
            Application(job_id=job.id, status="interessant", created_at=today - timedelta(days=1)),
            Application(job_id=job.id, status="interessant", created_at=today - timedelta(days=2)),
        ])
        await db.commit()

        res = await client.get("/api/stats/streak")

        assert res.json()["streak"] == 3

    async def test_streak_broken_by_gap(self, client: httpx.AsyncClient, db: AsyncSession):
        job = await _job(db)
        today = datetime.now(timezone.utc)
        db.add_all([
            Application(job_id=job.id, status="interessant", created_at=today),
            Application(job_id=job.id, status="interessant", created_at=today - timedelta(days=3)),
        ])
        await db.commit()

        res = await client.get("/api/stats/streak")

        assert res.json()["streak"] == 1

    async def test_streak_resets_to_zero_if_older_than_yesterday(self, client: httpx.AsyncClient, db: AsyncSession):
        job = await _job(db)
        old = datetime.now(timezone.utc) - timedelta(days=5)
        db.add(Application(job_id=job.id, status="interessant", created_at=old))
        await db.commit()

        res = await client.get("/api/stats/streak")

        assert res.json()["streak"] == 0
        assert res.json()["letzte_aktivitaet"] is not None


class TestWeeklyBreakdown:
    async def test_returns_eight_weeks(self, client: httpx.AsyncClient):
        res = await client.get("/api/stats/weekly")

        assert res.status_code == 200, res.text
        assert len(res.json()) == 8

    async def test_current_week_reflects_new_application(self, client: httpx.AsyncClient, db: AsyncSession):
        job = await _job(db)
        db.add(Application(job_id=job.id, status="interessant"))
        await db.commit()

        res = await client.get("/api/stats/weekly")

        assert res.json()[-1]["anzahl"] == 1
