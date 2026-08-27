"""CRUD-Router fuer die Firmen-Blocklist (#84, G.3.2)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from backend.core.database import get_db
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


@router.post('/import')
async def import_blocklist(entries: list[BlocklistCreate], db: AsyncSession = Depends(get_db)):
    """Bulk-Import (#84) - z.B. eine zuvor exportierte Blocklist wieder
    einspielen. Ueberspringt Eintraege, deren firma bereits (case-
    insensitive, exakt) auf der Liste steht, statt Duplikate anzulegen."""
    existing = await db.execute(select(Blocklist.firma))
    existing_lower = {f.lower() for f in existing.scalars().all() if f}

    imported = 0
    skipped = 0
    for data in entries:
        if data.firma and data.firma.lower() in existing_lower:
            skipped += 1
            continue
        db.add(Blocklist(**data.model_dump()))
        if data.firma:
            existing_lower.add(data.firma.lower())
        imported += 1

    await db.commit()
    return {"imported": imported, "skipped": skipped}


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


async def get_blocked_company_terms(db: AsyncSession) -> list[str]:
    """Alle gesetzten firma-Werte der Blocklist auf einmal (fuer
    Substring-Abgleich gegen Job.company beim Listen/Speichern von
    Stellen) - vermeidet eine Einzelabfrage pro Job wie is_blocked()."""
    result = await db.execute(select(Blocklist.firma).where(Blocklist.firma.isnot(None)))
    return [f for f in result.scalars().all() if f]
