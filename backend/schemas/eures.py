from pydantic import BaseModel


class EuresJob(BaseModel):
    external_id: str
    source: str
    title: str
    company: str
    location: str
    country: str
    url: str
    description: str
    posted_at: str | None = None


class EuresSearchResult(BaseModel):
    """Deckt sowohl den Erfolgs- als auch den Fehlerfall von
    services/job_search/eures_scraper.search_eures() ab: bei einem Fehler
    fehlen page/page_size, dafuer ist "error" gesetzt - beides muss ohne
    Validierungsfehler durchgereicht werden koennen."""

    results: list[EuresJob]
    total: int
    page: int | None = None
    page_size: int | None = None
    error: str | None = None
