"""Duplikat-Erkennung fuer Stellenangebote via Fuzzy-Matching."""
from __future__ import annotations
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models import Job

try:
    from rapidfuzz import fuzz
    def _similarity(a: str, b: str) -> float:
        return fuzz.token_sort_ratio(a.lower(), b.lower()) / 100
except ImportError:
    def _similarity(a: str, b: str) -> float:
        a, b = a.lower().split(), b.lower().split()
        common = set(a) & set(b)
        return len(common) / max(len(set(a) | set(b)), 1)

THRESHOLD = 0.75


async def find_duplicates(job_id: int, db: AsyncSession) -> List[dict]:
    """Findet aehnliche Stellen zu einem gegebenen Job."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        return []

    all_jobs_result = await db.execute(
        select(Job).where(Job.id != job_id)
    )
    all_jobs = all_jobs_result.scalars().all()

    duplicates = []
    for other in all_jobs:
        title_sim = _similarity(job.title or '', other.title or '')
        company_sim = _similarity(job.company or '', other.company or '')
        city_sim = _similarity(job.city or '', other.city or '')
        score = title_sim * 0.5 + company_sim * 0.35 + city_sim * 0.15
        if score >= THRESHOLD:
            duplicates.append({
                'id': other.id,
                'title': other.title,
                'company': other.company,
                'city': other.city,
                'similarity_score': round(score, 2),
                'created_at': other.created_at,
            })

    return sorted(duplicates, key=lambda x: x['similarity_score'], reverse=True)


async def check_before_create(title: str, company: str, city: str, db: AsyncSession) -> List[dict]:
    """Prueft vor dem Anlegen ob aehnliche Stellen existieren."""
    all_jobs_result = await db.execute(select(Job))
    all_jobs = all_jobs_result.scalars().all()

    duplicates = []
    for other in all_jobs:
        title_sim = _similarity(title or '', other.title or '')
        company_sim = _similarity(company or '', other.company or '')
        city_sim = _similarity(city or '', other.city or '')
        score = title_sim * 0.5 + company_sim * 0.35 + city_sim * 0.15
        if score >= THRESHOLD:
            duplicates.append({
                'id': other.id,
                'title': other.title,
                'company': other.company,
                'city': other.city,
                'similarity_score': round(score, 2),
            })
    return sorted(duplicates, key=lambda x: x['similarity_score'], reverse=True)
