from datetime import datetime
from typing import Any
from pydantic import BaseModel


class HistoryEntryRead(BaseModel):
    id: int
    type: str
    description: str
    meta: Any
    at: datetime
