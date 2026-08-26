from datetime import datetime

from pydantic import BaseModel


class ApplicationJobInfo(BaseModel):
    title: str
    company: str
    city: str | None = None


class ApplicationBase(BaseModel):
    id: int
    job_id: int
    status: str
    notes: str | None
    applied_at: datetime | None
    interview_at: datetime | None
    kanban_position: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ApplicationRead(ApplicationBase):
    """Wie ApplicationBase, aber mit eingebetteten Job-Kerninfos (list/get) -
    create/update geben die reine ORM-Instanz zurueck, ohne die job-Relation
    zu laden, deshalb dort ApplicationBase statt ApplicationRead."""
    job: ApplicationJobInfo | None = None
