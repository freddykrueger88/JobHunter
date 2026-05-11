"""Adzuna API – aggregiert Indeed, Monster u.a. Kostenlos mit Registrierung.
   Registrierung: https://developer.adzuna.com/
"""
import httpx
from backend.services.job_search.base import BaseJobSource, RawJob
from datetime import datetime

BASE_URL = "https://api.adzuna.com/v1/api/jobs/de/search/1"


class AdzunaSource(BaseJobSource):
    def __init__(self, app_id: str, api_key: str):
        self.app_id = app_id
        self.api_key = api_key

    async def search(self, keywords: str, location: str, radius_km: int = 25) -> list[RawJob]:
        if not self.app_id or not self.api_key:
            return []
        params = {
            "app_id": self.app_id,
            "app_key": self.api_key,
            "what": keywords,
            "where": location,
            "distance": radius_km,
            "results_per_page": 20,
            "content-type": "application/json",
        }
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(BASE_URL, params=params, timeout=15)
                r.raise_for_status()
                data = r.json()
        except Exception:
            return []

        results = []
        for item in data.get("results", []):
            loc = item.get("location", {})
            results.append(RawJob(
                title=item.get("title", ""),
                company=item.get("company", {}).get("display_name", ""),
                city=loc.get("display_name"),
                description=item.get("description"),
                url=item.get("redirect_url"),
                job_type=self._map_type(item.get("contract_time", "")),
                source_portal="adzuna",
                external_id=str(item.get("id", "")),
                published_at=self._parse_date(item.get("created")),
                latitude=item.get("latitude"),
                longitude=item.get("longitude"),
            ))
        return results

    def _map_type(self, ct: str) -> str | None:
        if "full" in ct: return "vollzeit"
        if "part" in ct: return "teilzeit"
        return None

    def _parse_date(self, s: str | None) -> datetime | None:
        if not s: return None
        try: return datetime.fromisoformat(s.replace("Z", "+00:00"))
        except: return None
