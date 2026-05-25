"""StepStone-Scraper via httpx + BeautifulSoup.
Nur für den persönlichen Gebrauch. robots.txt wird respektiert.
"""
import httpx
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from backend.services.job_search.base import BaseJobSource, RawJob

log = logging.getLogger(__name__)

BASE_URL = "https://www.stepstone.de/jobs"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "de-DE,de;q=0.9",
    "Accept": "text/html,application/xhtml+xml",
}


class StepStoneSource(BaseJobSource):
    """Scraped StepStone-Suchergebnisse. Kein API-Key nötig."""

    async def search(self, keywords: str, location: str, radius_km: int = 25) -> list[RawJob]:
        params = {
            "q": keywords,
            "loc": location,
            "radius": radius_km,
            "of": 0,
        }
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=20) as client:
                r = await client.get(BASE_URL, params=params, headers=HEADERS)
                r.raise_for_status()
                html = r.text
        except httpx.TimeoutException:
            log.error("StepStoneSource: Timeout")
            return []
        except httpx.HTTPStatusError as e:
            log.error("StepStoneSource: HTTP %s", e.response.status_code)
            return []
        except Exception as e:
            log.exception("StepStoneSource: Unerwarteter Fehler: %s", e)
            return []

        results = self._parse(html)
        log.info("StepStoneSource: %d Jobs gefunden für '%s' in '%s'", len(results), keywords, location)
        if not results:
            log.warning(
                "StepStoneSource: 0 Ergebnisse – möglicherweise haben sich die HTML-Selektoren geändert. "
                "Bitte stepstone.py/_parse() prüfen."
            )
        return results

    def _parse(self, html: str) -> list[RawJob]:
        soup = BeautifulSoup(html, "html.parser")
        results = []

        # Primäre Selektoren (aktuelles Markup)
        articles = soup.select("article[data-job-id]")

        # Fallback: älteres / alternatives Markup
        if not articles:
            articles = soup.select("article[data-id]")
        if not articles:
            articles = soup.select("[data-at='job-item']")
        if not articles:
            # Letzter Fallback: alle <article>-Tags
            articles = soup.select("article")

        for article in articles:
            try:
                job_id = (
                    article.get("data-job-id")
                    or article.get("data-id")
                    or ""
                )

                # Titel: mehrere Selector-Varianten
                title_el = (
                    article.select_one("[data-at='job-item-title']")
                    or article.select_one("h2")
                    or article.select_one("h3")
                    or article.select_one("[class*='title' i]")
                )

                # Firma
                company_el = (
                    article.select_one("[data-at='job-item-company-name']")
                    or article.select_one("[class*='company' i]")
                    or article.select_one("[class*='employer' i]")
                )

                # Ort
                location_el = (
                    article.select_one("[data-at='job-item-location']")
                    or article.select_one("[class*='location' i]")
                    or article.select_one("[class*='city' i]")
                )

                # Link
                link_el = (
                    article.select_one("a[href*='/stellenangebote/']")
                    or article.select_one("a[href*='/job/']")
                    or article.select_one("a")
                )

                title = title_el.get_text(strip=True) if title_el else ""
                company = company_el.get_text(strip=True) if company_el else ""
                city = location_el.get_text(strip=True) if location_el else None
                href = link_el.get("href", "") if link_el else ""
                url = (
                    href if href.startswith("http")
                    else f"https://www.stepstone.de{href}"
                ) if href else None

                if not title:
                    continue

                results.append(RawJob(
                    title=title,
                    company=company,
                    city=city,
                    url=url,
                    source_portal="stepstone",
                    external_id=str(job_id) if job_id else None,
                    job_type=self._detect_type(title),
                ))
            except Exception as e:
                log.debug("StepStoneSource: Fehler beim Parsen eines Artikels: %s", e)
                continue

        return results

    def _detect_type(self, title: str) -> str | None:
        tl = title.lower()
        if any(w in tl for w in ["ausbildung", "azubi", "auszubildend"]):
            return "ausbildung"
        if any(w in tl for w in ["teilzeit", "part-time", "minijob"]):
            return "teilzeit"
        return "vollzeit"
