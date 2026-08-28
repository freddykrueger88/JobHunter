"""
Tests fuer backend/services/company_research.py.

Regressionsschutz: ein fehlgeschlagener Rechercheversuch (z.B. transienter
Netzwerkfehler) wurde in _CACHE gespeichert wie ein echtes Ergebnis -
jede weitere Anfrage fuer dieselbe Firma bekam fuer die gesamte
Prozesslaufzeit die Fehlermeldung zurueck statt es erneut zu versuchen.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.services.company_research import _CACHE, fetch_company_dossier

pytestmark = pytest.mark.asyncio


def _mock_http_client(get_side_effect=None, get_return_value=None):
    mock_client = MagicMock()
    if get_side_effect is not None:
        mock_client.get = AsyncMock(side_effect=get_side_effect)
    else:
        mock_client.get = AsyncMock(return_value=get_return_value)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


class TestFetchCompanyDossier:
    async def test_failed_lookup_is_not_cached(self):
        company = "Testfirma Failure XYZ"
        _CACHE.pop(company, None)

        with patch("httpx.AsyncClient", return_value=_mock_http_client(get_side_effect=ConnectionError("boom"))):
            result1 = await fetch_company_dossier(company)

        assert "fehlgeschlagen" in (result1["description"] or "")
        assert company not in _CACHE

        # Zweiter Versuch (Netzwerk jetzt "verfuegbar") darf nicht die
        # gecachte Fehlermeldung zurueckbekommen.
        empty_response = MagicMock()
        empty_response.json.return_value = {"query": {"search": []}}
        with patch("httpx.AsyncClient", return_value=_mock_http_client(get_return_value=empty_response)):
            result2 = await fetch_company_dossier(company)

        assert "fehlgeschlagen" not in (result2["description"] or "")

    async def test_successful_lookup_is_cached(self):
        company = "Testfirma Success XYZ"
        _CACHE.pop(company, None)

        empty_response = MagicMock()
        empty_response.json.return_value = {"query": {"search": []}}
        with patch("httpx.AsyncClient", return_value=_mock_http_client(get_return_value=empty_response)):
            result = await fetch_company_dossier(company)

        assert company in _CACHE
        assert _CACHE[company] is result

    async def test_rating_portal_links_always_present(self):
        """Kununu/Glassdoor haben keine kostenlose API - stattdessen
        Google-`site:`-Suchlinks, die unabhaengig vom Wikipedia-Ergebnis
        (auch bei Netzwerkfehler) immer gesetzt sein muessen."""
        company = "Testfirma Ratings XYZ"
        _CACHE.pop(company, None)

        with patch("httpx.AsyncClient", return_value=_mock_http_client(get_side_effect=ConnectionError("boom"))):
            result = await fetch_company_dossier(company)

        assert result["kununu_search_url"] == "https://www.google.com/search?q=site%3Akununu.com%20Testfirma%20Ratings%20XYZ"
        assert result["glassdoor_search_url"] == "https://www.google.com/search?q=site%3Aglassdoor.com%20Testfirma%20Ratings%20XYZ"
