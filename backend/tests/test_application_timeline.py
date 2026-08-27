"""
Tests fuer backend/services/application_timeline.py (#83, G.3.3).

Prueft die Verweildauer-Berechnung direkt mit kontrollierten
Zeitstempeln, statt sich nur auf die grobe End-to-End-Pruefung ueber
den Timeline-Endpoint zu verlassen (siehe test_applications.py::
TestTimelineAverages fuer die API-Ebene).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.application_status_log import ApplicationStatusLog
from backend.services.application_timeline import get_avg_days_by_status

pytestmark = pytest.mark.asyncio


async def _add_log(db: AsyncSession, app_id: int, status: str, changed_at: datetime) -> None:
    db.add(ApplicationStatusLog(application_id=app_id, status=status, changed_at=changed_at))
    await db.commit()


class TestGetAvgDaysByStatus:
    async def test_computes_duration_between_consecutive_entries(self, db: AsyncSession):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        await _add_log(db, 1, "interessant", base)
        await _add_log(db, 1, "beworben", base + timedelta(days=3))

        avg = await get_avg_days_by_status(db)

        assert avg["interessant"] == 3.0

    async def test_last_status_measured_against_now(self, db: AsyncSession):
        now = datetime.now(timezone.utc)
        await _add_log(db, 1, "interessant", now - timedelta(days=2))

        avg = await get_avg_days_by_status(db)

        # ~2 Tage bis jetzt, kleine Toleranz fuer Testlaufzeit
        assert 1.9 <= avg["interessant"] <= 2.1

    async def test_averages_across_multiple_applications(self, db: AsyncSession):
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        await _add_log(db, 1, "interessant", base)
        await _add_log(db, 1, "beworben", base + timedelta(days=2))
        await _add_log(db, 2, "interessant", base)
        await _add_log(db, 2, "beworben", base + timedelta(days=6))

        avg = await get_avg_days_by_status(db)

        assert avg["interessant"] == 4.0  # (2 + 6) / 2

    async def test_empty_log_returns_empty_dict(self, db: AsyncSession):
        avg = await get_avg_days_by_status(db)

        assert avg == {}

    async def test_zero_duration_for_simultaneous_entries(self, db: AsyncSession):
        """Zwei Statuswechsel mit identischem Zeitstempel (z.B. Status
        direkt bei Anlage schon nicht "interessant") ergeben 0 statt
        eines negativen oder unendlichen Werts."""
        base = datetime(2026, 1, 1, tzinfo=timezone.utc)
        await _add_log(db, 1, "interessant", base)
        await _add_log(db, 1, "beworben", base)

        avg = await get_avg_days_by_status(db)

        assert avg["interessant"] == 0.0
