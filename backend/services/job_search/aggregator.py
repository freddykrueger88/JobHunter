"""Aggregiert Ergebnisse aus allen aktivierten Job-Quellen."""
import asyncio
import logging
from backend.services.job_search.base import RawJob
from backend.services.job_search.arbeitsagentur import ArbeitsagenturSource
from backend.services.job_search.adzuna import AdzunaSource
from backend.services.job_search.stepstone import StepStoneSource
from backend.services.job_search.linkedin import LinkedInSource
from backend.core.crypto import decrypt

log = logging.getLogger(__name__)


async def search_all_sources(
    keywords: str,
    location: str,
    radius_km: int,
    settings_row,
) -> list[RawJob]:
    sources = []

    # 1. Bundesagentur für Arbeit (immer aktiv, benötigt keinen Nutzer-Key)
    #    Die API nutzt einen öffentlichen API-Key, der im Adapter fest hinterlegt ist.
    sources.append(ArbeitsagenturSource())

    # 2. StepStone (immer aktiv, kein Key nötig)
    sources.append(StepStoneSource())

    # 3. Adzuna (nur mit Keys)
    if getattr(settings_row, "adzuna_app_id_enc", None) and getattr(settings_row, "adzuna_api_key_enc", None):
        sources.append(AdzunaSource(
            decrypt(settings_row.adzuna_app_id_enc),
            decrypt(settings_row.adzuna_api_key_enc),
        ))

    # 4. LinkedIn (nur mit Key)
    if getattr(settings_row, "linkedin_api_key_enc", None):
        sources.append(LinkedInSource(decrypt(settings_row.linkedin_api_key_enc)))

    log.info(
        "Aggregator: Suche '%s' in '%s' (%d km) über %d Quelle(n)",
        keywords, location, radius_km, len(sources)
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
