from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.core.database import get_db
from backend.models.user_profile import UserProfile
from backend.schemas.profile import ProfileRead, ProfileUpdate

router = APIRouter(prefix="/api/profile", tags=["Profil"])


async def get_or_create_profile(db: AsyncSession) -> UserProfile:
    result = await db.execute(select(UserProfile).where(UserProfile.id == 1))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = UserProfile(id=1)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile


@router.get("/", response_model=ProfileRead)
async def get_profile(db: AsyncSession = Depends(get_db)):
    return await get_or_create_profile(db)


@router.patch("/", response_model=ProfileRead)
async def update_profile(data: ProfileUpdate, db: AsyncSession = Depends(get_db)):
    p = await get_or_create_profile(db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(p, field, value)
    await db.commit()
    await db.refresh(p)
    return p
