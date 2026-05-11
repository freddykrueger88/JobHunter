from pydantic import BaseModel
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

    model_config = {"from_attributes": True}
