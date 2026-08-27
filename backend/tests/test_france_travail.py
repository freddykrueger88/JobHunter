"""
Tests fuer backend/services/job_search/france_travail.py.

Phase I.1 (EU-weite Jobboersen, naechster Schritt nach Deutschland):
France Travail (ex-Pole Emploi) ist das franzoesische Gegenstueck zur
Arbeitsagentur-Quelle. Anders als alle bisherigen DE-Quellen dieser
Session gibt es keinen oeffentlichen Fest-Key - der Nutzer muss eigene,
kostenlose OAuth2-Zugangsdaten registrieren (francetravail.io). Das
Response-Format wurde NICHT mit echten Daten live verifiziert (dafuer
braucht es eigene Zugangsdaten, die nur der Nutzer selbst besorgen kann) -
basiert auf offizieller Doku + mehreren unabhaengigen
Referenzimplementierungen. Token-/Such-Endpoint-Erreichbarkeit selbst
wurden live gegengetestet (echter OAuth2-Fehler statt 404 bzw. 401 statt
404 auf den Such-Pfad).
"""
from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.services.job_search import france_travail
from backend.services.job_search.france_travail import FranceTravailSource, _get_token, _resolve_commune

pytestmark = pytest.mark.asyncio


def _mock_client(json_body, status_ok=True):
    mock_response = MagicMock()
    if status_ok:
        mock_response.raise_for_status = MagicMock()
    else:
        import httpx
        mock_response.raise_for_status = MagicMock(side_effect=httpx.HTTPStatusError(
            "err", request=MagicMock(), response=MagicMock(status_code=401),
        ))
    mock_response.json.return_value = json_body
    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


@pytest.fixture(autouse=True)
def _clear_token_cache():
    france_travail._token_cache.clear()
    yield
    france_travail._token_cache.clear()


class TestGetToken:
    async def test_fetches_and_caches_token(self):
        mock_client = _mock_client({"access_token": "tok-123", "expires_in": 1200})
        with patch("httpx.AsyncClient", return_value=mock_client):
            token = await _get_token("cid", "secret")

        assert token == "tok-123"
        assert "cid" in france_travail._token_cache

    async def test_uses_cached_token_without_new_request(self):
        france_travail._token_cache["cid"] = ("cached-tok", time.time() + 500)
        mock_client = _mock_client({})
        with patch("httpx.AsyncClient", return_value=mock_client):
            token = await _get_token("cid", "secret")

        assert token == "cached-tok"
        mock_client.post.assert_not_called()

    async def test_expired_cache_triggers_new_request(self):
        france_travail._token_cache["cid"] = ("old-tok", time.time() - 10)
        mock_client = _mock_client({"access_token": "new-tok", "expires_in": 1200})
        with patch("httpx.AsyncClient", return_value=mock_client):
            token = await _get_token("cid", "secret")

        assert token == "new-tok"

    async def test_failed_token_request_returns_none(self):
        mock_client = MagicMock()
        mock_client.post = AsyncMock(side_effect=Exception("boom"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        with patch("httpx.AsyncClient", return_value=mock_client):
            token = await _get_token("cid", "secret")

        assert token is None


class TestResolveCommune:
    async def test_returns_first_result_code(self):
        mock_client = _mock_client([{"code": "69123"}, {"code": "03080"}])
        with patch("httpx.AsyncClient", return_value=mock_client):
            code = await _resolve_commune("Lyon")

        assert code == "69123"

    async def test_no_match_returns_none(self):
        mock_client = _mock_client([])
        with patch("httpx.AsyncClient", return_value=mock_client):
            code = await _resolve_commune("Nichtexistenzstadt")

        assert code is None

    async def test_error_returns_none(self):
        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=Exception("boom"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        with patch("httpx.AsyncClient", return_value=mock_client):
            code = await _resolve_commune("Lyon")

        assert code is None


class TestFranceTravailSourceSearch:
    async def test_missing_credentials_returns_empty_without_any_request(self):
        results = await FranceTravailSource(None, None).search("dev", "Lyon", 25)
        assert results == []

        results2 = await FranceTravailSource("cid", None).search("dev", "Lyon", 25)
        assert results2 == []

    async def test_token_failure_returns_empty(self):
        with patch("backend.services.job_search.france_travail._get_token", new=AsyncMock(return_value=None)):
            results = await FranceTravailSource("cid", "secret").search("dev", "", 25)

        assert results == []

    async def test_returns_normalized_jobs(self):
        search_response = {
            "resultats": [{
                "id": "123ABC",
                "intitule": "Développeur Python Senior",
                "description": "Une belle offre",
                "entreprise": {"nom": "Acme SARL"},
                "lieuTravail": {"libelle": "69003 - Lyon 3e", "codePostal": "69003", "latitude": 45.75, "longitude": 4.85},
                "origineOffre": {"urlOrigine": "https://candidat.francetravail.fr/offres/recherche/detail/123ABC"},
                "dateCreation": "2026-08-20T10:00:00.000Z",
                "typeContrat": "CDI",
                "alternance": False,
            }],
        }
        with patch(
            "backend.services.job_search.france_travail._get_token",
            new=AsyncMock(return_value="tok-123"),
        ), patch(
            "backend.services.job_search.france_travail._resolve_commune",
            new=AsyncMock(return_value="69123"),
        ), patch("httpx.AsyncClient", return_value=_mock_client(search_response)):
            results = await FranceTravailSource("cid", "secret").search("python", "Lyon", 25)

        assert len(results) == 1
        job = results[0]
        assert job.title == "Développeur Python Senior"
        assert job.company == "Acme SARL"
        assert job.postal_code == "69003"
        assert job.source_portal == "france_travail"
        assert job.external_id == "france_travail_123ABC"
        assert job.url == "https://candidat.francetravail.fr/offres/recherche/detail/123ABC"
        assert job.job_type is None
        assert job.published_at is not None
        assert job.latitude == 45.75

    async def test_alternance_maps_to_ausbildung(self):
        search_response = {"resultats": [{
            "id": "x", "intitule": "Alternance Data", "alternance": True,
        }]}
        with patch(
            "backend.services.job_search.france_travail._get_token",
            new=AsyncMock(return_value="tok"),
        ), patch("httpx.AsyncClient", return_value=_mock_client(search_response)):
            results = await FranceTravailSource("cid", "secret").search("data", "", 25)

        assert results[0].job_type == "ausbildung"

    async def test_missing_title_is_skipped(self):
        search_response = {"resultats": [{"id": "x", "intitule": ""}]}
        with patch(
            "backend.services.job_search.france_travail._get_token",
            new=AsyncMock(return_value="tok"),
        ), patch("httpx.AsyncClient", return_value=_mock_client(search_response)):
            results = await FranceTravailSource("cid", "secret").search("x", "", 25)

        assert results == []

    async def test_empty_location_skips_commune_resolution(self):
        commune_mock = AsyncMock(return_value="69123")
        with patch(
            "backend.services.job_search.france_travail._get_token",
            new=AsyncMock(return_value="tok"),
        ), patch(
            "backend.services.job_search.france_travail._resolve_commune", new=commune_mock,
        ), patch("httpx.AsyncClient", return_value=_mock_client({"resultats": []})):
            await FranceTravailSource("cid", "secret").search("x", "", 25)

        commune_mock.assert_not_called()

    async def test_http_error_returns_empty_list(self):
        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=Exception("boom"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "backend.services.job_search.france_travail._get_token",
            new=AsyncMock(return_value="tok"),
        ), patch("httpx.AsyncClient", return_value=mock_client):
            results = await FranceTravailSource("cid", "secret").search("x", "", 25)

        assert results == []
