"""FastAPI-Router fuer das Wiedervorlagen-System (Issue #64).

Endpunkte::

    GET    /api/followups/              - alle offenen Wiedervorlagen (mit Ampel)
    GET    /api/followups/stats         - Dashboard-Zaehler
    GET    /api/followups/{id}/vorlage  - Nachfass-E-Mail-Vorlage als Text
    POST   /api/followups/              - neue Wiedervorlage anlegen
    PATCH  /api/followups/{id}/erledigt - als erledigt markieren
    PATCH  /api/followups/{id}          - Datum/Notiz aendern
    DELETE /api/followups/{id}          - loeschen
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.database import get_db
from backend.models import Application, FollowUp
from backend.services.followup_scheduler import (
    AmpelStatus,
    _UNSET,
    aktualisiere_followup,
    berechne_ampel,
    berechne_dashboard_stats,
    erstelle_followup,
    generiere_nachfass_vorlage,
    hole_alle_offenen_followups,
    loesche_followup,
    markiere_erledigt,
    tage_bis_faellig,
)

router = APIRouter(prefix="/api/followups", tags=["followups"])


# ---------------------------------------------------------------------------
# Pydantic-Schemas
# ---------------------------------------------------------------------------

class FollowUpCreate(BaseModel):
    application_id: int
    tage: int = Field(..., ge=1, le=365, description="In wie vielen Tagen soll nachgefasst werden")
    notiz: Optional[str] = None


class FollowUpUpdate(BaseModel):
    tage: Optional[int] = Field(None, ge=1, le=365)
    notiz: Optional[str] = None  # explizit None = Notiz loeschen

    @model_validator(mode="after")
    def mindestens_ein_feld(self) -> "FollowUpUpdate":
        """Verhindert leere PATCH-Requests ohne Aenderung."""
        if self.tage is None and self.notiz is None:
            raise ValueError("Mindestens 'tage' oder 'notiz' muss angegeben werden.")
        return self


class FollowUpResponse(BaseModel):
    id: int
    application_id: int
    faellig_am: datetime
    notiz: Optional[str]
    erledigt: bool
    erledigt_am: Optional[datetime]
    erstellt_am: datetime
    # Berechnete Felder
    ampel: AmpelStatus
    tage_bis_faellig: int
    # Bewerbungs-Kontext (aus JOIN)
    firma: Optional[str] = None
    stelle: Optional[str] = None

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    urgent: int
    soon: int
    later: int
    done: int
    gesamt_offen: int


# ---------------------------------------------------------------------------
# Hilfsfunktion: FollowUp -> Response anreichern
# ---------------------------------------------------------------------------

def _enrich(fw: FollowUp) -> FollowUpResponse:
    """Baut eine FollowUpResponse mit berechneten Feldern auf."""
    firma: Optional[str] = None
    stelle: Optional[str] = None
    if fw.application and fw.application.job:
        firma = fw.application.job.firma
        stelle = fw.application.job.titel
    return FollowUpResponse(
        id=fw.id,
        application_id=fw.application_id,
        faellig_am=fw.faellig_am,
        notiz=fw.notiz,
        erledigt=fw.erledigt,
        erledigt_am=fw.erledigt_am,
        erstellt_am=fw.erstellt_am,
        ampel=berechne_ampel(fw),
        tage_bis_faellig=tage_bis_faellig(fw),
        firma=firma,
        stelle=stelle,
    )


# ---------------------------------------------------------------------------
# Endpunkte
# ---------------------------------------------------------------------------

@router.get("/stats", response_model=DashboardStats)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Ampel-Statistik fuer das Dashboard-Widget."""
    return await berechne_dashboard_stats(db)


@router.get("/", response_model=list[FollowUpResponse])
async def list_followups(db: AsyncSession = Depends(get_db)):
    """Alle offenen Wiedervorlagen, sortiert nach Faelligkeit."""
    followups = await hole_alle_offenen_followups(db)
    return [_enrich(fw) for fw in followups]


@router.post("/", response_model=FollowUpResponse, status_code=201)
async def create_followup(
    data: FollowUpCreate,
    db: AsyncSession = Depends(get_db),
):
    """Neue Wiedervorlage anlegen."""
    fw = await erstelle_followup(
        db,
        application_id=data.application_id,
        tage=data.tage,
        notiz=data.notiz,
    )
    return _enrich(fw)


@router.patch("/{followup_id}/erledigt", response_model=FollowUpResponse)
async def mark_done(
    followup_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Wiedervorlage als erledigt markieren."""
    fw = await markiere_erledigt(db, followup_id)
    if not fw:
        raise HTTPException(404, "Wiedervorlage nicht gefunden")
    return _enrich(fw)


@router.patch("/{followup_id}", response_model=FollowUpResponse)
async def update_followup(
    followup_id: int,
    data: FollowUpUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Faelligkeit und/oder Notiz einer Wiedervorlage aendern.

    Notiz auf null setzen loescht die Notiz explizit.
    Leerer Request-Body ohne 'tage' und 'notiz' wird mit 422 abgelehnt.
    """
    # Sentinel-Weiterleitung: nur uebergeben was wirklich im Body stand
    notiz_value = data.notiz if data.notiz is not None else (
        None if "notiz" in data.model_fields_set else _UNSET
    )
    fw = await aktualisiere_followup(
        db,
        followup_id=followup_id,
        tage=data.tage,
        notiz=notiz_value,
    )
    if not fw:
        raise HTTPException(404, "Wiedervorlage nicht gefunden")
    return _enrich(fw)


@router.delete("/{followup_id}", status_code=204)
async def delete_followup(
    followup_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Wiedervorlage loeschen."""
    deleted = await loesche_followup(db, followup_id)
    if not deleted:
        raise HTTPException(404, "Wiedervorlage nicht gefunden")


@router.get("/{followup_id}/vorlage")
async def get_vorlage(
    followup_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Gibt die Nachfass-E-Mail-Vorlage als reinen Text zurueck."""
    result = await db.execute(
        select(FollowUp)
        .where(FollowUp.id == followup_id)
        .options(selectinload(FollowUp.application).selectinload(Application.job))
    )
    fw = result.scalar_one_or_none()
    if not fw:
        raise HTTPException(404, "Wiedervorlage nicht gefunden")

    firma = fw.application.job.firma if fw.application and fw.application.job else "Ihrer Firma"
    stelle = fw.application.job.titel if fw.application and fw.application.job else "der ausgeschriebenen Stelle"

    return {"vorlage": generiere_nachfass_vorlage(stelle=stelle, firma=firma)}
