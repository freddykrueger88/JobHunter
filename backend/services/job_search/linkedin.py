"""LinkedIn Job Search API.
Dokumentation: https://learn.microsoft.com/en-us/linkedin/shared/integrations/jobs/
API-Key (LinkedIn App OAuth2) in den Einstellungen hinterlegen.
"""
import httpx
from datetime import datetime, timezone
from backend.services.job_search.base import BaseJobSource, RawJob, safe_get

BASE_URL = "https://api.linkedin.com/v2/jobSearch"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"


class LinkedInSource(BaseJobSource):
    def __init__(self, api_key: str):
        # api_key = LinkedIn OAuth2 Access Token (aus App-Einstellungen)
        self.api_key = api_key

    async def search(self, keywords: str, location: str, radius_km: int = 25) -> list[RawJob]:
        if not self.api_key:
            return []
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        params = {
            "keywords": keywords,
            "location": location,
            "distance": radius_km,
            "count": 25,
            "start": 0,
        }
        async with httpx.AsyncClient(timeout=15) as client:
            r = await safe_get(client, BASE_URL, "LinkedInSource", headers=headers, params=params)
        if r is None:
            return []
        data = r.json()

        results = []
        for item in data.get("elements", []):
            posting = item.get("jobPosting", {})
            loc = posting.get("formattedLocation", "")
            results.append(RawJob(
                title=posting.get("title", ""),
                company=self._extract_company(posting),
                city=loc or None,
                url=posting.get("applyMethod", {}).get("com.linkedin.voyager.jobs.OffsiteApply", {}).get("companyApplyUrl")
                    or f"https://www.linkedin.com/jobs/view/{posting.get('id', '')}",
                description=posting.get("description", {}).get("text"),
                job_type=self._map_type(posting.get("workplaceTypes", [])),
                source_portal="linkedin",
                external_id=str(posting.get("id", "")),
                published_at=self._parse_ts(posting.get("listedAt")),
            ))
        return results

    def _extract_company(self, posting: dict) -> str:
        try:
            return posting["companyDetails"]["com.linkedin.voyager.jobs.JobPostingCompany"]["companyResolutionResult"]["name"]
        except (KeyError, TypeError):
            return posting.get("companyName", "")

    def _map_type(self, types: list) -> str | None:
        tl = [t.lower() for t in types]
        if any("part" in t for t in tl): return "teilzeit"
        if any("full" in t for t in tl): return "vollzeit"
        return None

    def _parse_ts(self, ts: int | None) -> datetime | None:
        if not ts: return None
        try: return datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        except: return None
