"""
Tests fuer die neuen EURES-bezogenen Endpunkte in backend/routers/jobs.py.

Regressionsschutz: GET /api/jobs/eures-countries muss VOR GET /{job_id}
registriert sein, sonst faengt die dynamische Route den Aufruf ab und
versucht "eures-countries" als job_id zu parsen (gleiches Muster wie
zuvor bei /defaults vs. /{template_id} in cover_letter_templates.py).
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from backend.services.job_search.base import RawJob

pytestmark = pytest.mark.asyncio


class TestEuresCountriesEndpoint:
    async def test_returns_31_countries_sorted_by_name(self, client: httpx.AsyncClient):
        res = await client.get("/api/jobs/eures-countries")

        assert res.status_code == 200, res.text
        body = res.json()
        assert len(body) == 31
        assert {"code": "DE", "name": "Deutschland"} in body
        names = [c["name"] for c in body]
        assert names == sorted(names)

    async def test_route_not_shadowed_by_job_id_route(self, client: httpx.AsyncClient):
        """Regression: /eures-countries muss vor /{job_id} registriert
        sein, sonst 404/422 statt der Laenderliste."""
        res = await client.get("/api/jobs/eures-countries")
        assert res.status_code != 404
        assert res.status_code != 422


class TestSearchEndpointCountryCode:
    async def test_passes_country_code_through_to_aggregator(self, client: httpx.AsyncClient):
        with patch(
            "backend.routers.jobs.search_all_sources",
            new=AsyncMock(return_value=[RawJob(title="X", company="Y", source_portal="eures")]),
        ) as mock_search:
            res = await client.get("/api/jobs/search", params={
                "keywords": "koch", "location": "Wien", "country_code": "at", "save": False,
            })

        assert res.status_code == 200, res.text
        assert mock_search.call_args.kwargs["country_code"] == "AT"

    async def test_defaults_to_de(self, client: httpx.AsyncClient):
        with patch(
            "backend.routers.jobs.search_all_sources",
            new=AsyncMock(return_value=[]),
        ) as mock_search:
            await client.get("/api/jobs/search", params={
                "keywords": "koch", "location": "Bremen", "save": False,
            })

        assert mock_search.call_args.kwargs["country_code"] == "DE"
