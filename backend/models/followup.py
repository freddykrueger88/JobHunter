"""Wiedervorlagen-Modell (Issue #64) – Nachfass-Erinnerungen für Bewerbungen."""
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from backend.core.database import Base


class FollowUp(Base):
    __tablename__ = "followups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    application_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    faellig_am: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), nullable=False)
    notiz: Mapped[str | None] = mapped_column(Text, nullable=True)
    erledigt: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    erledigt_am: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
    erstellt_am: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    aktualisiert_am: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    application: Mapped["Application"] = relationship(back_populates="followups")
