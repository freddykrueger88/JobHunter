"""
Tests fuer backend/services/job_search/arbetsformedlingen.py.

Phase I.1 (EU-weite Jobboersen, Fortsetzung nach Deutschland/Frankreich):
Arbetsformedlingen (schwedische Arbeitsagentur, JobTech-Plattform) ist -
wie Arbeitsagentur/EURES/Karriere.NRW/service.bund.de - eine voellig
oeffentliche API ohne Nutzer-Key, live gegengetestet mit echten aktuellen
Stellenanzeigen (u.a. bestaetigt: "webpage_url" liefert direkt eine
gueltige Detail-URL, kein Konstruktionsversuch).

Ort-Filterung bewusst NICHT ueber den strikten "municipality"-Parameter
(braucht eine Taxonomy-Concept-ID statt Klartext, matched nur exakt
buchstabierte volle Gemeindenamen - live gegengetestet: "malm" statt
"Malmö" liefert 0 Treffer) - stattdessen wird der Ort mit ins Freitext-
Suchfeld "q" eingemischt, wie von der API selbst so vorgesehen (live
verifiziert: "utvecklare stockholm" lieferte ausschliesslich Stockholm-
Treffer), siehe test_location_is_blended_into_freetext_query.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.services.job_search.arbetsformedlingen import ArbetsformedlingenSource

pytestmark = pytest.mark.asyncio


def _mock_client(hits: list[dict]):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"total": {"value": len(hits)}, "hits": hits}
    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


class TestArbetsformedlingenSource:
    async def test_returns_normalized_jobs(self):
        hits = [{
            "id": "31281556",
            "headline": "Systemutvecklare",
            "employer": {"name": "Test AB"},
            "workplace_address": {
                "city": "Stockholm", "municipality": "Stockholm",
                "postcode": "11122", "coordinates": [18.0686, 59.3293],
            },
            "description": {"text": "En bra beskrivning"},
            "webpage_url": "https://arbetsformedlingen.se/platsbanken/annonser/31281556",
            "working_hours_type": {"label": "Heltid"},
            "publication_date": "2026-07-20T00:01:23",
        }]
        with patch("httpx.AsyncClient", return_value=_mock_client(hits)):
            results = await ArbetsformedlingenSource().search("utvecklare", "Stockholm", 25)

        assert len(results) == 1
        job = results[0]
        assert job.title == "Systemutvecklare"
        assert job.company == "Test AB"
        assert job.city == "Stockholm"
        assert job.postal_code == "11122"
        assert job.source_portal == "arbetsformedlingen"
        assert job.external_id == "arbetsformedlingen_31281556"
        assert job.url == "https://arbetsformedlingen.se/platsbanken/annonser/31281556"
        assert job.job_type == "vollzeit"
        assert job.published_at is not None
        # GeoJSON-Reihenfolge [lon, lat] - nicht vertauschen
        assert job.longitude == 18.0686
        assert job.latitude == 59.3293

    async def test_deltid_maps_to_teilzeit(self):
        hits = [{"id": "x", "headline": "Deltidsjobb", "working_hours_type": {"label": "Deltid"}}]
        with patch("httpx.AsyncClient", return_value=_mock_client(hits)):
            results = await ArbetsformedlingenSource().search("x", "", 25)

        assert results[0].job_type == "teilzeit"

    async def test_missing_headline_is_skipped(self):
        hits = [{"id": "x", "headline": ""}]
        with patch("httpx.AsyncClient", return_value=_mock_client(hits)):
            results = await ArbetsformedlingenSource().search("x", "", 25)

        assert results == []

    async def test_location_is_blended_into_freetext_query(self):
        mock_client = _mock_client([])
        with patch("httpx.AsyncClient", return_value=mock_client):
            await ArbetsformedlingenSource().search("utvecklare", "Stockholm", 25)

        sent_params = mock_client.get.call_args.kwargs["params"]
        assert sent_params["q"] == "utvecklare Stockholm"
        assert "municipality" not in sent_params

    async def test_no_location_uses_keywords_only(self):
        mock_client = _mock_client([])
        with patch("httpx.AsyncClient", return_value=mock_client):
            await ArbetsformedlingenSource().search("utvecklare", "", 25)

        sent_params = mock_client.get.call_args.kwargs["params"]
        assert sent_params["q"] == "utvecklare"

    async def test_missing_coordinates_yields_none_lat_lon(self):
        hits = [{"id": "x", "headline": "Job", "workplace_address": {}}]
        with patch("httpx.AsyncClient", return_value=_mock_client(hits)):
            results = await ArbetsformedlingenSource().search("x", "", 25)

        assert results[0].latitude is None
        assert results[0].longitude is None

    async def test_http_error_returns_empty_list(self):
        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=Exception("boom"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await ArbetsformedlingenSource().search("x", "", 25)

        assert results == []
