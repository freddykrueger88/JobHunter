from sqlalchemy import Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from backend.core.database import Base


class DiaryEntry(Base):
    """Bewerbungs-Tagebuch (#80, G.3.6) - freie Notizen, nicht an eine
    bestimmte Bewerbung gebunden (dafuer gibt es bereits Application.notes)."""
    __tablename__ = "diary_entries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
