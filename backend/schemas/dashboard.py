from datetime import datetime
from pydantic import BaseModel
from backend.schemas.history import HistoryEntryRead


class DueReminder(BaseModel):
    id: int
    message: str | None
    remind_at: datetime
    application_id: int | None


class DashboardStats(BaseModel):
    counts: dict[str, int]
    total: int
    recent_activity: list[HistoryEntryRead]
    due_reminders: list[DueReminder]
