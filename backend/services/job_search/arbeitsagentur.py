"""Bundesagentur für Arbeit – Jobsuche API.

Öffentliche API – kein Nutzer-API-Key nötig.
Authentifizierung erfolgt über den festen Public-Key 'jobboerse-jobsuche'
als X-API-Key Header (dokumentiert auf https://jobsuche.api.bund.dev/).

**Migration v4 -> v6 (2026-08-28):** die alte pc/v4/jobs-URL liefert seit
kurzem HTTP 403 - live mit rohem httpx (auch ohne X-API-Key, auch per
WebFetch von komplett anderer Infrastruktur aus) reproduziert, also kein
Problem dieses Deployments. Recherche (github.com/bundesAPI/jobsuche-api,
aktuelle OpenAPI-Spec) ergab: der Endpoint wurde auf pc/v6/jobs
umgezogen, mit einem substanziell anderen Response-Schema (nicht nur
umbenannt) - live gegen echte Daten verifiziert, nicht nur aus der
Doku uebernommen:
- Top-Level-Key "ergebnisliste" statt "stellenangebote"
- Titel "stellenangebotsTitel" statt "beruf", Firma "firma" statt
  "arbeitgeber"-Objekt
- Ort/Koordinaten jetzt in "stellenlokationen" (Liste, nicht mehr ein
  einzelnes "arbeitsort"-Objekt) - erster Eintrag wird verwendet
- Arbeitszeit als einzelne Boolean-Flags (arbeitszeitVollzeit/
  arbeitszeitTeilzeit*) statt einer Freitext-Liste, plus
  stellenangebotsart="AUSBILDUNG"|"ARBEIT" auf oberster Ebene
- **Stellenbeschreibung ist NICHT mehr im Suchergebnis enthalten** -
  anders als bei v4 muss sie separat pro Job ueber
  pc/v4/jobdetails/{base64(referenznummer)} nachgeladen werden (Feld
  stellenangebotsBeschreibung). Parallelisiert per asyncio.gather, damit
  eine Suche nicht sequenziell durch alle Treffer laufen muss.
- Die menschenlesbare Detailseite (anders als bei anderen Quellen in
  diesem Projekt NICHT nur plausibel konstruiert, sondern per WebFetch
  echt geladen und inhaltlich bestaetigt) ist weiterhin
  arbeitsagentur.de/jobsuche/jobdetail/{referenznummer} - nur der
  fruehere hashId-Parameter existiert im v6-Suchergebnis nicht mehr,
  referenznummer uebernimmt dieselbe Rolle.
"""
import asyncio
import base64
import logging
from urllib.parse import quote

import httpx

from backend.services.job_search.base import BaseJobSource, RawJob, safe_get
from datetime import datetime

log = logging.getLogger(__name__)

BASE_URL = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v6/jobs"
DETAILS_URL_TEMPLATE = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobdetails/{code}"
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
        async with httpx.AsyncClient() as client:
            r = await safe_get(client, BASE_URL, "ArbeitsagenturSource", params=params, headers=headers, timeout=15)
            if r is None:
                return []
            data = r.json()

            items = data.get("ergebnisliste", [])
            descriptions = await asyncio.gather(
                *[self._fetch_description(client, headers, item.get("referenznummer")) for item in items]
            )

        results = []
        for item, description in zip(items, descriptions):
            lokationen = item.get("stellenlokationen") or [{}]
            adresse = (lokationen[0].get("adresse") or {})
            refnr = item.get("referenznummer") or ""
            results.append(RawJob(
                title=item.get("stellenangebotsTitel", ""),
                company=item.get("firma", ""),
                city=adresse.get("ort"),
                postal_code=adresse.get("plz"),
                address=adresse.get("strasse"),
                description=description,
                url=f"https://www.arbeitsagentur.de/jobsuche/jobdetail/{quote(refnr)}" if refnr else None,
                job_type=self._map_job_type(item),
                source_portal="arbeitsagentur",
                external_id=refnr or None,
                published_at=self._parse_date(item.get("datumErsteVeroeffentlichung")),
                latitude=lokationen[0].get("breite"),
                longitude=lokationen[0].get("laenge"),
            ))
        log.info(
            "ArbeitsagenturSource: %d Jobs gefunden für '%s' in '%s'",
            len(results), keywords, location,
        )
        return results

    async def _fetch_description(self, client: httpx.AsyncClient, headers: dict, refnr: str | None) -> str | None:
        if not refnr:
            return None
        code = base64.b64encode(refnr.encode()).decode()
        r = await safe_get(client, DETAILS_URL_TEMPLATE.format(code=code), "ArbeitsagenturSource (Details)", headers=headers, timeout=15)
        if r is None:
            return None
        return r.json().get("stellenangebotsBeschreibung")

    def _map_job_type(self, item: dict) -> str | None:
        if item.get("stellenangebotsart") == "AUSBILDUNG":
            return "ausbildung"
        if item.get("arbeitszeitVollzeit"):
            return "vollzeit"
        if any(item.get(k) for k in (
            "arbeitszeitTeilzeitAbend", "arbeitszeitTeilzeitNachmittag",
            "arbeitszeitTeilzeitVormittag", "arbeitszeitTeilzeitFlexibel",
        )):
            return "teilzeit"
        return None

    def _parse_date(self, s: str | None) -> datetime | None:
        if not s:
            return None
        try:
            return datetime.fromisoformat(s)
        except Exception:
            return None
