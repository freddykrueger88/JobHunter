"""
Tests fuer backend/services/job_search/eures_scraper.py.

Phase I.1 (EU-weite Jobboersen): der EURES-Adapter existierte bereits
als freistehende Funktion (search_eures), war aber nie im Aggregator
registriert (siehe aggregator.py) UND rief eine inzwischen tote
API-URL auf (404 - europa.eu/eures/eures-searchengine/page/jv-search/v2/
search). Aktueller Endpoint + Request-/Response-Schema recherchiert und
live gegen die echte API verifiziert (siehe Commit-Notiz), hier als
BaseJobSource-Klasse (EuresSource) neu implementiert und im Aggregator
registriert. Ausserdem hing bereits ein zweiter, unabhaengiger und
ebenfalls nie im Frontend genutzter Router (backend/routers/eures.py)
an derselben toten Funktion - als redundanter toter Code entfernt statt
repariert, da die Aggregator-Integration dieselbe Funktion konsistent
mit allen anderen Quellen abdeckt.

Response-Schema-Details unten (payload-Struktur, locationMap-Format)
sind absichtlich exakt wie die echte API nachgebildet.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.services.job_search.eures_scraper import (
    EURES_COUNTRIES,
    EuresSource,
    _resolve_location,
)

pytestmark = pytest.mark.asyncio


def _mock_eures_response(jvs: list[dict], number_records: int | None = None):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "numberRecords": number_records if number_records is not None else len(jvs),
        "jvs": jvs,
        "facets": {},
    }
    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


class TestResolveLocation:
    async def test_resolves_known_nuts_code_to_name(self):
        # DE111 = "Stuttgart, Stadtkreis" - live gegen die echte EURES-API
        # verifiziert (siehe Commit-Notiz), aus der offiziellen Eurostat/
        # GISCO-NUTS-2024-Referenztabelle.
        city, country = _resolve_location({"DE": ["DE111"]})
        assert city == "Stuttgart, Stadtkreis"
        assert country == "DE"

    async def test_unknown_nuts_code_returns_none_city(self):
        city, country = _resolve_location({"DE": ["DE_NICHT_VORHANDEN"]})
        assert city is None
        assert country == "DE"

    async def test_empty_location_map_returns_none_none(self):
        assert _resolve_location({}) == (None, None)


class TestEuresCountries:
    async def test_contains_31_eures_countries(self):
        # GET /shared-data-rest-api/public/reference/countries liefert
        # laut Doku 31 Laendercodes.
        assert len(EURES_COUNTRIES) == 31
        assert EURES_COUNTRIES["DE"] == "Deutschland"


class TestEuresSourceSearch:
    async def test_returns_normalized_jobs_with_resolved_city(self):
        jvs = [{
            "title": "Python Developer",
            "description": "<p>Toller Job</p>",
            "id": "MTM2NDQtMTc2NDgxLVMgMQ",
            "creationDate": 1783110346080,
            "locationMap": {"DE": ["DE111"]},
            "employer": {"name": "Intervall GmbH"},
        }]
        with patch("httpx.AsyncClient", return_value=_mock_eures_response(jvs, number_records=12212)):
            results = await EuresSource(country_code="DE").search("python developer", location="ignored")

        assert len(results) == 1
        job = results[0]
        assert job.title == "Python Developer"
        assert job.company == "Intervall GmbH"
        assert job.city == "Stuttgart, Stadtkreis"
        assert job.source_portal == "eures"
        assert job.external_id == "eures_MTM2NDQtMTc2NDgxLVMgMQ"
        assert job.url == "https://europa.eu/eures/portal/jv-se/jv-details/MTM2NDQtMTc2NDgxLVMgMQ?lang=de"
        assert job.published_at is not None

    async def test_sends_correct_payload_shape(self):
        mock_client = _mock_eures_response([])
        with patch("httpx.AsyncClient", return_value=mock_client):
            await EuresSource(country_code="AT", lang="de").search("koch", location="ignored")

        sent = mock_client.post.call_args.kwargs["json"]
        assert sent["keywords"] == [{"keyword": "koch", "specificSearchCode": "EVERYWHERE"}]
        assert sent["locationCodes"] == ["at"]
        assert sent["requestLanguage"] == "de"
        # Pflichtfelder aus dem JobSearchRequest-Schema muessen vorhanden
        # sein, auch wenn leer - sonst lehnt die echte API die Anfrage ab.
        for required_field in (
            "resultsPerPage", "page", "sortSearch", "occupationUris", "skillUris",
            "requiredExperienceCodes", "positionScheduleCodes", "sectorCodes",
            "educationAndQualificationLevelCodes", "positionOfferingCodes",
            "euresFlagCodes", "otherBenefitsCodes", "requiredLanguages", "sessionId",
        ):
            assert required_field in sent

    async def test_missing_id_yields_no_url_and_no_external_id(self):
        jvs = [{"title": "Ohne ID", "employer": {"name": "X"}, "locationMap": {}}]
        with patch("httpx.AsyncClient", return_value=_mock_eures_response(jvs)):
            results = await EuresSource().search("x", location="ignored")

        assert results[0].url is None
        assert results[0].external_id is None

    async def test_http_error_returns_empty_list(self):
        mock_client = MagicMock()
        mock_client.post = AsyncMock(side_effect=Exception("boom"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await EuresSource().search("x", location="ignored")

        assert results == []
