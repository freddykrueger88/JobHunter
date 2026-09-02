"""
Tests fuer die Benefit-Whitelist/Keyword-Blacklist-Filter (#88, G.3.1) in
GET /api/jobs/.

Beide Filter arbeiten als Freitext-Suche gegen Titel UND Beschreibung
(case-insensitive, Komma-getrennte Begriffsliste):
- benefit_keywords: nur Stellen zeigen, die MINDESTENS EINEN der Begriffe
  enthalten (ODER-Verknuepfung).
- blacklist_keywords: Stellen mit IRGENDEINEM der Begriffe ausblenden
  (UND-NOT-Verknuepfung - jeder einzelne Begriff darf nicht vorkommen).
"""
from __future__ import annotations

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.job import Job

pytestmark = pytest.mark.asyncio


async def _make_job(db: AsyncSession, **kwargs) -> Job:
    defaults = dict(title="Testjob", company="Testfirma", description=None, is_hidden=False)
    defaults.update(kwargs)
    job = Job(**defaults)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


class TestBenefitWhitelist:
    async def test_matches_description(self, client: httpx.AsyncClient, db: AsyncSession):
        await _make_job(db, title="Softwareentwickler", description="Wir bieten Homeoffice und flexible Arbeitszeiten.")
        await _make_job(db, title="Buchhalter", description="Vor-Ort-Taetigkeit, kein Homeoffice.")

        res = await client.get("/api/jobs/", params={"benefit_keywords": "Homeoffice"})

        assert res.status_code == 200, res.text
        titles = [j["title"] for j in res.json()]
        assert "Softwareentwickler" in titles
        assert "Buchhalter" in titles  # enthaelt "Homeoffice" ebenfalls im Text (Verneinung), bewusst nur Substring-Match

    async def test_matches_title(self, client: httpx.AsyncClient, db: AsyncSession):
        await _make_job(db, title="Ausbildung Fachinformatiker", description=None)
        await _make_job(db, title="Vertriebsleiter", description="Reisebereitschaft erforderlich.")

        res = await client.get("/api/jobs/", params={"benefit_keywords": "Ausbildung"})

        titles = [j["title"] for j in res.json()]
        assert titles == ["Ausbildung Fachinformatiker"]

    async def test_or_semantics_across_multiple_keywords(self, client: httpx.AsyncClient, db: AsyncSession):
        await _make_job(db, title="Job A", description="Dienstwagen inklusive.")
        await _make_job(db, title="Job B", description="30 Tage Urlaub.")
        await _make_job(db, title="Job C", description="Keine Benefits erwaehnt.")

        res = await client.get("/api/jobs/", params={"benefit_keywords": "Dienstwagen, Urlaub"})

        titles = {j["title"] for j in res.json()}
        assert titles == {"Job A", "Job B"}

    async def test_case_insensitive(self, client: httpx.AsyncClient, db: AsyncSession):
        await _make_job(db, title="Job", description="HOMEOFFICE moeglich")

        res = await client.get("/api/jobs/", params={"benefit_keywords": "homeoffice"})

        assert len(res.json()) == 1

    async def test_no_filter_returns_all(self, client: httpx.AsyncClient, db: AsyncSession):
        await _make_job(db, title="Job A")
        await _make_job(db, title="Job B")

        res = await client.get("/api/jobs/")

        assert len(res.json()) == 2


class TestBlacklist:
    async def test_excludes_matching_title(self, client: httpx.AsyncClient, db: AsyncSession):
        await _make_job(db, title="Callcenter-Agent", description=None)
        await _make_job(db, title="Data Engineer", description=None)

        res = await client.get("/api/jobs/", params={"blacklist_keywords": "Callcenter"})

        titles = [j["title"] for j in res.json()]
        assert titles == ["Data Engineer"]

    async def test_excludes_matching_description(self, client: httpx.AsyncClient, db: AsyncSession):
        await _make_job(db, title="Job A", description="Taetigkeit ueber eine Zeitarbeitsfirma.")
        await _make_job(db, title="Job B", description="Festanstellung direkt beim Unternehmen.")

        res = await client.get("/api/jobs/", params={"blacklist_keywords": "Zeitarbeit"})

        titles = [j["title"] for j in res.json()]
        assert titles == ["Job B"]

    async def test_null_description_is_not_excluded(self, client: httpx.AsyncClient, db: AsyncSession):
        await _make_job(db, title="Job ohne Beschreibung", description=None)

        res = await client.get("/api/jobs/", params={"blacklist_keywords": "irgendwas"})

        assert len(res.json()) == 1

    async def test_multiple_keywords_each_excludes(self, client: httpx.AsyncClient, db: AsyncSession):
        await _make_job(db, title="Job A", description="Schichtarbeit")
        await _make_job(db, title="Job B", description="Zeitarbeit")
        await _make_job(db, title="Job C", description="Normale Festanstellung")

        res = await client.get("/api/jobs/", params={"blacklist_keywords": "Schichtarbeit, Zeitarbeit"})

        titles = [j["title"] for j in res.json()]
        assert titles == ["Job C"]


class TestHideZeitarbeit:
    """Nutzerwunsch 2026-09-02 - Zeitarbeitsfirmen/private Arbeitsvermittler
    sollen standardmaessig (hide_zeitarbeit default True) ausgeblendet
    werden, Erkennung ueber Firmennamen-Abgleich gegen eine feste
    Begriffsliste (backend/services/job_search/zeitarbeit_keywords.py)."""

    async def test_default_hides_known_agency(self, client: httpx.AsyncClient, db: AsyncSession):
        await _make_job(db, title="Lagerhelfer", company="Randstad Deutschland GmbH")
        await _make_job(db, title="Lagerhelfer", company="Muster GmbH")

        res = await client.get("/api/jobs/")

        companies = [j["company"] for j in res.json()]
        assert companies == ["Muster GmbH"]

    async def test_default_hides_structural_keyword(self, client: httpx.AsyncClient, db: AsyncSession):
        await _make_job(db, title="Bürokraft", company="ABC Personaldienstleistungen GmbH")
        await _make_job(db, title="Bürokraft", company="Muster GmbH")

        res = await client.get("/api/jobs/")

        companies = [j["company"] for j in res.json()]
        assert companies == ["Muster GmbH"]

    async def test_case_insensitive(self, client: httpx.AsyncClient, db: AsyncSession):
        await _make_job(db, title="Job", company="ZEITARBEIT XYZ")

        res = await client.get("/api/jobs/")

        assert res.json() == []

    async def test_can_be_disabled(self, client: httpx.AsyncClient, db: AsyncSession):
        await _make_job(db, title="Lagerhelfer", company="Randstad Deutschland GmbH")

        res = await client.get("/api/jobs/", params={"hide_zeitarbeit": False})

        assert len(res.json()) == 1

    async def test_does_not_affect_unrelated_company_names(self, client: httpx.AsyncClient, db: AsyncSession):
        await _make_job(db, title="Job", company="Musterfirma AG")

        res = await client.get("/api/jobs/")

        assert len(res.json()) == 1


class TestCombinedFilters:
    async def test_whitelist_and_blacklist_together(self, client: httpx.AsyncClient, db: AsyncSession):
        await _make_job(db, title="Job A", description="Homeoffice, direkt angestellt.")
        await _make_job(db, title="Job B", description="Homeoffice ueber Zeitarbeitsfirma.")
        await _make_job(db, title="Job C", description="Vor-Ort-Taetigkeit im Buero.")

        res = await client.get("/api/jobs/", params={
            "benefit_keywords": "Homeoffice",
            "blacklist_keywords": "Zeitarbeit",
        })

        titles = [j["title"] for j in res.json()]
        assert titles == ["Job A"]

    async def test_hidden_jobs_stay_excluded_regardless_of_filters(self, client: httpx.AsyncClient, db: AsyncSession):
        await _make_job(db, title="Versteckter Job", description="Homeoffice", is_hidden=True)

        res = await client.get("/api/jobs/", params={"benefit_keywords": "Homeoffice"})

        assert res.json() == []
