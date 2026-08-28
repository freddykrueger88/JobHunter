"""
Tests fuer backend/services/response_rate_analyzer.py (#78, G.3.8).
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.application import Application
from backend.models.cover_letter import CoverLetter
from backend.models.job import Job
from backend.services.response_rate_analyzer import get_response_rate_analysis

pytestmark = pytest.mark.asyncio


async def _job(db: AsyncSession, source_portal: str | None) -> Job:
    job = Job(title="Testjob", company="Testfirma", source_portal=source_portal)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def _application(
    db: AsyncSession,
    job: Job,
    status: str,
    applied_at: datetime | None = None,
) -> Application:
    app = Application(job_id=job.id, status=status, applied_at=applied_at)
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return app


class TestByPortal:
    async def test_counts_responded_vs_total_per_portal(self, db: AsyncSession):
        stepstone = await _job(db, "stepstone")
        linkedin = await _job(db, "linkedin")
        await _application(db, stepstone, "interview")
        await _application(db, stepstone, "beworben")
        await _application(db, linkedin, "absage")

        result = await get_response_rate_analysis(db)

        by_key = {e["key"]: e for e in result["by_portal"]}
        assert by_key["stepstone"] == {"key": "stepstone", "total": 2, "beantwortet": 1, "quote": 50.0}
        assert by_key["linkedin"] == {"key": "linkedin", "total": 1, "beantwortet": 1, "quote": 100.0}

    async def test_interessant_status_excluded_entirely(self, db: AsyncSession):
        job = await _job(db, "adzuna")
        await _application(db, job, "interessant")

        result = await get_response_rate_analysis(db)

        assert result["by_portal"] == []

    async def test_missing_source_portal_grouped_as_unbekannt(self, db: AsyncSession):
        job = await _job(db, None)
        await _application(db, job, "beworben")

        result = await get_response_rate_analysis(db)

        assert result["by_portal"][0]["key"] == "unbekannt"


class TestByWeekday:
    async def test_uses_applied_at_when_set(self, db: AsyncSession):
        job = await _job(db, "arbeitsagentur")
        monday = datetime(2026, 8, 24, tzinfo=timezone.utc)  # ist ein Montag
        await _application(db, job, "interview", applied_at=monday)

        result = await get_response_rate_analysis(db)

        montag = next(e for e in result["by_weekday"] if e["key"] == 0)
        assert montag["total"] == 1
        assert montag["beantwortet"] == 1

    async def test_falls_back_to_created_at_when_applied_at_missing(self, db: AsyncSession):
        job = await _job(db, "arbeitsagentur")
        app = await _application(db, job, "beworben")
        assert app.created_at is not None  # server_default beim Insert gesetzt

        result = await get_response_rate_analysis(db)

        total_across_weekdays = sum(e["total"] for e in result["by_weekday"])
        assert total_across_weekdays == 1

    async def test_always_returns_all_seven_weekdays(self, db: AsyncSession):
        result = await get_response_rate_analysis(db)

        assert [e["key"] for e in result["by_weekday"]] == list(range(7))


class TestByCoverLetterLength:
    async def test_buckets_by_word_count(self, db: AsyncSession):
        job = await _job(db, "stepstone")
        kurz = await _application(db, job, "beworben")
        lang = await _application(db, job, "interview")

        db.add(CoverLetter(application_id=kurz.id, content=" ".join(["Wort"] * 50)))
        db.add(CoverLetter(application_id=lang.id, content=" ".join(["Wort"] * 400)))
        await db.commit()

        result = await get_response_rate_analysis(db)

        by_key = {e["key"]: e for e in result["by_cover_letter_length"]}
        assert by_key["kurz"]["total"] == 1
        assert by_key["kurz"]["beantwortet"] == 0
        assert by_key["lang"]["total"] == 1
        assert by_key["lang"]["beantwortet"] == 1

    async def test_application_without_cover_letter_not_counted(self, db: AsyncSession):
        job = await _job(db, "stepstone")
        await _application(db, job, "beworben")

        result = await get_response_rate_analysis(db)

        assert all(e["total"] == 0 for e in result["by_cover_letter_length"])

    async def test_only_newest_cover_letter_counted_per_application(self, db: AsyncSession):
        job = await _job(db, "stepstone")
        app = await _application(db, job, "beworben")
        db.add(CoverLetter(application_id=app.id, content=" ".join(["Wort"] * 400)))
        await db.commit()
        db.add(CoverLetter(application_id=app.id, content=" ".join(["Wort"] * 50)))  # neuer, kuerzer
        await db.commit()

        result = await get_response_rate_analysis(db)

        by_key = {e["key"]: e for e in result["by_cover_letter_length"]}
        assert by_key["kurz"]["total"] == 1
        assert by_key["lang"]["total"] == 0


class TestRecommendations:
    async def test_no_recommendation_below_minimum_sample_size(self, db: AsyncSession):
        stepstone = await _job(db, "stepstone")
        linkedin = await _job(db, "linkedin")
        await _application(db, stepstone, "interview")
        await _application(db, linkedin, "beworben")

        result = await get_response_rate_analysis(db)

        assert result["empfehlungen"] == []

    async def test_recommendation_appears_once_both_sides_have_enough_samples(self, db: AsyncSession):
        stepstone = await _job(db, "stepstone")
        linkedin = await _job(db, "linkedin")
        for _ in range(3):
            await _application(db, stepstone, "interview")
        for _ in range(3):
            await _application(db, linkedin, "beworben")

        result = await get_response_rate_analysis(db)

        assert any("stepstone" in e for e in result["empfehlungen"])

    async def test_no_recommendation_when_no_applications_at_all(self, db: AsyncSession):
        result = await get_response_rate_analysis(db)

        assert result["empfehlungen"] == []
