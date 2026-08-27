"""
Tests fuer backend/services/job_search/service_bund.py.

Phase I.1 (Portale unterhalb von EURES, Fortsetzung nach Karriere.NRW):
service.bund.de deckt Stellenausschreibungen von Bund, allen 16 Laendern
UND Kommunen bundesweit ab (~9.000 Ausschreibungen) - anders als Karriere.NRW
(nur ein Bundesland). Kein Scraping mit Session-Cookies noetig: die Seite
bietet einen dokumentierten, zustandslosen RSS-Export der Suchergebnisse
("jobsrss=true"), live gegengetestet. Anders als bei Karriere.NRW wurde
hier live bestaetigt, dass Orts-/Radius-Filter (city_zipcode/ambit_distance)
tatsaechlich funktionieren (Testabfrage mit city_zipcode=Berlin lieferte
ausschliesslich Berliner Treffer) - werden daher bewusst mitgeschickt.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.services.job_search.service_bund import ServiceBundSource, _snap_radius

_RSS_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>service.bund.de - Stellenangebote</title>
    {items}
  </channel>
</rss>"""

_ITEM = """
    <item>
<title>{title}</title>
<link>{link}#track=feed-jobs</link>
<description>
<![CDATA[
Arbeitgeber: <strong>{arbeitgeber}</strong><br />
    Ort: <strong>{ort}</strong>
 <br />
<br />Bewerbungsfrist:  <strong>24.09.2026 23:59</strong> <br />Veröffentlichungsende:  <strong>24.09.2026 23:59</strong>  <br /><br />
]]>
</description>
<pubDate>Thu, 27 Aug 2026 14:00:00 +0200</pubDate>
<guid>{link}</guid>
    </item>"""


def _mock_client(xml_text: str):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.text = xml_text
    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


@pytest.mark.asyncio
class TestServiceBundSource:
    async def test_returns_normalized_jobs_with_plz_split(self):
        xml = _RSS_TEMPLATE.format(items=_ITEM.format(
            title="Sachbearbeiter/-in Haushalt (m/w/d)",
            link="https://www.service.bund.de/IMPORTE/Stellenangebote/editor/x/2026/08/6620856.html",
            arbeitgeber="Berufsgenossenschaft Holz und Metall",
            ort="55124 Mainz",
        ))
        with patch("httpx.AsyncClient", return_value=_mock_client(xml)):
            results = await ServiceBundSource().search("Sachbearbeiter", "Mainz", 25)

        assert len(results) == 1
        job = results[0]
        assert job.title == "Sachbearbeiter/-in Haushalt (m/w/d)"
        assert job.company == "Berufsgenossenschaft Holz und Metall"
        assert job.city == "Mainz"
        assert job.postal_code == "55124"
        assert job.source_portal == "service_bund"
        assert job.url == "https://www.service.bund.de/IMPORTE/Stellenangebote/editor/x/2026/08/6620856.html"
        assert job.external_id == f"service_bund_{job.url}"
        assert job.published_at is not None

    async def test_ort_without_plz_falls_back_to_raw_string(self):
        xml = _RSS_TEMPLATE.format(items=_ITEM.format(
            title="Testjob", link="https://www.service.bund.de/x.html",
            arbeitgeber="Testbehoerde", ort="Irgendwo ohne PLZ",
        ))
        with patch("httpx.AsyncClient", return_value=_mock_client(xml)):
            results = await ServiceBundSource().search("x", "", 25)

        assert results[0].city == "Irgendwo ohne PLZ"
        assert results[0].postal_code is None

    async def test_html_entities_are_unescaped(self):
        xml = _RSS_TEMPLATE.format(items=_ITEM.format(
            title="Sachbearbeiter f&#252;r &#8222;Vermittlungskompass&#8220;",
            link="https://www.service.bund.de/y.html",
            arbeitgeber="Polizeipr&#228;sidium",
            ort="15234 Frankfurt (Oder)",
        ))
        with patch("httpx.AsyncClient", return_value=_mock_client(xml)):
            results = await ServiceBundSource().search("x", "", 25)

        assert "ü" in results[0].title
        assert "ä" in results[0].company

    async def test_empty_result_list_is_handled(self):
        xml = _RSS_TEMPLATE.format(items="")
        with patch("httpx.AsyncClient", return_value=_mock_client(xml)):
            results = await ServiceBundSource().search("nonexistentqueryxyz", "", 25)

        assert results == []

    async def test_location_and_radius_are_sent_when_location_given(self):
        mock_client = _mock_client(_RSS_TEMPLATE.format(items=""))
        with patch("httpx.AsyncClient", return_value=mock_client):
            await ServiceBundSource().search("Ingenieur", "Berlin", 30)

        sent_params = mock_client.get.call_args.kwargs["params"]
        assert sent_params["city_zipcode"] == "Berlin"
        assert sent_params["ambit_distance"] == "30"
        assert sent_params["templateQueryString"] == "Ingenieur"

    async def test_no_location_omits_location_params(self):
        mock_client = _mock_client(_RSS_TEMPLATE.format(items=""))
        with patch("httpx.AsyncClient", return_value=mock_client):
            await ServiceBundSource().search("Ingenieur", "", 25)

        sent_params = mock_client.get.call_args.kwargs["params"]
        assert "city_zipcode" not in sent_params
        assert "ambit_distance" not in sent_params

    async def test_malformed_xml_returns_empty_list(self):
        with patch("httpx.AsyncClient", return_value=_mock_client("<not><valid<xml")):
            results = await ServiceBundSource().search("x", "", 25)

        assert results == []

    async def test_http_error_returns_empty_list(self):
        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=Exception("boom"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("httpx.AsyncClient", return_value=mock_client):
            results = await ServiceBundSource().search("x", "", 25)

        assert results == []


class TestSnapRadius:
    def test_snaps_to_nearest_allowed_step(self):
        assert _snap_radius(25) == 20
        assert _snap_radius(26) == 30
        assert _snap_radius(5) == 10
        assert _snap_radius(200) == 90
