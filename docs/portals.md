# Unterstützte Job-Portale

JobHunter durchsucht mehrere Portale parallel und dedupliziert die Ergebnisse.

## Portal-Übersicht

| Portal | Adapter | Key nötig? | Methode | Status |
|--------|---------|-----------|---------|--------|
| Bundesagentur für Arbeit | `arbeitsagentur.py` | ❌ Nein | Offizielle REST-API | ✅ Aktiv |
| StepStone | `stepstone.py` | ❌ Nein | HTML-Scraping | ✅ Aktiv |
| Adzuna | `adzuna.py` | ✅ Ja (kostenlos) | REST-API | ✅ Mit Key |
| LinkedIn | `linkedin.py` | ✅ Ja (OAuth2) | REST-API | ✅ Mit Key |

## Bundesagentur für Arbeit
- **API**: https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs
- **Kosten**: Kostenlos, öffentlich
- **Registrierung**: Optional (höheres Rate-Limit mit Client-ID)
- **Besonderheit**: Offizielle Regierungsquelle, sehr zuverlässig

## StepStone
- **Methode**: HTML-Scraping (kein offizielles API)
- **Kosten**: Kostenlos
- **Rate-Limit**: Max. 1 Anfrage/Suche, User-Agent wird gesetzt
- **Hinweis**: Nur für persönlichen Gebrauch. Selektor-Pfade können sich bei
  StepStone-Updates ändern – dann `stepstone.py` anpassen.
- **Robots.txt**: `/jobs` ist nicht gesperrt (Stand Mai 2026)

## Adzuna
- **API**: https://api.adzuna.com/v1/api/jobs/de/search/
- **Kosten**: Kostenlos mit Registrierung (1000 Anfragen/Tag)
- **Registrierung**: https://developer.adzuna.com/
- **Aggregiert**: Indeed, Monster, diverse Jobbörsen

## LinkedIn
- **API**: LinkedIn Jobs API (v2)
- **Kosten**: Erfordert LinkedIn Developer App + genehmigten API-Zugang
- **Registrierung**: https://developer.linkedin.com/
- **Hinweis**: LinkedIn-API-Zugang ist restriktiv – Alternative: LinkedIn Job Search
  über Adzuna (aggregiert LinkedIn-Stellen mit).

## Neue Portale hinzufügen

1. Neue Datei in `backend/services/job_search/` anlegen
2. `BaseJobSource` importieren und `search()`-Methode implementieren
3. Ergebnisse als `RawJob`-Objekte zurückgeben
4. In `aggregator.py` einbinden

```python
class MeinPortalSource(BaseJobSource):
    async def search(self, keywords: str, location: str, radius_km: int) -> list[RawJob]:
        ...
        return [RawJob(title=..., company=..., source_portal="meinportal")]
```
