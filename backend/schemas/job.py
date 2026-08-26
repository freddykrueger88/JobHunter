import json

from pydantic import BaseModel, field_validator
from datetime import datetime


class JobBase(BaseModel):
    title: str
    company: str
    contact_person: str | None = None
    address: str | None = None
    city: str | None = None
    postal_code: str | None = None
    description: str | None = None
    url: str | None = None
    source_portal: str | None = None
    job_type: str | None = None
    is_hidden: bool = False


class JobCreate(JobBase):
    pass


class JobRead(JobBase):
    id: int
    distance_km: float | None = None
    published_at: datetime | None = None
    created_at: datetime
    salary_min: int | None = None
    salary_max: int | None = None
    work_model: str | None = None
    tags: list[str] | None = None
    skill_gap_score: int | None = None

    model_config = {"from_attributes": True}

    @field_validator("tags", mode="before")
    @classmethod
    def _parse_tags(cls, value):
        """tags liegt in der DB als JSON-codierter String vor (Text-Spalte)."""
        if value is None or isinstance(value, list):
            return value
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return None
