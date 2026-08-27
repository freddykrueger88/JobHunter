"""CRUD-Router fuer das Bewerbungs-Tagebuch (#80, G.3.6)."""
from __future__ import annotations

import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.models import DiaryEntry

router = APIRouter(prefix="/api/diary", tags=["Tagebuch"])


class DiaryEntryCreate(BaseModel):
    content: str


class DiaryEntryUpdate(BaseModel):
    content: str


@router.get("/")
async def list_entries(search: str | None = None, db: AsyncSession = Depends(get_db)):
    # id als Tiebreaker: created_at kann bei schnell aufeinanderfolgenden
    # Eintraegen (oder auf SQLite in Tests) denselben Zeitstempel tragen -
    # id ist immer streng monoton, garantiert stabile "neueste zuerst"-Reihenfolge.
    q = select(DiaryEntry).order_by(DiaryEntry.created_at.desc(), DiaryEntry.id.desc())
    if search:
        q = q.where(DiaryEntry.content.ilike(f"%{search}%"))
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/", status_code=201)
async def create_entry(data: DiaryEntryCreate, db: AsyncSession = Depends(get_db)):
    entry = DiaryEntry(content=data.content)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.patch("/{entry_id}")
async def update_entry(entry_id: int, data: DiaryEntryUpdate, db: AsyncSession = Depends(get_db)):
    entry = await db.get(DiaryEntry, entry_id)
    if not entry:
        raise HTTPException(404, "Eintrag nicht gefunden")
    entry.content = data.content
    await db.commit()
    await db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=204)
async def delete_entry(entry_id: int, db: AsyncSession = Depends(get_db)):
    entry = await db.get(DiaryEntry, entry_id)
    if not entry:
        raise HTTPException(404, "Eintrag nicht gefunden")
    await db.delete(entry)
    await db.commit()


@router.get("/pdf")
async def export_diary_pdf(search: str | None = None, db: AsyncSession = Depends(get_db)):
    """PDF-Export des Tagebuchs (#80, G.3.6) - respektiert denselben
    Suchfilter wie die Liste, damit ein gefiltertes Ergebnis auch
    gefiltert exportiert werden kann."""
    from backend.services.diary_pdf import generate_diary_pdf

    pdf_bytes = await generate_diary_pdf(db, search=search)
    filename = f"jobhunter_tagebuch_{datetime.now().strftime('%Y%m%d')}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
