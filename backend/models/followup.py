from sqlalchemy import DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from backend.core.database import Base


class FollowUp(Base):
    __tablename__ = "followups"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    faellig_am: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    notiz: Mapped[str | None] = mapped_column(Text, nullable=True)
    erledigt: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    erledigt_am: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    erstellt_am: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    aktualisiert_am: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    application: Mapped["Application"] = relationship(back_populates="followups")
