from pydantic import BaseModel
from datetime import datetime

APPLICATION_STATUSES = [
    "interessant",
    "beworben",
    "interview",
    "angenommen",
    "absage",
    "archiviert",
]


class ApplicationBase(BaseModel):
    job_id: int
    status: str = "interessant"
    notes: str | None = None
    applied_at: datetime | None = None
    interview_at: datetime | None = None
    kanban_position: int = 0


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None
    applied_at: datetime | None = None
    interview_at: datetime | None = None
    kanban_position: int | None = None


class ApplicationRead(ApplicationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
