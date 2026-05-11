"""StepStone-Scraper via httpx + BeautifulSoup.
Nur für den persönlichen Gebrauch. robots.txt wird respektiert.
"""
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from backend.services.job_search.base import BaseJobSource, RawJob

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
            "of": 0,  # Offset
        }
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=20) as client:
                r = await client.get(BASE_URL, params=params, headers=HEADERS)
                r.raise_for_status()
                html = r.text
        except Exception:
            return []

        return self._parse(html)

    def _parse(self, html: str) -> list[RawJob]:
        soup = BeautifulSoup(html, "html.parser")
        results = []

        # StepStone rendert Job-Cards als <article> mit data-job-id
        for article in soup.select("article[data-job-id]"):
            try:
                job_id = article.get("data-job-id", "")
                title_el = article.select_one("[data-at='job-item-title']")
                company_el = article.select_one("[data-at='job-item-company-name']")
                location_el = article.select_one("[data-at='job-item-location']")
                link_el = article.select_one("a[href*='/stellenangebote/']") or article.select_one("a")

                title = title_el.get_text(strip=True) if title_el else ""
                company = company_el.get_text(strip=True) if company_el else ""
                city = location_el.get_text(strip=True) if location_el else None
                url = f"https://www.stepstone.de{link_el['href']}" if link_el and link_el.get("href") else None

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
            except Exception:
                continue

        return results

    def _detect_type(self, title: str) -> str | None:
        tl = title.lower()
        if any(w in tl for w in ["ausbildung", "azubi", "auszubildend"]):
            return "ausbildung"
        if any(w in tl for w in ["teilzeit", "part-time", "minijob"]):
            return "teilzeit"
        return "vollzeit"
