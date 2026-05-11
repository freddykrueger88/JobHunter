"""CRUD-Router fuer die Firmen-Blocklist."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from pydantic import BaseModel
from typing import Optional
from backend.database import get_db
from backend.models import Blocklist

router = APIRouter(prefix='/api/blocklist', tags=['blocklist'])

class BlocklistCreate(BaseModel):
    firma: Optional[str] = None
    recruiter_name: Optional[str] = None
    grund: Optional[str] = None


@router.get('/')
async def list_blocklist(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Blocklist).order_by(Blocklist.erstellt_am.desc()))
    return result.scalars().all()


@router.post('/', status_code=201)
async def add_to_blocklist(data: BlocklistCreate, db: AsyncSession = Depends(get_db)):
    entry = Blocklist(**data.model_dump())
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.delete('/{entry_id}', status_code=204)
async def remove_from_blocklist(entry_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Blocklist).where(Blocklist.id == entry_id))
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(404, 'Eintrag nicht gefunden')
    await db.delete(entry)
    await db.commit()


async def is_blocked(firma: str, db: AsyncSession) -> bool:
    """Hilfsfunktion: prueft ob eine Firma blockiert ist."""
    if not firma:
        return False
    result = await db.execute(
        select(Blocklist).where(
            Blocklist.firma.ilike(f'%{firma}%')
        )
    )
    return result.scalar_one_or_none() is not None
