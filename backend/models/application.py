from sqlalchemy import String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from backend.core.database import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    # Status: interessant, beworben, interview, angenommen, absage, archiviert
    status: Mapped[str] = mapped_column(String(50), default="interessant")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    applied_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    interview_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    kanban_position: Mapped[int] = mapped_column(Integer, default=0)  # Reihenfolge im Kanban
    # Zwischengespeicherter ATS-Score (backend/services/ats_scorer.py),
    # damit application_quality.py nicht bei jedem Checklisten-Aufruf neu
    # gegen den CV rechnen muss.
    ats_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    job: Mapped["Job"] = relationship(back_populates="applications")
    cover_letters: Mapped[list["CoverLetter"]] = relationship(back_populates="application", cascade="all, delete-orphan")
    reminders: Mapped[list["Reminder"]] = relationship(back_populates="application", cascade="all, delete-orphan")
    followups: Mapped[list["FollowUp"]] = relationship(back_populates="application", cascade="all, delete-orphan")
