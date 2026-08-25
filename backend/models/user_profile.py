"""KI-Hintergrundprofil des Nutzers (Phase H) - fliesst in den
Anschreiben-Prompt ein, damit die KI mehr als nur den CV-Auszug kennt.
Ueberschneidet sich bewusst mit dem geplanten Firmenkultur-Matching
(#75/G.3.10) ueber arbeitsstil/werte, siehe docs/analysis/BACKLOG.md."""
from sqlalchemy import Text, String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from backend.core.database import Base


class UserProfile(Base):
    __tablename__ = "user_profile"

    id: Mapped[int] = mapped_column(primary_key=True)
    ueber_mich: Mapped[str | None] = mapped_column(Text, nullable=True)
    kernkompetenzen: Mapped[str | None] = mapped_column(Text, nullable=True)
    wunschrolle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    erfahrungsjahre: Mapped[int | None] = mapped_column(Integer, nullable=True)
    soft_skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    # startup, mittelstand, konzern, behoerde, egal
    arbeitsstil: Mapped[str | None] = mapped_column(String(20), nullable=True)
    werte: Mapped[str | None] = mapped_column(Text, nullable=True)
