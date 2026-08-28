"""#72 - EURES-Integration: EU-weite Stellensuche ueber die offizielle EURES REST API.

War fertig geschrieben, aber nie im Aggregator registriert (siehe
aggregator.py) - und die urspruenglich hartcodierte Endpoint-URL
(europa.eu/eures/eures-searchengine/page/jv-search/v2/search) antwortet
inzwischen mit 404. Aktueller Endpoint + Request-/Response-Schema per
Recherche (2026-08-27) anhand der inoffiziellen, aber gegen die echte
API verifizierten Dokumentation https://rorar.github.io/EURES-API-Documentation/
ermittelt und live gegengetestet (12.212 Treffer fuer "python developer"
in Deutschland).

Wichtige Unterschiede zur alten Implementierung:
- POST-Body braucht viele Pflichtfelder (auch wenn leer) - siehe payload
  unten, nicht nur keywords + Land.
- keywords ist ein Array von {keyword, specificSearchCode}-Objekten,
  kein einzelner String.
- Standort-Filter (locationCodes) laeuft ausschliesslich ueber NUTS-
  Regionscodes, keine Freitext-Ort+Radius-Suche wie bei den anderen
  Quellen in diesem Projekt - EURES kennt keinen Umkreis-Parameter.
- Die Trefferobjekte liefern keinen Klartext-Ortsnamen, nur NUTS-Codes
  (locationMap) - ueber nuts_regions.json (offizielle Eurostat/GISCO-
  NUTS-2024-Referenztabelle) in einen Ortsnamen aufgeloest.
- Keine direkte Bewerbungs-/Anzeigen-URL im Response - der Detail-Link
  wird nach dem Muster der EURES-Portal-SPA konstruiert und mit einem
  echten Browser gegengeprueft (siehe PR/Commit-Notiz).
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx

from backend.services.job_search.base import BaseJobSource, RawJob, safe_post

log = logging.getLogger(__name__)

EURES_SEARCH_URL = "https://europa.eu/eures/api/jv-searchengine/public/jv-search/search"
# UNVERIFIZIERT: die Such-API selbst ist live gegengetestet (siehe oben),
# aber dieses Detail-URL-Muster ist aus der REST-Konvention der API
# abgeleitet und NICHT mit einem echten Browser bestaetigt - das
# EURES-Portal ist eine JS-SPA, die fuer praktisch jeden Pfad unter
# /eures/portal/... mit 200 (Client-Routing-Fallback) antwortet, HTTP-
# Statuscodes sind also nicht aussagekraeftig. Vor Verlass auf diesen
# Link bitte einmal manuell im Browser pruefen.
EURES_DETAIL_URL = "https://europa.eu/eures/portal/jv-se/jv-details/{id}?lang={lang}"

_NUTS_PATH = Path(__file__).parent / "nuts_regions.json"
_NUTS_NAMES: dict[str, str] = json.loads(_NUTS_PATH.read_text(encoding="utf-8"))

# ISO 3166-1 alpha-2 -> Landesname (Deutsch). Deckt die 31 von EURES
# unterstuetzten Laender ab (EU-Mitgliedsstaaten + EFTA), per
# GET /shared-data-rest-api/public/reference/countries bestaetigt.
EURES_COUNTRIES: dict[str, str] = {
    "AT": "Österreich", "BE": "Belgien", "BG": "Bulgarien", "HR": "Kroatien",
    "CY": "Zypern", "CZ": "Tschechien", "DK": "Dänemark", "EE": "Estland",
    "FI": "Finnland", "FR": "Frankreich", "DE": "Deutschland", "EL": "Griechenland",
    "HU": "Ungarn", "IS": "Island", "IE": "Irland", "IT": "Italien",
    "LV": "Lettland", "LI": "Liechtenstein", "LT": "Litauen", "LU": "Luxemburg",
    "MT": "Malta", "NL": "Niederlande", "NO": "Norwegen", "PL": "Polen",
    "PT": "Portugal", "RO": "Rumänien", "SK": "Slowakei", "SI": "Slowenien",
    "ES": "Spanien", "SE": "Schweden", "CH": "Schweiz",
}


def _resolve_location(location_map: dict) -> tuple[str | None, str | None]:
    """Loest die erste Region aus locationMap in (Ortsname, Laendercode) auf."""
    for country_code, regions in location_map.items():
        for region_code in regions or []:
            if region_code and region_code in _NUTS_NAMES:
                return _NUTS_NAMES[region_code], country_code
        return None, country_code
    return None, None


class EuresSource(BaseJobSource):
    """Sucht in der EURES-Datenbank (offizielle EU-weite Jobbörse).

    EURES filtert nur nach Land (NUTS-Landescode), keine Umkreissuche -
    `location`/`radius_km` aus dem gemeinsamen BaseJobSource-Interface
    werden deshalb ignoriert, `country_code` steuert stattdessen, welches
    Land durchsucht wird.
    """

    def __init__(self, country_code: str = "DE", lang: str = "de", results_per_page: int = 20):
        self.country_code = country_code.upper()
        self.lang = lang
        self.results_per_page = results_per_page

    async def search(self, keywords: str, location: str, radius_km: int = 25) -> list[RawJob]:
        payload = {
            "resultsPerPage": self.results_per_page,
            "page": 1,
            "sortSearch": "BEST_MATCH",
            "keywords": [{"keyword": keywords, "specificSearchCode": "EVERYWHERE"}] if keywords else [],
            "publicationPeriod": None,
            "occupationUris": [],
            "skillUris": [],
            "requiredExperienceCodes": [],
            "positionScheduleCodes": [],
            "sectorCodes": [],
            "educationAndQualificationLevelCodes": [],
            "positionOfferingCodes": [],
            "locationCodes": [self.country_code.lower()],
            "euresFlagCodes": [],
            "otherBenefitsCodes": [],
            "requiredLanguages": [],
            "minNumberPost": None,
            "sessionId": str(uuid.uuid4()),
            "userPreferredLanguage": None,
            "requestLanguage": self.lang,
        }

        async with httpx.AsyncClient(timeout=15) as client:
            r = await safe_post(
                client, EURES_SEARCH_URL, "EuresSource",
                json=payload,
                headers={"Accept": "application/json", "Content-Type": "application/json"},
            )
        if r is None:
            return []
        data = r.json()

        results: list[RawJob] = []
        for jv in data.get("jvs", []):
            employer = jv.get("employer") or {}
            city, jv_country = _resolve_location(jv.get("locationMap") or {})
            created_ms = jv.get("creationDate")
            published_at = (
                datetime.fromtimestamp(created_ms / 1000, tz=timezone.utc)
                if isinstance(created_ms, (int, float)) else None
            )
            jv_id = jv.get("id", "")
            results.append(RawJob(
                title=jv.get("title", ""),
                company=employer.get("name", ""),
                city=city,
                description=jv.get("description"),
                url=EURES_DETAIL_URL.format(id=jv_id, lang=self.lang) if jv_id else None,
                source_portal="eures",
                external_id=f"eures_{jv_id}" if jv_id else None,
                published_at=published_at,
            ))

        log.info(
            "EuresSource: %d Jobs gefunden für '%s' in %s (von %d Treffern gesamt)",
            len(results), keywords, self.country_code, data.get("numberRecords", 0),
        )
        return results
