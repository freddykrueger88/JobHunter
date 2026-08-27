"""Arbetsformedlingen (schwedische Arbeitsagentur) - JobSearch API,
Teil der offiziellen "JobTech"-Offene-Daten-Plattform. Voellig oeffentlich,
kein API-Key noetig (explizit als frei fuer jeden Zweck nutzbar dokumentiert)
- damit im selben zero-config-Muster wie Arbeitsagentur/EURES/Karriere.NRW/
service.bund.de dieser Session, nicht wie das France-Travail-Muster
(eigene Zugangsdaten noetig).

Live gegengetestet: https://jobsearch.api.jobtechdev.se/search liefert
sauberes, sehr reichhaltiges JSON mit echten aktuellen Stellenanzeigen
(u.a. bestaetigt: webpage_url-Feld liefert direkt eine gueltige, echte
Detail-URL - kein Konstruktionsversuch noetig wie bei EURES).

Ort-Filterung: der dokumentierte "municipality"-Parameter braucht eine
Taxonomy-Concept-ID (nicht den Klartextnamen - "municipality=Stockholm"
liefert live 0 Treffer, "municipality=<concept_id>" korrekt gefiltert),
und die Taxonomy-API matched nur exakt buchstabierte volle Gemeindenamen,
keine Teilstrings/Fuzzy-Suche (bei "malm" statt "Malmö": 0 Treffer) -
bei einem freien Texteingabefeld im Frontend ein echtes Risiko fuer
stille 0-Treffer, aehnlich dem Karriere.NRW-ort-Fund dieser Session.
Deshalb bewusst NICHT der strikte municipality-Filter, sondern die von
der API selbst so vorgesehene Variante: Ort wird einfach mit ins
Freitext-Suchfeld "q" eingemischt (die API extrahiert Orte selbst aus
natuerlichsprachigem Text, live verifiziert: "utvecklare stockholm"
lieferte 226 tatsaechlich in Stockholm ansaessige Treffer) - degradiert
bei unerkannten Ortsnamen graceful zu einer reinen Stichwortsuche statt
still leer zu bleiben.
"""
from __future__ import annotations

import logging
from datetime import datetime

import httpx

from backend.services.job_search.base import BaseJobSource, RawJob

log = logging.getLogger(__name__)

SEARCH_URL = "https://jobsearch.api.jobtechdev.se/search"


class ArbetsformedlingenSource(BaseJobSource):
    """Schwedische nationale Jobboerse (Arbetsformedlingen/JobTech),
    oeffentliche API ohne Nutzer-Key."""

    async def search(self, keywords: str, location: str, radius_km: int = 25) -> list[RawJob]:
        query = f"{keywords} {location}".strip() if location else keywords
        params = {"q": query, "limit": 30}

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(SEARCH_URL, params=params, headers={"Accept": "application/json"})
                r.raise_for_status()
                data = r.json()
        except httpx.TimeoutException:
            log.error("ArbetsformedlingenSource: Timeout")
            return []
        except httpx.HTTPStatusError as e:
            log.error("ArbetsformedlingenSource: HTTP %s", e.response.status_code)
            return []
        except Exception as e:
            log.exception("ArbetsformedlingenSource: Unerwarteter Fehler: %s", e)
            return []

        results: list[RawJob] = []
        for item in data.get("hits", []):
            title = item.get("headline") or ""
            if not title:
                continue

            employer = item.get("employer") or {}
            addr = item.get("workplace_address") or {}
            coords = addr.get("coordinates") or []  # [lon, lat] (GeoJSON-Reihenfolge)

            pub_date_raw = item.get("publication_date")
            published_at = None
            if pub_date_raw:
                try:
                    published_at = datetime.fromisoformat(pub_date_raw)
                except ValueError:
                    published_at = None

            offer_id = item.get("id", "")
            results.append(RawJob(
                title=title,
                company=employer.get("name") or "",
                city=addr.get("city") or addr.get("municipality"),
                postal_code=addr.get("postcode"),
                description=(item.get("description") or {}).get("text"),
                url=item.get("webpage_url"),
                job_type=self._map_type(item.get("working_hours_type")),
                source_portal="arbetsformedlingen",
                external_id=f"arbetsformedlingen_{offer_id}" if offer_id else None,
                published_at=published_at,
                latitude=coords[1] if len(coords) == 2 else None,
                longitude=coords[0] if len(coords) == 2 else None,
            ))

        log.info(
            "ArbetsformedlingenSource: %d Jobs gefunden für '%s' in '%s'",
            len(results), keywords, location,
        )
        return results

    def _map_type(self, working_hours_type: dict | None) -> str | None:
        if not working_hours_type:
            return None
        label = (working_hours_type.get("label") or "").lower()
        if "deltid" in label:
            return "teilzeit"
        if "heltid" in label:
            return "vollzeit"
        return None
