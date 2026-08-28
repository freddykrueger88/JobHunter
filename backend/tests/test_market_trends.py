"""
Tests fuer backend/services/market_trends.py (#76, G.3.9).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.job import Job
from backend.services.market_trends import classify_job, get_market_trends


async def _job(
    db: AsyncSession,
    title: str,
    published_at: datetime | None = None,
    description: str | None = None,
    city: str | None = None,
    postal_code: str | None = None,
) -> Job:
    job = Job(
        title=title,
        company="Testfirma",
        description=description,
        published_at=published_at,
        city=city,
        postal_code=postal_code,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


class TestClassifyJob:
    def test_german_it_title(self):
        job = Job(title="Fachinformatiker Systemintegration (m/w/d)", company="X")
        assert classify_job(job) == "IT & Software"

    def test_french_it_title(self):
        job = Job(title="Developpeur Java (H/F)", company="X")
        assert classify_job(job) == "IT & Software"

    def test_swedish_it_title(self):
        job = Job(title="Senior Systemutvecklare inom .Net", company="X")
        assert classify_job(job) == "IT & Software"

    def test_healthcare_title(self):
        job = Job(title="Krankenpfleger (m/w/d) für die Intensivstation", company="X")
        assert classify_job(job) == "Gesundheit & Pflege"

    def test_falls_back_to_description_when_title_has_no_keyword(self):
        job = Job(title="Mitarbeiter (m/w/d)", company="X", description="Wir suchen einen Elektriker für unser Team.")
        assert classify_job(job) == "Handwerk & Bau"

    def test_unclassifiable_title_returns_sonstige(self):
        job = Job(title="Mitarbeiter (m/w/d)", company="X", description=None)
        assert classify_job(job) == "Sonstige"


@pytest.mark.asyncio
class TestGetMarketTrends:
    async def test_growing_category_detected(self, db: AsyncSession):
        now = datetime.now(timezone.utc)
        # "vorher"-Fenster (Tag 20): 1 IT-Job
        await _job(db, "Fachinformatiker", published_at=now - timedelta(days=20))
        # "aktuell"-Fenster (Tag 5): 3 IT-Jobs
        for _ in range(3):
            await _job(db, "Softwareentwickler", published_at=now - timedelta(days=5))

        result = await get_market_trends(db, days=30)

        it = next(b for b in result["branchen"] if b["branche"] == "IT & Software")
        assert it["vorher"] == 1
        assert it["aktuell"] == 3
        assert it["trend"] == "wachsend"
        assert it["veraenderung_prozent"] == 200.0

    async def test_new_category_has_none_percent_and_neu_trend(self, db: AsyncSession):
        now = datetime.now(timezone.utc)
        await _job(db, "Elektriker gesucht", published_at=now - timedelta(days=2))

        result = await get_market_trends(db, days=30)

        handwerk = next(b for b in result["branchen"] if b["branche"] == "Handwerk & Bau")
        assert handwerk["vorher"] == 0
        assert handwerk["veraenderung_prozent"] is None
        assert handwerk["trend"] == "neu"
        assert handwerk in result["top_wachsend"]

    async def test_shrinking_category_detected(self, db: AsyncSession):
        now = datetime.now(timezone.utc)
        for _ in range(4):
            await _job(db, "Fachinformatiker", published_at=now - timedelta(days=20))
        await _job(db, "IT-Administrator", published_at=now - timedelta(days=5))

        result = await get_market_trends(db, days=30)

        it = next(b for b in result["branchen"] if b["branche"] == "IT & Software")
        assert it["trend"] == "schrumpfend"
        assert it in result["top_schrumpfend"]

    async def test_jobs_outside_window_excluded(self, db: AsyncSession):
        now = datetime.now(timezone.utc)
        await _job(db, "Fachinformatiker", published_at=now - timedelta(days=90))

        result = await get_market_trends(db, days=30)

        assert result["branchen"] == []

    async def test_falls_back_to_created_at_when_published_at_missing(self, db: AsyncSession):
        job = await _job(db, "Fachinformatiker", published_at=None)
        assert job.created_at is not None

        result = await get_market_trends(db, days=30)

        assert any(b["branche"] == "IT & Software" for b in result["branchen"])

    async def test_city_filter_narrows_results(self, db: AsyncSession):
        now = datetime.now(timezone.utc)
        await _job(db, "Fachinformatiker", published_at=now - timedelta(days=5), city="Köln")
        await _job(db, "Elektriker", published_at=now - timedelta(days=5), city="München")

        result = await get_market_trends(db, days=30, city="Köln")

        branchen = {b["branche"] for b in result["branchen"]}
        assert branchen == {"IT & Software"}

    async def test_postal_code_filter_narrows_results(self, db: AsyncSession):
        now = datetime.now(timezone.utc)
        await _job(db, "Fachinformatiker", published_at=now - timedelta(days=5), postal_code="50667")
        await _job(db, "Elektriker", published_at=now - timedelta(days=5), postal_code="80331")

        result = await get_market_trends(db, days=30, postal_code="506")

        branchen = {b["branche"] for b in result["branchen"]}
        assert branchen == {"IT & Software"}

    async def test_no_jobs_returns_empty_lists(self, db: AsyncSession):
        result = await get_market_trends(db, days=30)

        assert result == {
            "zeitraum_tage": 30,
            "branchen": [],
            "top_wachsend": [],
            "top_schrumpfend": [],
        }
