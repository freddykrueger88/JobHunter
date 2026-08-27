"""
Tests fuer backend/routers/applications.py (Backlog Phase B.6).

Regressionsschutz fuer einen kritischen, beim manuellen Testen gefundenen
Bug: list_applications/get_application griffen auf job.location zu - ein
Feld, das auf dem Job-Modell nie existierte (dort heisst es city). Jeder
Aufruf von GET /api/applications/ crashte mit 500, sobald eine Bewerbung
zu einem existierenden Job vorlag - das betrifft direkt das Kanban-Board,
den Kernbestandteil der App. Derselbe Copy-Paste-Bug steckte auch in
backend/services/auto_apply.py und backend/routers/export.py (dort per
manuellem End-to-End-Test verifiziert, siehe BACKLOG.md Phase B.6).
"""
from __future__ import annotations

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.cover_letter import CoverLetter
from backend.models.job import Job

pytestmark = pytest.mark.asyncio


async def _create_job_and_application(client: httpx.AsyncClient, db: AsyncSession) -> tuple[int, int]:
    job = Job(title="Backend Engineer", company="Beispiel GmbH", city="Bremen")
    db.add(job)
    await db.commit()
    await db.refresh(job)

    res = await client.post("/api/applications/", json={"job_id": job.id})
    assert res.status_code == 200, res.text
    return job.id, res.json()["id"]


class TestListAndGet:
    async def test_list_applications_does_not_crash_with_existing_job(
        self, client: httpx.AsyncClient, db: AsyncSession,
    ):
        """Regression: 500 durch job.location (existiert nicht, korrekt: job.city)."""
        job_id, _ = await _create_job_and_application(client, db)

        res = await client.get("/api/applications/")

        assert res.status_code == 200, res.text
        body = res.json()
        assert len(body) == 1
        assert body[0]["job"] == {"title": "Backend Engineer", "company": "Beispiel GmbH", "city": "Bremen"}

    async def test_get_application_does_not_crash_with_existing_job(
        self, client: httpx.AsyncClient, db: AsyncSession,
    ):
        job_id, app_id = await _create_job_and_application(client, db)

        res = await client.get(f"/api/applications/{app_id}")

        assert res.status_code == 200, res.text
        assert res.json()["job"]["city"] == "Bremen"

    async def test_list_applications_handles_job_without_city(
        self, client: httpx.AsyncClient, db: AsyncSession,
    ):
        job = Job(title="Remote Job", company="Remote GmbH", city=None)
        db.add(job)
        await db.commit()
        await db.refresh(job)
        await client.post("/api/applications/", json={"job_id": job.id})

        res = await client.get("/api/applications/")

        assert res.status_code == 200, res.text
        assert res.json()[0]["job"]["city"] is None


class TestHasCoverLetter:
    """Bugfix-Sweep 2026-08-27: AutoApplyButton bekam bisher
    hasCoverLetter aus dem Bewerbungsstatus geraten (status !==
    'interessant') statt aus der Datenbank geprueft - zeigte faelschlich
    'Anschreiben enthalten', obwohl nie eines generiert wurde. list/get
    liefern jetzt has_cover_letter aus der cover_letters-Tabelle."""

    async def test_false_when_no_cover_letter_exists(self, client: httpx.AsyncClient, db: AsyncSession):
        job_id, app_id = await _create_job_and_application(client, db)
        await client.patch(f"/api/applications/{app_id}", json={"status": "beworben"})

        list_res = await client.get("/api/applications/")
        get_res = await client.get(f"/api/applications/{app_id}")

        assert list_res.json()[0]["has_cover_letter"] is False
        assert get_res.json()["has_cover_letter"] is False

    async def test_true_when_cover_letter_exists(self, client: httpx.AsyncClient, db: AsyncSession):
        job_id, app_id = await _create_job_and_application(client, db)
        db.add(CoverLetter(application_id=app_id, content="Sehr geehrte Damen und Herren..."))
        await db.commit()

        list_res = await client.get("/api/applications/")
        get_res = await client.get(f"/api/applications/{app_id}")

        assert list_res.json()[0]["has_cover_letter"] is True
        assert get_res.json()["has_cover_letter"] is True


class TestCreateAndUpdate:
    async def test_create_application(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Job", company="Firma")
        db.add(job)
        await db.commit()
        await db.refresh(job)

        res = await client.post("/api/applications/", json={"job_id": job.id, "status": "interessant"})

        assert res.status_code == 200, res.text
        body = res.json()
        assert body["job_id"] == job.id
        assert body["status"] == "interessant"
        assert "job" not in body  # ApplicationBase, keine Job-Relation im create-Response

    async def test_update_application_status(self, client: httpx.AsyncClient, db: AsyncSession):
        _, app_id = await _create_job_and_application(client, db)

        res = await client.patch(f"/api/applications/{app_id}", json={"status": "beworben"})

        assert res.status_code == 200, res.text
        assert res.json()["status"] == "beworben"

    async def test_get_nonexistent_application_returns_404(self, client: httpx.AsyncClient):
        res = await client.get("/api/applications/999999")
        assert res.status_code == 404

    async def test_update_application_interview_at_datetime_field(
        self, client: httpx.AsyncClient, db: AsyncSession,
    ):
        """Regression: HistoryEntry.meta=data.model_dump() (ohne mode="json")
        crashte mit 'Object of type datetime is not JSON serializable',
        sobald ein datetime-Feld (interview_at/applied_at) gepatcht wurde -
        betraf jedes Setzen eines Interview-Termins ueber Kanban."""
        _, app_id = await _create_job_and_application(client, db)

        res = await client.patch(
            f"/api/applications/{app_id}",
            json={"interview_at": "2026-09-01T10:00:00"},
        )

        assert res.status_code == 200, res.text
        assert res.json()["interview_at"] is not None


class TestTimeline:
    """Bugfix-Sweep 2026-08-27: Kanban.tsx rief GET /api/applications/{id}/
    timeline seit jeher fuer die Detail-Modal-Timeline auf - der Endpoint
    existierte nie (404, still ignoriert da der Frontend-Query-Default ein
    leeres Array ist). application_status_logs existierte als Modell ohne
    Migration und ohne dass je etwas hineingeschrieben wurde.

    #83/G.3.3 (spaetere Session): Response-Form von einem nackten Array
    auf {entries, avg_days_by_status} umgestellt, um den im Issue
    gewuenschten "Vergleich mit Durchschnittswerten" zu liefern - siehe
    TestTimelineAverages unten fuer die neuen Tests dazu."""

    async def test_timeline_logs_initial_status_on_create(
        self, client: httpx.AsyncClient, db: AsyncSession,
    ):
        _, app_id = await _create_job_and_application(client, db)

        res = await client.get(f"/api/applications/{app_id}/timeline")

        assert res.status_code == 200, res.text
        entries = res.json()["entries"]
        assert len(entries) == 1
        assert entries[0]["status"] == "interessant"

    async def test_timeline_logs_status_changes_in_order(
        self, client: httpx.AsyncClient, db: AsyncSession,
    ):
        _, app_id = await _create_job_and_application(client, db)

        await client.patch(f"/api/applications/{app_id}", json={"status": "beworben"})
        await client.patch(f"/api/applications/{app_id}", json={"status": "interview"})

        res = await client.get(f"/api/applications/{app_id}/timeline")

        assert res.status_code == 200, res.text
        statuses = [entry["status"] for entry in res.json()["entries"]]
        assert statuses == ["interessant", "beworben", "interview"]

    async def test_timeline_does_not_log_when_status_unchanged(
        self, client: httpx.AsyncClient, db: AsyncSession,
    ):
        _, app_id = await _create_job_and_application(client, db)

        await client.patch(f"/api/applications/{app_id}", json={"notes": "nur eine Notiz"})

        res = await client.get(f"/api/applications/{app_id}/timeline")

        assert len(res.json()["entries"]) == 1  # nur der initiale Eintrag aus create

    async def test_timeline_for_nonexistent_application_returns_404(self, client: httpx.AsyncClient):
        res = await client.get("/api/applications/999999/timeline")
        assert res.status_code == 404


class TestTimelineAverages:
    """#83/G.3.3: avg_days_by_status im Timeline-Response."""

    async def test_single_application_has_no_completed_stage_yet(
        self, client: httpx.AsyncClient, db: AsyncSession,
    ):
        """Eine einzelne, gerade erst angelegte Bewerbung hat noch keinen
        abgeschlossenen Statuswechsel - der Durchschnitt fuer 'interessant'
        existiert trotzdem (Dauer bis jetzt), ist aber >= 0."""
        _, app_id = await _create_job_and_application(client, db)

        res = await client.get(f"/api/applications/{app_id}/timeline")

        avg = res.json()["avg_days_by_status"]
        assert "interessant" in avg
        assert avg["interessant"] >= 0

    async def test_average_reflects_multiple_applications(
        self, client: httpx.AsyncClient, db: AsyncSession,
    ):
        """Zwei Bewerbungen wechseln von 'interessant' zu 'beworben' -
        der Durchschnitt fuer 'interessant' wird aus beiden Verweildauern
        gebildet, nicht nur aus der zuletzt abgefragten Bewerbung."""
        _, app_id_1 = await _create_job_and_application(client, db)
        _, app_id_2 = await _create_job_and_application(client, db)

        await client.patch(f"/api/applications/{app_id_1}", json={"status": "beworben"})
        await client.patch(f"/api/applications/{app_id_2}", json={"status": "beworben"})

        res = await client.get(f"/api/applications/{app_id_1}/timeline")

        avg = res.json()["avg_days_by_status"]
        assert "interessant" in avg
        assert "beworben" in avg  # aktueller Status beider Bewerbungen, Dauer bis jetzt

    async def test_avg_is_shared_across_all_applications_not_just_this_one(
        self, client: httpx.AsyncClient, db: AsyncSession,
    ):
        """Der Durchschnitt in der Timeline-Antwort von Bewerbung A
        beruecksichtigt auch den Statusverlauf von Bewerbung B - es ist
        eine globale Statistik, keine rein bewerbungsbezogene."""
        _, app_id_1 = await _create_job_and_application(client, db)
        _, app_id_2 = await _create_job_and_application(client, db)
        await client.patch(f"/api/applications/{app_id_2}", json={"status": "absage"})

        res = await client.get(f"/api/applications/{app_id_1}/timeline")

        avg = res.json()["avg_days_by_status"]
        assert "absage" in avg  # stammt nur aus Bewerbung 2s Verlauf
