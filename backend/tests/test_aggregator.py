"""
Tests fuer backend/services/job_search/aggregator.py.

Phase I.1: EuresSource ist jetzt immer als Quelle registriert (deckt EU-
weite Suche ab). Arbeitsagentur/StepStone sind Deutschland-spezifische
Scraper und werden nur noch aktiviert, wenn country_code=="DE" (Default,
identisch zum bisherigen Verhalten) - sonst wuerden bei einer expliziten
Auslandssuche (z.B. "AT") irrefuehrende deutsche Treffer mit einlaufen.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from backend.models.settings import UserSettings
from backend.services.job_search.aggregator import search_all_sources
from backend.services.job_search.base import RawJob

pytestmark = pytest.mark.asyncio


class TestSearchAllSources:
    async def test_default_country_uses_de_specific_sources(self):
        settings_row = UserSettings(id=1)
        with patch(
            "backend.services.job_search.arbeitsagentur.ArbeitsagenturSource.search",
            new=AsyncMock(return_value=[RawJob(title="AA-Job", company="X", source_portal="arbeitsagentur")]),
        ), patch(
            "backend.services.job_search.stepstone.StepStoneSource.search",
            new=AsyncMock(return_value=[]),
        ), patch(
            "backend.services.job_search.karriere_nrw.KarriereNrwSource.search",
            new=AsyncMock(return_value=[RawJob(title="NRW-Job", company="Z", source_portal="karriere_nrw")]),
        ), patch(
            "backend.services.job_search.eures_scraper.EuresSource.search",
            new=AsyncMock(return_value=[RawJob(title="EURES-Job", company="Y", source_portal="eures")]),
        ):
            results = await search_all_sources("python", "Bremen", 25, settings_row)

        portals = {r.source_portal for r in results}
        assert "arbeitsagentur" in portals
        assert "karriere_nrw" in portals
        assert "eures" in portals

    async def test_non_de_country_skips_german_specific_sources(self):
        settings_row = UserSettings(id=1)
        aa_search = AsyncMock(return_value=[RawJob(title="AA-Job", company="X", source_portal="arbeitsagentur")])
        nrw_search = AsyncMock(return_value=[RawJob(title="NRW-Job", company="Z", source_portal="karriere_nrw")])
        with patch(
            "backend.services.job_search.arbeitsagentur.ArbeitsagenturSource.search", new=aa_search,
        ), patch(
            "backend.services.job_search.karriere_nrw.KarriereNrwSource.search", new=nrw_search,
        ), patch(
            "backend.services.job_search.eures_scraper.EuresSource.search",
            new=AsyncMock(return_value=[RawJob(title="EURES-AT-Job", company="Y", source_portal="eures")]),
        ):
            results = await search_all_sources("koch", "Wien", 25, settings_row, country_code="AT")

        aa_search.assert_not_called()
        nrw_search.assert_not_called()
        portals = {r.source_portal for r in results}
        assert portals == {"eures"}

    async def test_eures_receives_selected_country_code(self):
        settings_row = UserSettings(id=1)
        with patch(
            "backend.services.job_search.eures_scraper.EuresSource.__init__", return_value=None,
        ) as mock_init, patch(
            "backend.services.job_search.eures_scraper.EuresSource.search",
            new=AsyncMock(return_value=[]),
        ):
            await search_all_sources("x", "y", 25, settings_row, country_code="FR")

        mock_init.assert_called_once_with(country_code="FR")
