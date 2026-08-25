"""Baut aus dem KI-Hintergrundprofil (Phase H) einen Textblock fuer den
Anschreiben-Prompt. Gemeinsam genutzt von routers/ai.py und
routers/cover_letter_templates.py, damit beide Anschreiben-Generierungs-
Pfade dasselbe Profil beruecksichtigen."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.user_profile import UserProfile


async def build_profile_summary(db: AsyncSession) -> str | None:
    result = await db.execute(select(UserProfile).where(UserProfile.id == 1))
    profile = result.scalar_one_or_none()
    if not profile:
        return None

    parts = []
    if profile.wunschrolle:
        parts.append(f"Wunschrolle: {profile.wunschrolle}")
    if profile.erfahrungsjahre is not None:
        parts.append(f"Berufserfahrung: {profile.erfahrungsjahre} Jahre")
    if profile.kernkompetenzen:
        parts.append(f"Kernkompetenzen: {profile.kernkompetenzen}")
    if profile.soft_skills:
        parts.append(f"Staerken: {profile.soft_skills}")
    if profile.werte:
        parts.append(f"Wichtig im Job: {profile.werte}")
    if profile.ueber_mich:
        parts.append(f"Ueber mich: {profile.ueber_mich}")

    if not parts:
        return None
    return "Zusaetzliche Hintergrundinfos zum Bewerber:\n" + "\n".join(parts)
