"""Abstrakte Basisklasse für alle Job-Portal-Adapter.

safe_get/safe_post (I.3, "generisches Connector-Framework"): der
try/except-Block fuer Timeout/HTTP-Fehler/sonstige Exceptions mit
einheitlichem Logging war Zeile fuer Zeile identisch in 7 der 9
bestehenden Quellen dupliziert (arbeitsagentur/arbetsformedlingen/
eures_scraper/france_travail/karriere_nrw/service_bund/stepstone) - hier
einmal extrahiert, die beiden aelteren Quellen ohne dieses Muster
(adzuna/linkedin) beim Refactor mit angeglichen. Zwei duenne Wrapper
statt einer generischen client.request(method, ...)-Variante, damit die
bestehenden Tests (die client.get/client.post direkt mocken) unveraendert
funktionieren."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
import logging

import httpx

log = logging.getLogger(__name__)


@dataclass
class RawJob:
    """Normalisiertes Stellenangebot aus einem beliebigen Portal."""
    title: str
    company: str
    city: str | None = None
    postal_code: str | None = None
    address: str | None = None
    contact_person: str | None = None
    description: str | None = None
    url: str | None = None
    job_type: str | None = None  # vollzeit, teilzeit, ausbildung
    source_portal: str = ""
    external_id: str | None = None
    published_at: datetime | None = None
    latitude: float | None = None
    longitude: float | None = None


class BaseJobSource(ABC):
    @abstractmethod
    async def search(self, keywords: str, location: str, radius_km: int = 25) -> list[RawJob]:
        """Sucht Stellen und gibt normalisierte RawJob-Objekte zurück."""
        ...


async def _safe_call(coro, source_name: str) -> httpx.Response | None:
    try:
        r = await coro
        r.raise_for_status()
        return r
    except httpx.TimeoutException:
        log.error("%s: Timeout", source_name)
        return None
    except httpx.HTTPStatusError as e:
        log.error("%s: HTTP %s", source_name, e.response.status_code)
        return None
    except Exception as e:
        log.exception("%s: Unerwarteter Fehler: %s", source_name, e)
        return None


async def safe_get(client: httpx.AsyncClient, url: str, source_name: str, **kwargs) -> httpx.Response | None:
    """GET mit einheitlicher Fehlerbehandlung/Logging, None bei jedem
    Fehlschlag statt einer Exception - der Aufrufer prüft nur noch
    `if r is None: return []`."""
    return await _safe_call(client.get(url, **kwargs), source_name)


async def safe_post(client: httpx.AsyncClient, url: str, source_name: str, **kwargs) -> httpx.Response | None:
    """POST-Variante von safe_get, gleiche Semantik."""
    return await _safe_call(client.post(url, **kwargs), source_name)
