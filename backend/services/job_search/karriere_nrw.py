"""Karriere.NRW – Open-Data-API des Landes NRW fuer oeffentliche
Stellenausschreibungen (Land + Kommunen: Staedte, Gemeinden, Landkreise).

Phase I.1 (EU-weite Jobboersen, Teil 2 - Portale unterhalb von EURES):
erster echter Kommunalebene-Fund - eine offizielle, dokumentierte
RESTful-JSON-API (https://karriere.nrw/karriere.nrw-opendata-api.pdf,
Stand 2020), live gegen echte Daten verifiziert (1105 offene Stellen,
u.a. von kleinen Staedten wie Meerbusch, Kamen, Korschenbroich -
niemand aus einer der grossen deutschen Staedte, das ist genau die
Kommunalebene aus der urspruenglichen Nutzervision).

Wichtig: das Antwortformat des Such-Endpoints (`/suche`) weicht von der
2020er PDF-Doku ab - die Doku beschreibt deutsche Feldnamen
(titel_der_stelle, ausschreibende_behoerde, ort), die Live-API liefert
inzwischen englische Kurzfeldnamen (title, authority, location) in
einem "items"-Array (Doku: "results"). Nur der Detail-Endpoint
(/stellenausschreibungen/<uuid>) folgt noch exakt der Doku. Deshalb
gegen die tatsaechliche Live-Antwort implementiert, nicht gegen die PDF
- gleiche Lektion wie beim EURES-Fund zuvor in dieser Session.

Die Detail-URL (https://karriere.nrw/stellenausschreibung/<uuid>) ist
NICHT geraten: der Detail-Endpoint liefert selbst ein `url`-Feld mit
genau diesem Muster fuer denselben Datensatz - anders als bei EURES
hier also echt bestaetigt, kein unverifizierter Konstruktions-Versuch.
"""
from __future__ import annotations

import logging
from datetime import datetime

import httpx

from backend.services.job_search.base import BaseJobSource, RawJob, safe_get

log = logging.getLogger(__name__)

SEARCH_URL = "https://api.karriere.nrw/v1.0/opennrw/suche"
DETAIL_URL_TEMPLATE = "https://karriere.nrw/stellenausschreibung/{uuid}"


class KarriereNrwSource(BaseJobSource):
    """Oeffentliche Stellenausschreibungen des Landes NRW und seiner
    Kommunen (Open-Data-API, kein API-Key noetig).

    Ort/Radius werden NICHT an die API durchgereicht: der dokumentierte
    ort-Parameter (PDF-Beispiel "ort=Bochum") liefert live selbst fuer
    Staedte mit nachweislich vorhandenen Treffern 0 Ergebnisse (z.B.
    "ort=Krefeld" trotz eines Krefeld-Jobs im ungefilterten Datensatz) -
    live gegengetestet, kein Tippfehler. Wuerde man ihn trotzdem
    durchreichen, liefe diese Quelle in der echten App (die immer einen
    Ort mitschickt) faktisch immer leer. Stattdessen: reine
    Stichwortsuche ueber ganz NRW - die App-weite Umkreissuche gilt fuer
    diese Quelle nicht, ihr Suchraum ist ohnehin auf NRW begrenzt."""

    async def search(self, keywords: str, location: str, radius_km: int = 25) -> list[RawJob]:
        params: dict[str, str] = {}
        if keywords:
            params["text"] = keywords

        async with httpx.AsyncClient(timeout=15) as client:
            r = await safe_get(client, SEARCH_URL, "KarriereNrwSource", params=params, headers={"Accept": "application/json"})
        if r is None:
            return []
        data = r.json()

        results: list[RawJob] = []
        for item in data.get("items", []):
            uuid = item.get("uuid", "")
            published = item.get("published")
            try:
                published_at = datetime.fromisoformat(published) if published else None
            except ValueError:
                published_at = None

            results.append(RawJob(
                title=item.get("title", ""),
                company=item.get("authority") or item.get("contracting_authority") or "",
                city=item.get("location"),
                description=None,  # nur ueber den Detail-Endpoint verfuegbar, hier bewusst nicht N+1 nachgeladen
                url=DETAIL_URL_TEMPLATE.format(uuid=uuid) if uuid else None,
                job_type="ausbildung" if item.get("jobtype") == "apprenticeship" else None,
                source_portal="karriere_nrw",
                external_id=f"karriere_nrw_{uuid}" if uuid else None,
                published_at=published_at,
            ))

        log.info(
            "KarriereNrwSource: %d Jobs gefunden für '%s' in '%s' (von %d Treffern gesamt)",
            len(results), keywords, location, data.get("count", len(results)),
        )
        return results
