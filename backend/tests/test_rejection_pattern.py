"""
Tests fuer backend/services/rejection_pattern.py (#73, G.3.12).
"""
from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.application import Application
from backend.models.job import Job
from backend.models.user_profile import UserProfile
from backend.services.rejection_pattern import get_rejection_patterns

pytestmark = pytest.mark.asyncio


async def _job(db: AsyncSession, title: str = "Testjob", skill_gap_score: int | None = None) -> Job:
    job = Job(title=title, company="Testfirma", skill_gap_score=skill_gap_score)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def _application(db: AsyncSession, job: Job, status: str, ats_score: int | None = None) -> Application:
    app = Application(job_id=job.id, status=status, ats_score=ats_score)
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return app


class TestSkillGapSignal:
    async def test_flags_notable_difference(self, db: AsyncSession):
        for _ in range(3):
            job = await _job(db, skill_gap_score=30)
            await _application(db, job, "absage")
        for _ in range(3):
            job = await _job(db, skill_gap_score=90)
            await _application(db, job, "interview")

        result = await get_rejection_patterns(db)

        skill_gap = next(s for s in result["signale"] if s["signal"] == "skill_gap")
        assert skill_gap["risiko_gruppe"]["absage_quote"] == 100.0
        assert skill_gap["referenz_gruppe"]["absage_quote"] == 0.0
        assert skill_gap["auffaellig"] is True
        assert any("Skill-Match" in e for e in result["empfehlungen"])

    async def test_not_flagged_below_min_sample(self, db: AsyncSession):
        job = await _job(db, skill_gap_score=30)
        await _application(db, job, "absage")
        job2 = await _job(db, skill_gap_score=90)
        await _application(db, job2, "interview")

        result = await get_rejection_patterns(db)

        skill_gap = next(s for s in result["signale"] if s["signal"] == "skill_gap")
        assert skill_gap["auffaellig"] is False

    async def test_no_difference_not_flagged(self, db: AsyncSession):
        for _ in range(3):
            job = await _job(db, skill_gap_score=30)
            await _application(db, job, "absage")
        for _ in range(3):
            job = await _job(db, skill_gap_score=90)
            await _application(db, job, "absage")

        result = await get_rejection_patterns(db)

        skill_gap = next(s for s in result["signale"] if s["signal"] == "skill_gap")
        assert skill_gap["auffaellig"] is False

    async def test_jobs_without_score_ignored(self, db: AsyncSession):
        job = await _job(db, skill_gap_score=None)
        await _application(db, job, "absage")

        result = await get_rejection_patterns(db)

        skill_gap = next(s for s in result["signale"] if s["signal"] == "skill_gap")
        assert skill_gap["risiko_gruppe"]["total"] == 0
        assert skill_gap["referenz_gruppe"]["total"] == 0


class TestAtsSignal:
    async def test_flags_notable_difference(self, db: AsyncSession):
        for _ in range(3):
            job = await _job(db)
            await _application(db, job, "absage", ats_score=20)
        for _ in range(3):
            job = await _job(db)
            await _application(db, job, "interview", ats_score=95)

        result = await get_rejection_patterns(db)

        ats = next(s for s in result["signale"] if s["signal"] == "ats")
        assert ats["auffaellig"] is True


class TestSeniorityGate:
    async def test_no_seniority_signal_without_profile_erfahrungsjahre(self, db: AsyncSession):
        job = await _job(db, title="Senior Developer")
        await _application(db, job, "absage")

        result = await get_rejection_patterns(db)

        assert not any(s["signal"] == "seniority" for s in result["signale"])

    async def test_flags_applying_above_own_level(self, db: AsyncSession):
        db.add(UserProfile(id=1, erfahrungsjahre=1))  # junior
        await db.commit()

        for _ in range(3):
            job = await _job(db, title="Senior Software Engineer")
            await _application(db, job, "absage")
        for _ in range(3):
            job = await _job(db, title="Junior Developer")
            await _application(db, job, "interview")

        result = await get_rejection_patterns(db)

        seniority = next(s for s in result["signale"] if s["signal"] == "seniority")
        assert seniority["risiko_gruppe"]["absage_quote"] == 100.0
        assert seniority["referenz_gruppe"]["absage_quote"] == 0.0
        assert seniority["auffaellig"] is True


class TestOverall:
    async def test_interessant_status_excluded(self, db: AsyncSession):
        job = await _job(db)
        await _application(db, job, "interessant")

        result = await get_rejection_patterns(db)

        assert result["gesamt_bewerbungen"] == 0

    async def test_genug_daten_flag(self, db: AsyncSession):
        job = await _job(db)
        for _ in range(5):
            await _application(db, job, "absage")

        result = await get_rejection_patterns(db)

        assert result["gesamt_absagen"] == 5
        assert result["genug_daten"] is False

    async def test_empty_db(self, db: AsyncSession):
        result = await get_rejection_patterns(db)

        assert result["gesamt_bewerbungen"] == 0
        assert result["gesamt_absagen"] == 0
        assert result["genug_daten"] is False
        assert result["empfehlungen"] == []
