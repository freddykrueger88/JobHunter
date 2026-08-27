from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.core.database import get_db
from backend.models import UserBadge
from backend.services.badges import all_badges_with_status, check_and_award

router = APIRouter(prefix="/api/badges", tags=["Abzeichen"])


@router.get("/")
async def list_badges(db: AsyncSession = Depends(get_db)):
    """Prueft auf neu erreichte Abzeichen und liefert alle mit Status."""
    await check_and_award(db)
    result = await db.execute(select(UserBadge.badge_key))
    unlocked = {row[0] for row in result.all()}
    return all_badges_with_status(unlocked)
