from datetime import datetime
from typing import Any
from pydantic import BaseModel


class CVUploadResponse(BaseModel):
    id: int
    filename: str
    status: str


class CVListItem(BaseModel):
    id: int
    filename: str
    full_name: str | None
    email: str | None
    skills: Any
    uploaded_at: datetime
    parsed: bool
    model_config = {"from_attributes": True}


class CVDetail(BaseModel):
    id: int
    filename: str
    full_name: str | None
    email: str | None
    phone: str | None
    address: str | None
    skills: Any
    work_experience: Any
    education: Any
    uploaded_at: datetime
    model_config = {"from_attributes": True}
