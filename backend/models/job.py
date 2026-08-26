from sqlalchemy import String, Text, DateTime, Boolean, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from backend.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    company: Mapped[str] = mapped_column(String(255))
    contact_person: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_portal: Mapped[str | None] = mapped_column(String(50), nullable=True)  # arbeitsagentur, adzuna, linkedin etc.
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    job_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # vollzeit, teilzeit, ausbildung etc.
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)  # ausblenden wenn nicht passend
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    published_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Ergebnisse der KI-Stellenanalyse (backend/services/job_analyzer.py)
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    work_model: Mapped[str | None] = mapped_column(String(20), nullable=True)  # remote, hybrid, vor-ort, unbekannt
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON-codierte Liste
    # Ergebnis der KI-Skill-Gap-Analyse (backend/services/skill_gap.py)
    skill_gap_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    skill_gap_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    applications: Mapped[list["Application"]] = relationship(back_populates="job", cascade="all, delete-orphan")
