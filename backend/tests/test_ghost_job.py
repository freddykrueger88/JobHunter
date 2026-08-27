"""
Tests fuer den ghost_job-computed_field auf JobRead (Bugfix-Sweep
2026-08-27).

GhostJobBadge.tsx war fertig gebaut, bekam sein `result` aber nirgends
geliefert - kein Backend-Feld existierte. detect_ghost_job() ist rein
deterministisch (kein KI-Call), deshalb als computed_field direkt in
JobRead berechnet statt in einem eigenen Endpoint.

Kritischer Fund dabei: detect_ghost_job() verglich datetime.utcnow()
(naiv) mit Job.published_at (timezone-aware DB-Spalte) - haette bei
jedem Job mit gesetztem published_at "can't subtract offset-naive and
offset-aware datetimes" geworfen und damit GET /api/jobs/ komplett
lahmgelegt, sobald irgendein zurueckgegebener Job ein Veroeffentlichungs-
datum hat.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.job import Job

pytestmark = pytest.mark.asyncio


class TestGhostJobField:
    async def test_list_jobs_with_timezone_aware_published_at_does_not_crash(
        self, client: httpx.AsyncClient, db: AsyncSession,
    ):
        """Regression: datetime.utcnow() (naiv) vs. published_at (aware)."""
        job = Job(
            title="Backend Engineer",
            company="Beispiel GmbH",
            description="Kurz.",
            published_at=datetime.now(timezone.utc) - timedelta(days=45),
        )
        db.add(job)
        await db.commit()

        res = await client.get("/api/jobs/?hide_hidden=false")

        assert res.status_code == 200, res.text
        body = res.json()[0]
        assert body["ghost_job"]["ist_ghost_job"] is True
        assert any("Tage alt" in g for g in body["ghost_job"]["gruende"])

    async def test_complete_recent_listing_scores_low(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(
            title="Backend Engineer",
            company="Beispiel GmbH",
            description=(
                "Wir suchen eine erfahrene Backend-Entwicklerin mit fundierten Kenntnissen in "
                "Python, FastAPI und PostgreSQL. Sie arbeiten eng mit unserem zehnkoepfigen Team "
                "zusammen und uebernehmen Verantwortung fuer die Architektur unserer Kernplattform. "
                "Wir bieten ein Gehalt von 60000 bis 75000 EUR sowie flexible Arbeitszeiten und "
                "Homeoffice-Moeglichkeiten in einem stabilen, etablierten Unternehmen mit klaren "
                "Zustaendigkeiten und einem eingespielten Team."
            ),
            published_at=datetime.now(timezone.utc),
            contact_person="Julia Schmidt",
            salary_min=60000,
            salary_max=75000,
        )
        db.add(job)
        await db.commit()

        res = await client.get("/api/jobs/?hide_hidden=false")

        body = res.json()[0]
        assert body["ghost_job"]["ist_ghost_job"] is False

    async def test_get_single_job_includes_ghost_job(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Backend Engineer", company="Beispiel GmbH")
        db.add(job)
        await db.commit()
        await db.refresh(job)

        res = await client.get(f"/api/jobs/{job.id}")

        assert res.status_code == 200, res.text
        assert "ghost_job" in res.json()
