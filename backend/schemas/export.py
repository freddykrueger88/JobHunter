from pydantic import BaseModel


class ImportStats(BaseModel):
    jobs: int
    applications: int
    reminders: int
    history: int


class ImportResult(BaseModel):
    imported: ImportStats
    source_version: str
