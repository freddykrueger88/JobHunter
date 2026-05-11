"""Aggregiert Ergebnisse aus allen aktivierten Job-Quellen."""
from backend.services.job_search.base import RawJob
from backend.services.job_search.arbeitsagentur import ArbeitsagenturSource
from backend.services.job_search.adzuna import AdzunaSource
from backend.core.crypto import decrypt
import asyncio


async def search_all_sources(
    keywords: str,
    location: str,
    radius_km: int,
    settings_row,  # UserSettings ORM-Objekt
) -> list[RawJob]:
    sources = []

    # Arbeitsagentur (immer aktiv, kein Key nötig)
    aa_id = ""
    aa_secret = ""
    if settings_row.arbeitsagentur_client_id_enc:
        aa_id = decrypt(settings_row.arbeitsagentur_client_id_enc)
    if settings_row.arbeitsagentur_client_secret_enc:
        aa_secret = decrypt(settings_row.arbeitsagentur_client_secret_enc)
    sources.append(ArbeitsagenturSource(aa_id, aa_secret))

    # Adzuna (nur wenn Keys vorhanden)
    if settings_row.adzuna_app_id_enc and settings_row.adzuna_api_key_enc:
        sources.append(AdzunaSource(
            decrypt(settings_row.adzuna_app_id_enc),
            decrypt(settings_row.adzuna_api_key_enc),
        ))

    # Parallel suchen
    results_nested = await asyncio.gather(
        *[src.search(keywords, location, radius_km) for src in sources],
        return_exceptions=True,
    )

    # Flatten + Duplikate entfernen (per external_id)
    seen = set()
    all_jobs: list[RawJob] = []
    for batch in results_nested:
        if isinstance(batch, Exception):
            continue
        for job in batch:
            key = f"{job.source_portal}:{job.external_id}"
            if key not in seen:
                seen.add(key)
                all_jobs.append(job)
    return all_jobs
