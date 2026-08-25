from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from backend.core.database import Base


class UserBadge(Base):
    __tablename__ = "user_badges"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    badge_key: Mapped[str] = mapped_column(String, unique=True)
    freigeschaltet_am: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
