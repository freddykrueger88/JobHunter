"""
Tests fuer GET /api/stats/activity-heatmap (#79, G.3.7 - Aktivitaets-
Heatmap im GitHub-Contribution-Graph-Stil).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.application import Application
from backend.models.job import Job

pytestmark = pytest.mark.asyncio


async def _make_application(db: AsyncSession, created_at: datetime) -> None:
    job = Job(title="Testjob", company="Testfirma")
    db.add(job)
    await db.flush()
    db.add(Application(job_id=job.id, status="beworben", created_at=created_at))
    await db.commit()


class TestActivityHeatmap:
    async def test_returns_one_entry_per_day_including_zero(self, client: httpx.AsyncClient):
        res = await client.get("/api/stats/activity-heatmap", params={"days": 7})

        assert res.status_code == 200, res.text
        body = res.json()
        assert len(body) == 7
        assert all(entry["anzahl"] == 0 for entry in body)

    async def test_entries_are_in_chronological_order(self, client: httpx.AsyncClient):
        res = await client.get("/api/stats/activity-heatmap", params={"days": 5})

        dates = [entry["datum"] for entry in res.json()]
        assert dates == sorted(dates)

    async def test_last_entry_is_today(self, client: httpx.AsyncClient):
        res = await client.get("/api/stats/activity-heatmap", params={"days": 3})

        today = datetime.now(timezone.utc).date().isoformat()
        assert res.json()[-1]["datum"] == today

    async def test_counts_applications_on_correct_day(self, client: httpx.AsyncClient, db: AsyncSession):
        today = datetime.now(timezone.utc)
        await _make_application(db, today)
        await _make_application(db, today)
        await _make_application(db, today - timedelta(days=2))

        res = await client.get("/api/stats/activity-heatmap", params={"days": 7})

        by_date = {entry["datum"]: entry["anzahl"] for entry in res.json()}
        today_key = today.date().isoformat()
        two_days_ago_key = (today - timedelta(days=2)).date().isoformat()
        assert by_date[today_key] == 2
        assert by_date[two_days_ago_key] == 1

    async def test_applications_outside_window_are_excluded(self, client: httpx.AsyncClient, db: AsyncSession):
        old = datetime.now(timezone.utc) - timedelta(days=30)
        await _make_application(db, old)

        res = await client.get("/api/stats/activity-heatmap", params={"days": 7})

        assert all(entry["anzahl"] == 0 for entry in res.json())

    async def test_default_days_is_365(self, client: httpx.AsyncClient):
        res = await client.get("/api/stats/activity-heatmap")

        assert len(res.json()) == 365
