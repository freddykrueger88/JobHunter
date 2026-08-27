"""France Travail (bis 2024 "Pole Emploi") - franzoesische nationale Jobboerse,
das FR-Gegenstueck zur deutschen Arbeitsagentur-Quelle, ~300.000 Stellen in
Echtzeit. Anders als alle anderen in dieser Session hinzugefuegten Quellen
gibt es keinen oeffentlichen Fest-Key: der Nutzer muss sich selbst kostenlos
unter https://francetravail.io/inscription registrieren und eigene OAuth2-
Zugangsdaten (client_id/client_secret) in den Einstellungen hinterlegen -
genau wie beim bereits vorhandenen Adzuna/LinkedIn-Muster in diesem Projekt.

Live gegengetestet (ohne eigene Zugangsdaten moeglich): Token-Endpoint
antwortet mit einem echten OAuth2-Fehler ("invalid_client") statt 404/Fehler-
seite, Such-Endpoint antwortet mit 401 statt 404 - beide Endpunkte existieren
und sind aktuell. Das Response-Format (Feldnamen wie "intitule"/"lieuTravail"/
"origineOffre"/"dateCreation") stammt aus offizieller Doku + mehreren
unabhaengigen Referenzimplementierungen, konnte aber OHNE eigene
Zugangsdaten nicht mit echten Daten live verifiziert werden (anders als
EURES/Karriere.NRW/service.bund.de in dieser Session, die alle ohne
Nutzer-Key auskommen). Bitte nach Eintragen eigener Zugangsdaten einmal
live pruefen.

Ort wird ueber die offizielle franzoesische Geo-API (geo.api.gouv.fr, kein
Key noetig) von Freitext-Stadtname zu INSEE-Gemeindecode aufgeloest
(boost=population loest Mehrdeutigkeiten zugunsten der bevoelkerungsreichsten
gleichnamigen Stadt) - live verifiziert (z.B. "Lyon" -> "69123").
"""
from __future__ import annotations

import logging
import time
from datetime import datetime

import httpx

from backend.services.job_search.base import BaseJobSource, RawJob

log = logging.getLogger(__name__)

TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire"
SEARCH_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"
GEO_URL = "https://geo.api.gouv.fr/communes"
SCOPE = "api_offresdemploiv2 o2dsoffre"

# In-Memory-Cache fuer OAuth2-Access-Tokens, keyed nach client_id (Ablauf
# 60s vor der eigentlichen expires_in-Grenze als Sicherheitsmarge).
_token_cache: dict[str, tuple[str, float]] = {}


async def _get_token(client_id: str, client_secret: str) -> str | None:
    cached = _token_cache.get(client_id)
    if cached and cached[1] > time.time():
        return cached[0]

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                TOKEN_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "scope": SCOPE,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        log.error("FranceTravailSource: Token-Anfrage fehlgeschlagen: %s", e)
        return None

    token = data.get("access_token")
    expires_in = data.get("expires_in", 1200)
    if token:
        _token_cache[client_id] = (token, time.time() + expires_in - 60)
    return token


async def _resolve_commune(location: str) -> str | None:
    """Loest einen Freitext-Ortsnamen zu einem INSEE-Gemeindecode auf (von
    der Such-API als "commune"-Parameter gefordert, kein Freitext moeglich)."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(GEO_URL, params={
                "nom": location, "fields": "code", "boost": "population", "limit": 1,
            })
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        log.warning("FranceTravailSource: Gemeinde-Aufloesung für '%s' fehlgeschlagen: %s", location, e)
        return None
    return data[0]["code"] if data else None


class FranceTravailSource(BaseJobSource):
    """Franzoesische nationale Jobboerse (ex-Pole Emploi). Benoetigt vom
    Nutzer selbst registrierte, kostenlose OAuth2-Zugangsdaten (siehe
    Moduldoku oben)."""

    def __init__(self, client_id: str | None, client_secret: str | None):
        self.client_id = client_id
        self.client_secret = client_secret

    async def search(self, keywords: str, location: str, radius_km: int = 25) -> list[RawJob]:
        if not self.client_id or not self.client_secret:
            return []

        token = await _get_token(self.client_id, self.client_secret)
        if not token:
            return []

        params: dict[str, str | int] = {"motsCles": keywords, "range": "0-49"}
        if location:
            commune = await _resolve_commune(location)
            if commune:
                params["commune"] = commune
                params["distance"] = radius_km

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(
                    SEARCH_URL, params=params,
                    headers={"Authorization": f"Bearer {token}"},
                )
                r.raise_for_status()
                data = r.json()
        except httpx.TimeoutException:
            log.error("FranceTravailSource: Timeout")
            return []
        except httpx.HTTPStatusError as e:
            log.error("FranceTravailSource: HTTP %s", e.response.status_code)
            return []
        except Exception as e:
            log.exception("FranceTravailSource: Unerwarteter Fehler: %s", e)
            return []

        results: list[RawJob] = []
        for item in data.get("resultats", []):
            entreprise = item.get("entreprise") or {}
            lieu = item.get("lieuTravail") or {}
            origine = item.get("origineOffre") or {}

            pub_date_raw = item.get("dateCreation")
            published_at = None
            if pub_date_raw:
                try:
                    published_at = datetime.fromisoformat(pub_date_raw.replace("Z", "+00:00"))
                except ValueError:
                    published_at = None

            offer_id = item.get("id", "")
            title = item.get("intitule", "")
            if not title:
                continue

            results.append(RawJob(
                title=title,
                company=entreprise.get("nom") or "",
                city=lieu.get("libelle"),
                postal_code=lieu.get("codePostal"),
                description=item.get("description"),
                url=origine.get("urlOrigine") or None,
                # "alternance" (Ausbildung/duales Studium) ist ein bestaetigtes
                # Feld der API; eine Vollzeit/Teilzeit-Unterscheidung wird
                # bewusst NICHT geraten - der exakte Feldname dafuer konnte
                # ohne eigene Zugangsdaten nicht live verifiziert werden.
                job_type="ausbildung" if item.get("alternance") else None,
                source_portal="france_travail",
                external_id=f"france_travail_{offer_id}" if offer_id else None,
                published_at=published_at,
                latitude=lieu.get("latitude"),
                longitude=lieu.get("longitude"),
            ))

        log.info(
            "FranceTravailSource: %d Jobs gefunden für '%s' in '%s'",
            len(results), keywords, location,
        )
        return results
