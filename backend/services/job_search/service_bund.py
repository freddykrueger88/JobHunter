"""service.bund.de - Stellenangebote von Bund, Laendern, Staedten und Kommunen.

Ueber den gesamten oeffentlichen Dienst Deutschlands hinweg (Polizei, Ministerien,
Behoerden, Stadtverwaltungen, Landkreise, Sozialversicherungstraeger etc.),
~9.000 aktuelle Ausschreibungen. Keine Session/Cookies noetig: die Seite bietet
einen dokumentierten, zustandslosen RSS-Export der Suchergebnisse
(URL-Parameter "jobsrss=true"), live gegengetestet - liefert sauberes,
wohlgeformtes XML statt HTML zum Scrapen, und Orts-/Radius-Filter (anders als
bei Karriere.NRW) funktionieren live nachweislich korrekt (gegengetestet mit
city_zipcode=Berlin: alle Treffer tatsaechlich in Berlin).
"""
from __future__ import annotations

import logging
import re
from datetime import datetime
from xml.etree import ElementTree

import httpx

from backend.services.job_search.base import BaseJobSource, RawJob, safe_get

log = logging.getLogger(__name__)

SEARCH_URL = "https://www.service.bund.de/Content/DE/Stellen/Suche/Formular.html"
NN = "4642046"

# Erlaubte Radius-Stufen des Suchformulars (<select name="ambit_distance">) -
# es gibt keine freie Zahleneingabe, es muss auf einen dieser Werte gerundet werden.
_RADIUS_STEPS = [10, 20, 30, 50, 75, 90]

_DESC_ARBEITGEBER = re.compile(r"Arbeitgeber:\s*<strong>(.*?)</strong>", re.S)
_DESC_ORT = re.compile(r"Ort:\s*<strong>(.*?)</strong>", re.S)
_ORT_PLZ = re.compile(r"^\s*(\d{5})\s+(.*)$")


def _snap_radius(radius_km: int) -> int:
    return min(_RADIUS_STEPS, key=lambda step: abs(step - radius_km))


def _unescape(s: str) -> str:
    return (
        s.replace("&#252;", "ü").replace("&#228;", "ä").replace("&#246;", "ö")
        .replace("&#8222;", "„").replace("&#8220;", "“").replace("&amp;", "&")
        .strip()
    )


class ServiceBundSource(BaseJobSource):
    """RSS-basierte Anbindung an service.bund.de (oeffentlicher Dienst, alle Ebenen)."""

    async def search(self, keywords: str, location: str, radius_km: int = 25) -> list[RawJob]:
        params = {
            "nn": NN,
            "jobsrss": "true",
            "resultsPerPage": "100",
            "templateQueryString": keywords,
        }
        if location:
            params["city_zipcode"] = location
            params["ambit_distance"] = str(_snap_radius(radius_km))

        async with httpx.AsyncClient(timeout=15) as client:
            r = await safe_get(client, SEARCH_URL, "ServiceBundSource", params=params, headers={"Accept": "application/rss+xml, text/xml"})
        if r is None:
            return []
        xml_text = r.text

        results = self._parse(xml_text)
        log.info("ServiceBundSource: %d Jobs gefunden für '%s' in '%s'", len(results), keywords, location)
        return results

    def _parse(self, xml_text: str) -> list[RawJob]:
        try:
            root = ElementTree.fromstring(xml_text)
        except ElementTree.ParseError as e:
            log.error("ServiceBundSource: RSS-XML nicht parsebar: %s", e)
            return []

        results: list[RawJob] = []
        for item in root.findall("./channel/item"):
            try:
                title = _unescape((item.findtext("title") or ""))
                url = (item.findtext("link") or "").split("#")[0] or None
                guid = item.findtext("guid") or url or ""
                desc = item.findtext("description") or ""

                ag_match = _DESC_ARBEITGEBER.search(desc)
                ort_match = _DESC_ORT.search(desc)
                company = _unescape(ag_match.group(1)) if ag_match else ""
                ort_raw = _unescape(ort_match.group(1)) if ort_match else ""

                postal_code = None
                city = ort_raw or None
                plz_match = _ORT_PLZ.match(ort_raw)
                if plz_match:
                    postal_code = plz_match.group(1)
                    city = plz_match.group(2)

                pub_date_raw = item.findtext("pubDate")
                published_at = None
                if pub_date_raw:
                    try:
                        published_at = datetime.strptime(pub_date_raw, "%a, %d %b %Y %H:%M:%S %z")
                    except ValueError:
                        published_at = None

                if not title:
                    continue

                results.append(RawJob(
                    title=title,
                    company=company,
                    city=city,
                    postal_code=postal_code,
                    url=url,
                    source_portal="service_bund",
                    external_id=f"service_bund_{guid}" if guid else None,
                    published_at=published_at,
                ))
            except Exception as e:
                log.debug("ServiceBundSource: Fehler beim Parsen eines Items: %s", e)
                continue

        return results
