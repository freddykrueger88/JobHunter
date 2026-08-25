from sqlalchemy import String, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from backend.core.database import Base


class BackupLog(Base):
    __tablename__ = "backup_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    dateiname: Mapped[str | None] = mapped_column(String, nullable=True)
    groesse_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    erstellt_am: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    erfolgreich: Mapped[bool] = mapped_column(Boolean, default=True)
