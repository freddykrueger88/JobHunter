"""Bundesagentur für Arbeit – Jobsuche API.

Öffentliche API – kein Nutzer-API-Key nötig.
Authentifizierung erfolgt über den festen Public-Key 'jobboerse-jobsuche'
als X-API-Key Header (dokumentiert auf https://jobsuche.api.bund.dev/).
"""
import httpx
import logging
from backend.services.job_search.base import BaseJobSource, RawJob
from datetime import datetime

log = logging.getLogger(__name__)

BASE_URL = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs"
# Öffentlicher API-Key – fest eingebaut, kein Nutzer-Input nötig
PUBLIC_API_KEY = "jobboerse-jobsuche"


class ArbeitsagenturSource(BaseJobSource):
    """Jobsuche über die öffentliche Bundesagentur-API.

    Keine Registrierung oder persönlichen API-Keys erforderlich.
    """

    async def search(self, keywords: str, location: str, radius_km: int = 25) -> list[RawJob]:
        headers = {
            "X-API-Key": PUBLIC_API_KEY,
            "User-Agent": "JobHunter/1.0",
        }
        params = {
            "was": keywords,
            "wo": location,
            "umkreis": radius_km,
            "size": 25,
            "page": 1,
            "angebotsart": 1,  # 1 = Arbeit, 4 = Ausbildung
        }
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(BASE_URL, params=params, headers=headers, timeout=15)
                r.raise_for_status()
                data = r.json()
        except httpx.TimeoutException:
            log.error("ArbeitsagenturSource: Timeout beim Abrufen der Jobs")
            return []
        except httpx.HTTPStatusError as e:
            log.error(
                "ArbeitsagenturSource: HTTP %s – %s",
                e.response.status_code,
                e.response.text[:200],
            )
            return []
        except Exception as e:
            log.exception("ArbeitsagenturSource: Unerwarteter Fehler: %s", e)
            return []

        results = []
        for item in data.get("stellenangebote", []):
            arbeitgeber = item.get("arbeitgeber", {})
            arbeitsort = item.get("arbeitsort", {})
            results.append(RawJob(
                title=item.get("beruf", ""),
                company=(
                    arbeitgeber
                    if isinstance(arbeitgeber, str)
                    else arbeitgeber.get("name", "")
                ),
                city=arbeitsort.get("ort"),
                postal_code=arbeitsort.get("plz"),
                address=arbeitsort.get("strasse"),
                description=item.get("stellenbeschreibung"),
                url=f"https://www.arbeitsagentur.de/jobsuche/jobdetail/{item.get('hashId', '')}",
                job_type=self._map_arbeitszeitmodell(item.get("arbeitszeitmodelle", [])),
                source_portal="arbeitsagentur",
                external_id=item.get("hashId"),
                published_at=self._parse_date(item.get("eintrittsdatum")),
                latitude=arbeitsort.get("koordinaten", {}).get("lat"),
                longitude=arbeitsort.get("koordinaten", {}).get("lon"),
            ))
        log.info(
            "ArbeitsagenturSource: %d Jobs gefunden für '%s' in '%s'",
            len(results), keywords, location,
        )
        return results

    def _map_arbeitszeitmodell(self, models: list) -> str | None:
        m = [x.lower() for x in models]
        if any("ausbildung" in x for x in m):
            return "ausbildung"
        if any("vollzeit" in x for x in m):
            return "vollzeit"
        if any("teilzeit" in x for x in m):
            return "teilzeit"
        return None

    def _parse_date(self, s: str | None) -> datetime | None:
        if not s:
            return None
        try:
            return datetime.fromisoformat(s)
        except Exception:
            return None
