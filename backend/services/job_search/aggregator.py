"""Aggregiert Ergebnisse aus allen aktivierten Job-Quellen."""
from backend.services.job_search.base import RawJob
from backend.services.job_search.arbeitsagentur import ArbeitsagenturSource
from backend.services.job_search.adzuna import AdzunaSource
from backend.services.job_search.stepstone import StepStoneSource
from backend.services.job_search.linkedin import LinkedInSource
from backend.core.crypto import decrypt
import asyncio


async def search_all_sources(
    keywords: str,
    location: str,
    radius_km: int,
    settings_row,
) -> list[RawJob]:
    sources = []

    # 1. Bundesagentur für Arbeit (immer aktiv)
    aa_id, aa_secret = "", ""
    if getattr(settings_row, "arbeitsagentur_client_id_enc", None):
        aa_id = decrypt(settings_row.arbeitsagentur_client_id_enc)
    if getattr(settings_row, "arbeitsagentur_client_secret_enc", None):
        aa_secret = decrypt(settings_row.arbeitsagentur_client_secret_enc)
    sources.append(ArbeitsagenturSource(aa_id, aa_secret))

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

    # Parallel suchen
    results_nested = await asyncio.gather(
        *[src.search(keywords, location, radius_km) for src in sources],
        return_exceptions=True,
    )

    # Flatten + Duplikate herausfiltern
    seen: set[str] = set()
    all_jobs: list[RawJob] = []
    for batch in results_nested:
        if isinstance(batch, Exception):
            continue
        for job in batch:
            key = f"{job.source_portal}:{job.external_id or job.title+job.company}"
            if key not in seen:
                seen.add(key)
                all_jobs.append(job)
    return all_jobs
