# 🔍 Supported Job Portals / Unterstützte Job-Portale

🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

---

## English

JobHunter searches multiple portals in parallel and deduplicates results.

## Portal Overview

| Portal | Adapter | Key required? | Method | Status |
|--------|---------|--------------|---------|--------|
| Bundesagentur für Arbeit | `arbeitsagentur.py` | ❌ No | Official REST API | ✅ Active |
| StepStone | `stepstone.py` | ❌ No | HTML scraping | ✅ Active |
| Adzuna | `adzuna.py` | ✅ Yes (free) | REST API | ✅ With key |
| LinkedIn | `linkedin.py` | ✅ Yes (OAuth2) | REST API | ✅ With key |

## Bundesagentur für Arbeit
- **API**: https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs
- **Cost**: Free, public
- **Registration**: Optional (higher rate limit with Client ID)
- **Note**: Official government source, very reliable

## StepStone
- **Method**: HTML scraping (no official API)
- **Cost**: Free
- **Rate limit**: Max. 1 request/search, User-Agent is set
- **Note**: For personal use only. Selector paths may change on StepStone updates – update `stepstone.py` accordingly.
- **Robots.txt**: `/jobs` is not blocked (as of May 2026)

## Adzuna
- **API**: https://api.adzuna.com/v1/api/jobs/de/search/
- **Cost**: Free with registration (1000 requests/day)
- **Registration**: https://developer.adzuna.com/
- **Aggregates**: Indeed, Monster, various job boards

## LinkedIn
- **API**: LinkedIn Jobs API (v2)
- **Cost**: Requires LinkedIn Developer App + approved API access
- **Registration**: https://developer.linkedin.com/
- **Note**: LinkedIn API access is restrictive – alternative: LinkedIn jobs via Adzuna (aggregates LinkedIn listings).

## Adding New Portals

1. Create new file in `backend/services/job_search/`
2. Import `BaseJobSource` and implement `search()` method
3. Return results as `RawJob` objects
4. Register in `aggregator.py`

```python
class MyPortalSource(BaseJobSource):
    async def search(self, keywords: str, location: str, radius_km: int) -> list[RawJob]:
        ...
        return [RawJob(title=..., company=..., source_portal="myportal")]
```

---
---

## Deutsch

JobHunter durchsucht mehrere Portale parallel und dedupliziert die Ergebnisse.

## Portal-Übersicht

| Portal | Adapter | Key nötig? | Methode | Status |
|--------|---------|-----------|---------|--------|
| Bundesagentur für Arbeit | `arbeitsagentur.py` | ❌ Nein | Offizielle REST-API | ✅ Aktiv |
| StepStone | `stepstone.py` | ❌ Nein | HTML-Scraping | ✅ Aktiv |
| Adzuna | `adzuna.py` | ✅ Ja (kostenlos) | REST-API | ✅ Mit Key |
| LinkedIn | `linkedin.py` | ✅ Ja (OAuth2) | REST-API | ✅ Mit Key |

## Bundesagentur für Arbeit
- Kostenlos, öffentlich – sehr zuverlässig
- Registrierung optional (höheres Rate-Limit)

## StepStone
- HTML-Scraping, kein offizielles API
- Nur für persönlichen Gebrauch
- Robots.txt: `/jobs` nicht gesperrt (Stand Mai 2026)

## Adzuna
- Kostenlos mit Registrierung (1000 Anfragen/Tag)
- Aggregiert Indeed, Monster u.a.

## LinkedIn
- Erfordert Developer App + genehmigten API-Zugang
- Alternative: LinkedIn-Jobs über Adzuna beziehen

## Neues Portal hinzufügen

```python
class MeinPortalSource(BaseJobSource):
    async def search(self, keywords: str, location: str, radius_km: int) -> list[RawJob]:
        ...
        return [RawJob(title=..., company=..., source_portal="meinportal")]
```
