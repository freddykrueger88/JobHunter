"""Abstrakte Basisklasse für alle Job-Portal-Adapter."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


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
