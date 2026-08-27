# 🔍 Supported Job Portals / Unterstützte Job-Portale

🇩🇪 [Deutsche Version](#deutsch) | 🇬🇧 [English Version](#english)

---

## English

JobHunter searches multiple portals in parallel and deduplicates results.

## Portal Overview

| Portal | Adapter | Coverage | Key required? | Method | Status |
|--------|---------|----------|--------------|---------|--------|
| Bundesagentur für Arbeit | `arbeitsagentur.py` | 🇩🇪 Germany | ❌ No | Official REST API | ✅ Active |
| StepStone | `stepstone.py` | 🇩🇪 Germany | ❌ No | HTML scraping | ✅ Active |
| Adzuna | `adzuna.py` | 🇩🇪 Germany | ✅ Yes (free) | REST API | ✅ With key |
| LinkedIn | `linkedin.py` | 🇩🇪 Germany | ✅ Yes (OAuth2) | REST API | ✅ With key |
| EURES | `eures_scraper.py` | 🇪🇺 EU-wide (31 countries, country picker) | ❌ No | Official REST API | ✅ Active |
| Karriere.NRW | `karriere_nrw.py` | 🇩🇪 North Rhine-Westphalia (state + municipalities) | ❌ No | Open Data REST API | ✅ Active |
| service.bund.de | `service_bund.py` | 🇩🇪 Germany (federal + all 16 states + municipalities) | ❌ No | RSS export | ✅ Active |
| France Travail | `france_travail.py` | 🇫🇷 France | ✅ Yes (free, OAuth2) | Official REST API | ✅ With key |
| Arbetsförmedlingen | `arbetsformedlingen.py` | 🇸🇪 Sweden | ❌ No | Official REST API (JobTech) | ✅ Active |

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

## EURES
- **API**: https://europa.eu/eures/api/jv-searchengine/public/jv-search/search
- **Cost**: Free, public
- **Registration**: None
- **Note**: The EU's own official pan-European job board, covering the 31 EURES member countries. Select the target country in the Jobs page dropdown. Location results are resolved from EU NUTS region codes to place names via the official Eurostat/GISCO reference data.

## Karriere.NRW
- **API**: https://api.karriere.nrw/v1.0/opennrw/suche
- **Cost**: Free, public
- **Registration**: None
- **Note**: Open Data API of the German state of North Rhine-Westphalia, covering job postings from the state and its municipalities (cities, towns, districts) — the first source with real municipal-level coverage. Location/radius filtering is not passed through to the API (its own search space is state-limited anyway, and the documented location parameter does not work reliably).

## service.bund.de
- **Method**: RSS export of the search results (`jobsrss=true` query parameter), no API key or session needed
- **Cost**: Free, public
- **Registration**: None
- **Note**: Covers public-sector job postings across all of Germany — federal government, all 16 states, and municipalities (cities, towns, districts) — around 9,000 listings. Location and radius filtering work correctly.

## France Travail
- **API**: https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search
- **Cost**: Free with registration (OAuth2 client credentials)
- **Registration**: https://francetravail.io/inscription
- **Note**: France's national employment agency (formerly Pôle Emploi), ~300,000 listings. Only active when searching France and once you've entered your own free `client_id`/`client_secret` in Settings. Location is resolved from a free-text city name to an INSEE commune code via the official `geo.api.gouv.fr`.

## Arbetsförmedlingen
- **API**: https://jobsearch.api.jobtechdev.se/search
- **Cost**: Free, public
- **Registration**: None
- **Note**: Sweden's national employment agency, part of the "JobTech" open-data platform. Location is blended into the free-text search query rather than using the API's strict municipality filter, since that filter requires an exact, fully-spelled municipality name with no fuzzy matching.

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

| Portal | Adapter | Abdeckung | Key nötig? | Methode | Status |
|--------|---------|-----------|-----------|---------|--------|
| Bundesagentur für Arbeit | `arbeitsagentur.py` | 🇩🇪 Deutschland | ❌ Nein | Offizielle REST-API | ✅ Aktiv |
| StepStone | `stepstone.py` | 🇩🇪 Deutschland | ❌ Nein | HTML-Scraping | ✅ Aktiv |
| Adzuna | `adzuna.py` | 🇩🇪 Deutschland | ✅ Ja (kostenlos) | REST-API | ✅ Mit Key |
| LinkedIn | `linkedin.py` | 🇩🇪 Deutschland | ✅ Ja (OAuth2) | REST-API | ✅ Mit Key |
| EURES | `eures_scraper.py` | 🇪🇺 EU-weit (31 Länder, Länderauswahl) | ❌ Nein | Offizielle REST-API | ✅ Aktiv |
| Karriere.NRW | `karriere_nrw.py` | 🇩🇪 Nordrhein-Westfalen (Land + Kommunen) | ❌ Nein | Open-Data-REST-API | ✅ Aktiv |
| service.bund.de | `service_bund.py` | 🇩🇪 Deutschland (Bund + alle 16 Länder + Kommunen) | ❌ Nein | RSS-Export | ✅ Aktiv |
| France Travail | `france_travail.py` | 🇫🇷 Frankreich | ✅ Ja (kostenlos, OAuth2) | Offizielle REST-API | ✅ Mit Key |
| Arbetsförmedlingen | `arbetsformedlingen.py` | 🇸🇪 Schweden | ❌ Nein | Offizielle REST-API (JobTech) | ✅ Aktiv |

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

## EURES
- Kostenlos, öffentlich, keine Registrierung
- Das offizielle EU-weite Jobportal, deckt alle 31 EURES-Länder ab (Länderauswahl im Jobs-Dropdown). Ortsnamen werden über die offizielle Eurostat/GISCO-NUTS-Referenztabelle aufgelöst.

## Karriere.NRW
- Kostenlos, öffentlich, keine Registrierung
- Open-Data-API des Landes NRW für Stellen von Land und Kommunen (Städte, Gemeinden, Landkreise) - erste Quelle mit echter Kommunalebene. Orts-/Radius-Filter werden nicht durchgereicht (der dokumentierte Parameter liefert live keine verlässlichen Ergebnisse).

## service.bund.de
- Kostenlos, öffentlich, keine Registrierung
- RSS-Export der Suchergebnisse, kein Session-Cookie nötig. Deckt öffentliche Stellen von Bund, allen 16 Ländern und Kommunen bundesweit ab (~9.000 Ausschreibungen). Orts-/Radius-Filter funktionieren korrekt.

## France Travail
- Kostenlos mit Registrierung (OAuth2-Zugangsdaten): https://francetravail.io/inscription
- Französische nationale Arbeitsagentur (ehem. Pôle Emploi), ~300.000 Stellen. Nur aktiv bei Suche in Frankreich und nach Eintragen eigener `client_id`/`client_secret` in den Einstellungen. Ortsauflösung über `geo.api.gouv.fr`.

## Arbetsförmedlingen
- Kostenlos, öffentlich, keine Registrierung
- Schwedische nationale Arbeitsagentur, Teil der offenen "JobTech"-Plattform. Ort wird ins Freitext-Suchfeld eingemischt statt über einen strikten Gemeinde-Filter (der braucht exakte Schreibweise ohne Fuzzy-Matching).

## Neues Portal hinzufügen

```python
class MeinPortalSource(BaseJobSource):
    async def search(self, keywords: str, location: str, radius_km: int) -> list[RawJob]:
        ...
        return [RawJob(title=..., company=..., source_portal="meinportal")]
```
