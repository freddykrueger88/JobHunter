"""Bundesagentur für Arbeit – Jobsuche API (kostenlos, kein Key nötig)."""
import httpx
from backend.services.job_search.base import BaseJobSource, RawJob
from datetime import datetime

BASE_URL = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs"
TOKEN_URL = "https://rest.arbeitsagentur.de/oauth/token"


class ArbeitsagenturSource(BaseJobSource):
    def __init__(self, client_id: str = "", client_secret: str = ""):
        # Ohne Keys: öffentlicher Zugriff mit eingeschränktem Rate-Limit
        self.client_id = client_id
        self.client_secret = client_secret

    async def _get_token(self) -> str | None:
        if not self.client_id:
            return None
        async with httpx.AsyncClient() as client:
            r = await client.post(TOKEN_URL, data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            })
            return r.json().get("access_token")

    async def search(self, keywords: str, location: str, radius_km: int = 25) -> list[RawJob]:
        token = await self._get_token()
        headers = {"User-Agent": "JobHunter/1.0"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        params = {
            "was": keywords,
            "wo": location,
            "umkreis": radius_km,
            "size": 25,
            "page": 1,
        }
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(BASE_URL, params=params, headers=headers, timeout=15)
                r.raise_for_status()
                data = r.json()
        except Exception:
            return []

        results = []
        for item in data.get("stellenangebote", []):
            arbeitgeber = item.get("arbeitgeber", {})
            arbeitsort = item.get("arbeitsort", {})
            results.append(RawJob(
                title=item.get("beruf", ""),
                company=arbeitgeber if isinstance(arbeitgeber, str) else arbeitgeber.get("name", ""),
                city=arbeitsort.get("ort"),
                postal_code=arbeitsort.get("plz"),
                address=arbeitsort.get("strasse"),
                description=item.get("stellenbeschreibung"),
                url=f"https://www.arbeitsagentur.de/jobsuche/jobdetail/{item.get('hashId', '')}",
                job_type=self._map_arbeitszeitmodell(item.get("arbeitszeitmodelle", [])),
                source_portal="arbeitsagentur",
                external_id=item.get("hashId"),
                published_at=self._parse_date(item.get("eintrittsdatum")),
                latitude=arbeitsort.get("koordinaten", {}).get("lat"),
                longitude=arbeitsort.get("koordinaten", {}).get("lon"),
            ))
        return results

    def _map_arbeitszeitmodell(self, models: list) -> str | None:
        m = [x.lower() for x in models]
        if any("ausbildung" in x for x in m): return "ausbildung"
        if any("vollzeit" in x for x in m): return "vollzeit"
        if any("teilzeit" in x for x in m): return "teilzeit"
        return None

    def _parse_date(self, s: str | None) -> datetime | None:
        if not s: return None
        try: return datetime.fromisoformat(s)
        except: return None
