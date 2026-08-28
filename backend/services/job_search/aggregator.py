"""Aggregiert Ergebnisse aus allen aktivierten Job-Quellen."""
import asyncio
import logging
from backend.services.job_search.base import RawJob
from backend.services.job_search.arbeitsagentur import ArbeitsagenturSource
from backend.services.job_search.adzuna import AdzunaSource
from backend.services.job_search.linkedin import LinkedInSource
from backend.services.job_search.eures_scraper import EuresSource
from backend.services.job_search.karriere_nrw import KarriereNrwSource
from backend.services.job_search.service_bund import ServiceBundSource
from backend.services.job_search.france_travail import FranceTravailSource
from backend.services.job_search.arbetsformedlingen import ArbetsformedlingenSource
from backend.core.crypto import decrypt

log = logging.getLogger(__name__)


async def search_all_sources(
    keywords: str,
    location: str,
    radius_km: int,
    settings_row,
    country_code: str = "DE",
) -> list[RawJob]:
    sources = []

    # 1. Bundesagentur für Arbeit (immer aktiv, benötigt keinen Nutzer-Key) -
    #    nur sinnvoll fuer Deutschland, Country-Auswahl betrifft sie nicht.
    #    Die API nutzt einen öffentlichen API-Key, der im Adapter fest hinterlegt ist.
    if country_code == "DE":
        sources.append(ArbeitsagenturSource())

    # StepStone (HTML-Scraper) 2026-08-28 entfernt: stepstone.de hat eine
    # aktive Akamai-Bot-Schutzmauer vor die Suchergebnisse geschaltet
    # (JS-Challenge-Interstitial) UND robots.txt verbietet inzwischen
    # explizit das genutzte Anfrage-Muster (/jobs?q=*&*). Beides zusammen
    # signalisiert klar, dass automatisierter Zugriff nicht mehr geduldet
    # ist - anders als die dokumentierten APIs der uebrigen Quellen. Live
    # verifiziert (docker logs zeigten 0 Ergebnisse, Rohantwort war die
    # Akamai-Challenge-Seite). Nutzerentscheidung: nicht versuchen zu
    # umgehen, Quelle sauber abschalten statt sie umzubauen. Code-Historie
    # in Git erhalten (siehe Commit dieser Aenderung).

    # 3. Adzuna (nur mit Keys)
    if getattr(settings_row, "adzuna_app_id_enc", None) and getattr(settings_row, "adzuna_api_key_enc", None):
        sources.append(AdzunaSource(
            decrypt(settings_row.adzuna_app_id_enc),
            decrypt(settings_row.adzuna_api_key_enc),
        ))

    # 4. LinkedIn (nur mit Key)
    if getattr(settings_row, "linkedin_api_key_enc", None):
        sources.append(LinkedInSource(decrypt(settings_row.linkedin_api_key_enc)))

    # 5. EURES (immer aktiv, kein Key noetig, einzige Quelle mit echter
    #    EU-weiter Abdeckung - #72/Phase I.1). War fertig implementiert,
    #    aber nie hier registriert; die alte API-URL war zudem tot (404).
    sources.append(EuresSource(country_code=country_code))

    # 6. Karriere.NRW (Open-Data-API des Landes NRW, oeffentliche Stellen
    #    von Land + Kommunen - erster echter Kommunalebene-Fund fuer
    #    Phase I.1, nur fuer DE relevant).
    if country_code == "DE":
        sources.append(KarriereNrwSource())

    # 7. service.bund.de (RSS-Export, oeffentlicher Dienst - Bund, alle 16
    #    Laender UND Kommunen bundesweit, ~9.000 Ausschreibungen, nur DE).
    #    Anders als Karriere.NRW: Orts-/Radius-Filter live nachweislich korrekt.
    if country_code == "DE":
        sources.append(ServiceBundSource())

    # 8. France Travail (FR-Gegenstueck zur Arbeitsagentur, ~300.000
    #    Stellen). Anders als alle bisherigen Quellen braucht sie eigene,
    #    vom Nutzer selbst registrierte OAuth2-Zugangsdaten (wie Adzuna/
    #    LinkedIn oben) - kein oeffentlicher Fest-Key verfuegbar.
    if country_code == "FR" and getattr(settings_row, "francetravail_client_id_enc", None) and getattr(settings_row, "francetravail_client_secret_enc", None):
        sources.append(FranceTravailSource(
            decrypt(settings_row.francetravail_client_id_enc),
            decrypt(settings_row.francetravail_client_secret_enc),
        ))

    # 9. Arbetsformedlingen (schwedische Arbeitsagentur, JobTech-Plattform).
    #    Wieder zero-config wie Arbeitsagentur/EURES/Karriere.NRW/
    #    service.bund.de - oeffentliche API, kein Nutzer-Key noetig.
    if country_code == "SE":
        sources.append(ArbetsformedlingenSource())

    log.info(
        "Aggregator: Suche '%s' in '%s' (%d km, Land %s) über %d Quelle(n)",
        keywords, location, radius_km, country_code, len(sources)
    )

    if not sources:
        log.warning("Aggregator: Keine aktiven Job-Quellen konfiguriert")
        return []

    # Parallel suchen
    results_nested = await asyncio.gather(
        *[src.search(keywords, location, radius_km) for src in sources],
        return_exceptions=True,
    )

    # Flatten + Duplikate herausfiltern
    seen: set[str] = set()
    all_jobs: list[RawJob] = []
    for i, batch in enumerate(results_nested):
        source_name = type(sources[i]).__name__
        if isinstance(batch, Exception):
            log.error("Aggregator: Quelle '%s' hat eine Exception geworfen: %s", source_name, batch)
            continue
        for job in batch:
            key = f"{job.source_portal}:{job.external_id or job.title + job.company}"
            if key not in seen:
                seen.add(key)
                all_jobs.append(job)

    log.info("Aggregator: %d eindeutige Jobs gesamt", len(all_jobs))
    return all_jobs
