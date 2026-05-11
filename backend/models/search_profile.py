from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from backend.core.database import Base


class SearchProfile(Base):
    __tablename__ = "search_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # z.B. "IT-Support Bremen"
    keywords = Column(String, nullable=False)
    location = Column(String, nullable=False)
    radius_km = Column(Integer, default=25)
    schedule = Column(String, default="daily")  # "daily", "weekly" oder cron
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime(timezone=True), nullable=True)
    last_result_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
