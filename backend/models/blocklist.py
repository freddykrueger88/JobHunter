from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from backend.core.database import Base


class Blocklist(Base):
    __tablename__ = "blocklist"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    firma: Mapped[str | None] = mapped_column(String, nullable=True)
    recruiter_name: Mapped[str | None] = mapped_column(String, nullable=True)
    grund: Mapped[str | None] = mapped_column(Text, nullable=True)
    erstellt_am: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
