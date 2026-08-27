"""
Tests fuer backend/services/job_search/karriere_nrw.py.

Phase I.1 (EU-weite Jobboersen, Teil 2 - Portale unterhalb von EURES):
erster echter Fund auf Kommunalebene - eine offizielle, dokumentierte
Open-Data-API des Landes NRW fuer Land- und Kommunalstellen. Live gegen
echte Daten verifiziert (1105 offene Stellen insgesamt, u.a. von
kleinen Staedten wie Meerbusch/Kamen/Korschenbroich).

Kritischer Fund waehrend der Implementierung: der dokumentierte
ort-Parameter (PDF-Beispiel "ort=Bochum") liefert live 0 Ergebnisse,
selbst fuer Staedte mit nachweislich vorhandenen Treffern (z.B.
"ort=Krefeld" trotz eines Krefeld-Jobs im ungefilterten Datensatz) -
haette die Quelle in der echten App (die immer einen Ort mitschickt)
faktisch stumm gemacht. Deshalb reicht diese Quelle Ort/Radius bewusst
nicht durch, siehe test_search_does_not_send_broken_location_params.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.services.job_search.karriere_nrw import KarriereNrwSource

pytestmark = pytest.mark.asyncio


def _mock_response(items: list[dict], count: int | None = None):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"count": count if count is not None else len(items), "pages": 1, "items": items}
    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


class TestKarriereNrwSource:
    async def test_returns_normalized_jobs(self):
        items = [{
            "uuid": "040f0972-5e03-4e35-9f68-ab7a9d654d18",
            "title": "Sachbearbeiter/in (m/w/d) Straßenerhaltungsmanagement",
            "authority": "Stadt Krefeld",
            "location": "Krefeld",
            "jobtype": "joboffer",
            "published": "2026-07-06",
            "deadline": "2027-02-28",
        }]
        with patch("httpx.AsyncClient", return_value=_mock_response(items, count=1105)):
            results = await KarriereNrwSource().search("Sachbearbeiter", "Krefeld", 25)

        assert len(results) == 1
        job = results[0]
        assert job.title == "Sachbearbeiter/in (m/w/d) Straßenerhaltungsmanagement"
        assert job.company == "Stadt Krefeld"
        assert job.city == "Krefeld"
        assert job.source_portal == "karriere_nrw"
        assert job.external_id == "karriere_nrw_040f0972-5e03-4e35-9f68-ab7a9d654d18"
        # Verifiziert bestaetigt: der Detail-Endpoint liefert selbst genau
        # dieses URL-Muster fuer denselben Datensatz zurueck, siehe
        # Commit-Notiz - kein unverifizierter Konstruktionsversuch.
        assert job.url == "https://karriere.nrw/stellenausschreibung/040f0972-5e03-4e35-9f68-ab7a9d654d18"
        assert job.published_at is not None

    async def test_apprenticeship_jobtype_maps_to_ausbildung(self):
        items = [{"uuid": "x", "title": "Duales Studium", "authority": "Land NRW", "location": "Köln", "jobtype": "apprenticeship"}]
        with patch("httpx.AsyncClient", return_value=_mock_response(items)):
            results = await KarriereNrwSource().search("", "", 25)

        assert results[0].job_type == "ausbildung"

    async def test_search_does_not_send_broken_location_params(self):
        """Regression: ort/umkreis wurden entfernt, weil die Live-API mit
        ihnen 0 Ergebnisse liefert, selbst fuer Staedte mit vorhandenen
        Treffern."""
        mock_client = _mock_response([])
        with patch("httpx.AsyncClient", return_value=mock_client):
            await KarriereNrwSource().search("Sachbearbeiter", "Krefeld", 25)

        sent_params = mock_client.get.call_args.kwargs["params"]
        assert "ort" not in sent_params
        assert "umkreis" not in sent_params
        assert sent_params["text"] == "Sachbearbeiter"

    async def test_missing_uuid_yields_no_url_and_no_external_id(self):
        items = [{"title": "Ohne UUID", "authority": "X", "location": "Y"}]
        with patch("httpx.AsyncClient", return_value=_mock_response(items)):
            results = await KarriereNrwSource().search("x", "", 25)

        assert results[0].url is None
        assert results[0].external_id is None

    async def test_http_error_returns_empty_list(self):
        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=Exception("boom"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await KarriereNrwSource().search("x", "", 25)

        assert results == []
