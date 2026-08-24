"""
Tests fuer backend/services/followup_scheduler.py (Issue #64).

Testgruppen:
  - Unit-Tests: berechne_ampel(), tage_bis_faellig(), generiere_nachfass_vorlage()
  - Integration-Tests (In-Memory-DB): CRUD-Funktionen, Dashboard-Stats

Ausfuehren::

    cd backend
    pytest tests/test_followup_scheduler.py -v
"""
from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import Application, Job, FollowUp
from backend.services.followup_scheduler import (
    aktualisiere_followup,
    berechne_ampel,
    berechne_dashboard_stats,
    erstelle_followup,
    generiere_nachfass_vorlage,
    hole_followups_fuer_bewerbung,
    loesche_followup,
    markiere_erledigt,
    tage_bis_faellig,
)

# pytest.ini setzt asyncio_mode = auto - async Tests werden automatisch
# erkannt, ein globales pytestmark = pytest.mark.asyncio wuerde faelschlich
# auch auf die synchronen Unit-Tests (TestBerechneAmpel u.a.) angewandt und
# PytestWarning fuer jeden davon erzeugen.


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _make_followup(days_from_now: float, erledigt: bool = False) -> FollowUp:
    """Erstellt ein nicht-persistiertes FollowUp-Objekt fuer Unit-Tests."""
    fw = FollowUp()
    fw.faellig_am = datetime.utcnow() + timedelta(days=days_from_now)
    fw.erledigt   = erledigt
    fw.notiz      = None
    fw.erledigt_am = None
    return fw


async def _seed_application(db: AsyncSession) -> int:
    """Legt einen minimalen Job + Application an und gibt die application.id zurueck."""
    job = Job(title="IT-Support Specialist", company="Dataport AoeR")
    db.add(job)
    await db.flush()  # id benoetigt

    app = Application(job_id=job.id, status="beworben")
    db.add(app)
    await db.flush()
    return app.id


# ===========================================================================
# UNIT-TESTS: berechne_ampel()
# ===========================================================================

class TestBerechneAmpel:
    def test_erledigt_gibt_done(self):
        fw = _make_followup(days_from_now=5, erledigt=True)
        assert berechne_ampel(fw) == "done"

    def test_heute_gibt_urgent(self):
        fw = _make_followup(days_from_now=0)
        assert berechne_ampel(fw) == "urgent"

    def test_ueberfaellig_gibt_urgent(self):
        fw = _make_followup(days_from_now=-3)
        assert berechne_ampel(fw) == "urgent"

    def test_morgen_gibt_soon(self):
        fw = _make_followup(days_from_now=1)
        assert berechne_ampel(fw) == "soon"

    def test_uebermorgen_gibt_later(self):
        fw = _make_followup(days_from_now=2)
        assert berechne_ampel(fw) == "later"

    def test_weit_in_zukunft_gibt_later(self):
        fw = _make_followup(days_from_now=30)
        assert berechne_ampel(fw) == "later"


# ===========================================================================
# UNIT-TESTS: tage_bis_faellig()
# ===========================================================================

class TestTageBisFaellig:
    def test_heute_ist_null(self):
        fw = _make_followup(days_from_now=0)
        assert tage_bis_faellig(fw) == 0

    def test_morgen_ist_eins(self):
        fw = _make_followup(days_from_now=1)
        assert tage_bis_faellig(fw) == 1

    def test_ueberfaellig_ist_negativ(self):
        fw = _make_followup(days_from_now=-2)
        assert tage_bis_faellig(fw) == -2


# ===========================================================================
# UNIT-TESTS: generiere_nachfass_vorlage()
# ===========================================================================

class TestGeneriereNachfassVorlage:
    def test_enthaelt_stelle_und_firma(self):
        text = generiere_nachfass_vorlage(stelle="IT-Support", firma="Dataport")
        assert "IT-Support" in text
        assert "Dataport" in text

    def test_default_anrede(self):
        text = generiere_nachfass_vorlage(stelle="Admin", firma="TechCorp")
        assert "Sehr geehrte Damen und Herren" in text

    def test_custom_anrede(self):
        text = generiere_nachfass_vorlage(
            stelle="Admin", firma="TechCorp", anrede="Sehr geehrte Frau Muster"
        )
        assert "Frau Muster" in text

    def test_enthaelt_abschlussformel(self):
        text = generiere_nachfass_vorlage(stelle="X", firma="Y")
        assert "Mit freundlichen Gruessen" in text


# ===========================================================================
# INTEGRATION-TESTS: CRUD
# ===========================================================================

class TestCrud:
    async def test_erstelle_followup_persistiert(self, db: AsyncSession):
        app_id = await _seed_application(db)
        fw = await erstelle_followup(db, application_id=app_id, tage=7, notiz="Bitte nachfassen")

        assert fw.id is not None
        assert fw.erledigt is False
        assert fw.notiz == "Bitte nachfassen"
        # Faelligkeit muss in etwa 7 Tagen liegen (+/- 5 Sekunden Toleranz)
        expected = datetime.utcnow() + timedelta(days=7)
        diff = abs((fw.faellig_am - expected).total_seconds())
        assert diff < 5

    async def test_markiere_erledigt_setzt_flag(self, db: AsyncSession):
        app_id = await _seed_application(db)
        fw = await erstelle_followup(db, application_id=app_id, tage=3)
        updated = await markiere_erledigt(db, fw.id)

        assert updated is not None
        assert updated.erledigt is True
        assert updated.erledigt_am is not None

    async def test_markiere_erledigt_nicht_gefunden(self, db: AsyncSession):
        result = await markiere_erledigt(db, followup_id=99999)
        assert result is None

    async def test_aktualisiere_notiz(self, db: AsyncSession):
        app_id = await _seed_application(db)
        fw = await erstelle_followup(db, application_id=app_id, tage=5)
        updated = await aktualisiere_followup(db, fw.id, notiz="Neue Notiz")

        assert updated is not None
        assert updated.notiz == "Neue Notiz"

    async def test_aktualisiere_tage_verschiebt_faelligket(self, db: AsyncSession):
        app_id = await _seed_application(db)
        fw = await erstelle_followup(db, application_id=app_id, tage=1)
        updated = await aktualisiere_followup(db, fw.id, tage=14)

        assert updated is not None
        expected = datetime.utcnow() + timedelta(days=14)
        diff = abs((updated.faellig_am - expected).total_seconds())
        assert diff < 5

    async def test_loesche_followup(self, db: AsyncSession):
        app_id = await _seed_application(db)
        fw = await erstelle_followup(db, application_id=app_id, tage=2)
        deleted = await loesche_followup(db, fw.id)
        assert deleted is True

        # Nochmal loeschen liefert False
        deleted_again = await loesche_followup(db, fw.id)
        assert deleted_again is False

    async def test_hole_followups_fuer_bewerbung_nur_offene(self, db: AsyncSession):
        app_id = await _seed_application(db)
        fw1 = await erstelle_followup(db, application_id=app_id, tage=1)
        fw2 = await erstelle_followup(db, application_id=app_id, tage=3)
        await markiere_erledigt(db, fw1.id)

        offene = await hole_followups_fuer_bewerbung(db, app_id, nur_offene=True)
        ids = [f.id for f in offene]
        assert fw1.id not in ids
        assert fw2.id in ids


# ===========================================================================
# INTEGRATION-TESTS: Dashboard-Stats
# ===========================================================================

class TestDashboardStats:
    async def test_leere_db_gibt_nullen(self, db: AsyncSession):
        stats = await berechne_dashboard_stats(db)
        assert stats["urgent"]       == 0
        assert stats["soon"]         == 0
        assert stats["later"]        == 0
        assert stats["gesamt_offen"] == 0

    async def test_stats_zaehlt_korrekt(self, db: AsyncSession):
        app_id = await _seed_application(db)

        # 2x urgent (ueberfaellig)
        await erstelle_followup(db, application_id=app_id, tage=0)
        await erstelle_followup(db, application_id=app_id, tage=0)
        # 1x soon  (morgen) – wir mocken den Scheduler intern nicht,
        # stattdessen setzen wir faellig_am direkt nach dem Anlegen
        fw_soon = await erstelle_followup(db, application_id=app_id, tage=99)
        fw_soon.faellig_am = datetime.utcnow() + timedelta(days=1)
        await db.commit()
        # 1x later
        await erstelle_followup(db, application_id=app_id, tage=5)

        stats = await berechne_dashboard_stats(db)
        assert stats["urgent"]       == 2
        assert stats["soon"]         == 1
        assert stats["later"]        == 1
        assert stats["gesamt_offen"] == 4
        assert stats["done"]         == 0
