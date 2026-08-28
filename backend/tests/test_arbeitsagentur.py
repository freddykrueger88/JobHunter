"""
Tests fuer backend/services/job_search/arbeitsagentur.py.

Migration v4 -> v6 (2026-08-28): die alte pc/v4/jobs-URL liefert seit
kurzem HTTP 403 (live mit rohem httpx reproduziert, auch von komplett
anderer Infrastruktur aus - kein Problem dieses Deployments, ein echter
Umzug auf pc/v6/jobs mit substanziell anderem Response-Schema, siehe
Moduldoku in arbeitsagentur.py). Anders als beim v4-Schema liefert die
Suche selbst keine Stellenbeschreibung mehr mit - die wird pro Treffer
per separatem Request (pc/v4/jobdetails/{base64(referenznummer)})
nachgeladen, parallelisiert per asyncio.gather.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.services.job_search.arbeitsagentur import ArbeitsagenturSource

pytestmark = pytest.mark.asyncio


def _search_response(items: list[dict]):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"ergebnisliste": items}
    return mock_response


def _details_response(beschreibung: str | None):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"stellenangebotsBeschreibung": beschreibung} if beschreibung is not None else {}
    return mock_response


def _mock_client(search_items: list[dict], descriptions: dict[str, str] | None = None):
    """search_items -> Antwort auf pc/v6/jobs, descriptions (refnr -> Text)
    -> Antworten auf die parallelen pc/v4/jobdetails/{code}-Requests."""
    descriptions = descriptions or {}

    async def _get(url, **kwargs):
        if "jobdetails" in url:
            # Der Code im Pfad ist base64(refnr) - fuer den Test reicht es,
            # anhand der Reihenfolge zu antworten statt zu dekodieren.
            return _details_response(descriptions.get(_get.next_refnr.pop(0)))
        return _search_response(search_items)

    _get.next_refnr = [item.get("referenznummer") for item in search_items]

    mock_client = MagicMock()
    mock_client.get = AsyncMock(side_effect=_get)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


class TestArbeitsagenturSource:
    async def test_returns_normalized_jobs_with_description(self):
        items = [{
            "stellenangebotsTitel": "Softwareentwickler (m/w/d)",
            "firma": "bayoonet AG",
            "referenznummer": "12117-YF-48852-YF-S",
            "stellenangebotsart": "ARBEIT",
            "arbeitszeitVollzeit": True,
            "datumErsteVeroeffentlichung": "2026-08-19",
            "stellenlokationen": [{
                "adresse": {"plz": "10115", "ort": "Berlin", "strasse": "Musterstr. 1"},
                "breite": 52.53,
                "laenge": 13.38,
            }],
        }]
        mock_client = _mock_client(items, descriptions={"12117-YF-48852-YF-S": "Eine tolle Stelle."})

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await ArbeitsagenturSource().search("Softwareentwickler", "Berlin", 25)

        assert len(results) == 1
        job = results[0]
        assert job.title == "Softwareentwickler (m/w/d)"
        assert job.company == "bayoonet AG"
        assert job.city == "Berlin"
        assert job.postal_code == "10115"
        assert job.address == "Musterstr. 1"
        assert job.description == "Eine tolle Stelle."
        assert job.url == "https://www.arbeitsagentur.de/jobsuche/jobdetail/12117-YF-48852-YF-S"
        assert job.job_type == "vollzeit"
        assert job.external_id == "12117-YF-48852-YF-S"
        assert job.latitude == 52.53
        assert job.longitude == 13.38
        assert job.published_at is not None

    async def test_ausbildung_maps_to_ausbildung_job_type(self):
        items = [{
            "stellenangebotsTitel": "Ausbildung zum Verkäufer",
            "firma": "X GmbH",
            "referenznummer": "abc",
            "stellenangebotsart": "AUSBILDUNG",
        }]
        mock_client = _mock_client(items)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await ArbeitsagenturSource().search("Verkäufer", "", 25)

        assert results[0].job_type == "ausbildung"

    async def test_teilzeit_flag_maps_to_teilzeit(self):
        items = [{
            "stellenangebotsTitel": "Teilzeit-Job",
            "firma": "X GmbH",
            "referenznummer": "abc",
            "stellenangebotsart": "ARBEIT",
            "arbeitszeitVollzeit": False,
            "arbeitszeitTeilzeitVormittag": True,
        }]
        mock_client = _mock_client(items)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await ArbeitsagenturSource().search("x", "", 25)

        assert results[0].job_type == "teilzeit"

    async def test_missing_referenznummer_yields_no_url_and_no_external_id(self):
        items = [{"stellenangebotsTitel": "Ohne Referenznummer", "firma": "X"}]
        mock_client = _mock_client(items)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await ArbeitsagenturSource().search("x", "", 25)

        assert results[0].url is None
        assert results[0].external_id is None

    async def test_missing_stellenlokationen_does_not_crash(self):
        items = [{"stellenangebotsTitel": "Ohne Ort", "firma": "X", "referenznummer": "abc"}]
        mock_client = _mock_client(items)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await ArbeitsagenturSource().search("x", "", 25)

        assert results[0].city is None

    async def test_empty_ergebnisliste_yields_no_jobs(self):
        mock_client = _mock_client([])

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await ArbeitsagenturSource().search("x", "", 25)

        assert results == []

    async def test_http_error_on_search_returns_empty_list(self):
        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=Exception("boom"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await ArbeitsagenturSource().search("x", "", 25)

        assert results == []

    async def test_failed_description_fetch_leaves_description_none_not_crash(self):
        items = [{
            "stellenangebotsTitel": "Job ohne ladbare Beschreibung",
            "firma": "X",
            "referenznummer": "abc",
        }]

        async def _get(url, **kwargs):
            if "jobdetails" in url:
                raise Exception("boom")
            return _search_response(items)

        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=_get)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await ArbeitsagenturSource().search("x", "", 25)

        assert len(results) == 1
        assert results[0].description is None
