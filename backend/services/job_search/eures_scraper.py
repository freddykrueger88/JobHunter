"""#72 – EURES-Integration: EU-weite Stellensuche über die offizielle EURES REST API."""
import httpx
from typing import Any

EURES_BASE = "https://europa.eu/eures/eures-searchengine/page/jv-search/v2/search"

# Mapping: Sprache → EURES-Sprachcode
LANG_MAP = {"de": "de", "en": "en", "fr": "fr", "nl": "nl", "sv": "sv", "da": "da", "no": "no"}


async def search_eures(
    keywords: str,
    country_code: str = "DE",  # ISO-3166-1 Alpha-2
    lang: str = "de",
    page: int = 0,
    page_size: int = 20,
) -> dict[str, Any]:
    """Sucht Stellen in der EURES-Datenbank. Gibt normalisierte Job-Objekte zurück."""
    payload = {
        "keywords": keywords,
        "sortSearch": "BEST_MATCH",
        "pageNumber": page,
        "pageSize": page_size,
        "lang": LANG_MAP.get(lang, "de"),
        "dataSetRequest": {"dataSetCode": "EURES"},
    }
    if country_code and country_code != "EU":
        payload["positionLocation"] = [{"countryCode": country_code}]

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                EURES_BASE,
                json=payload,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Accept-Language": lang,
                },
            )
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        return {"error": str(e), "results": [], "total": 0}

    items = data.get("jobVacancies", []) or data.get("results", [])
    normalized = []
    for item in items:
        jv = item.get("jobVacancy", item)
        header = jv.get("header", {})
        employer = jv.get("hiringOrganization", {})
        location = (jv.get("jobLocation") or [{}])[0] if jv.get("jobLocation") else {}
        normalized.append({
            "external_id": f"eures_{jv.get('id', '')}",
            "source": "EURES",
            "title": header.get("title") or jv.get("title", ""),
            "company": employer.get("name", ""),
            "location": location.get("address", {}).get("addressLocality", ""),
            "country": location.get("address", {}).get("addressCountry", country_code),
            "url": jv.get("uri") or f"https://eures.ec.europa.eu/eures-jobs_{jv.get('id', '')}",
            "description": jv.get("description", "")[:2000],
            "posted_at": jv.get("publicationStartDate"),
        })

    return {
        "results": normalized,
        "total": data.get("totalCount", len(normalized)),
        "page": page,
        "page_size": page_size,
    }
