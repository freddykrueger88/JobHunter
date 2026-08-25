"""Wiederverwendbare Textbausteine (vormals faelschlich CoverLetterTemplate genannt -
Namenskollision mit dem echten DOCX-Vorlagen-Feature aus PR #91/Issue #89 aufgeloest,
siehe docs/analysis/BACKLOG.md Phase F.2)."""
from sqlalchemy import String, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from backend.core.database import Base


class TextSnippet(Base):
    __tablename__ = "text_snippets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, default="allgemein")
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False)
    sprache: Mapped[str] = mapped_column(String, default="de")
    erstellt_am: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
