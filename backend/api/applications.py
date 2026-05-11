from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.core.database import get_db
from backend.models.application import Application
from backend.models.history import HistoryEntry
from backend.schemas.application import ApplicationCreate, ApplicationRead, ApplicationUpdate

router = APIRouter(prefix="/applications", tags=["Bewerbungen"])


@router.get("/", response_model=list[ApplicationRead])
async def list_applications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application).order_by(Application.kanban_position))
    return result.scalars().all()


@router.get("/{app_id}", response_model=ApplicationRead)
async def get_application(app_id: int, db: AsyncSession = Depends(get_db)):
    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Bewerbung nicht gefunden")
    return app


@router.post("/", response_model=ApplicationRead, status_code=201)
async def create_application(data: ApplicationCreate, db: AsyncSession = Depends(get_db)):
    application = Application(**data.model_dump())
    db.add(application)
    await db.commit()
    await db.refresh(application)
    db.add(HistoryEntry(
        event_type="application_created",
        description=f"Bewerbung für Stelle ID {application.job_id} erstellt",
        meta={"job_id": application.job_id, "status": application.status},
    ))
    await db.commit()
    return application


@router.patch("/{app_id}", response_model=ApplicationRead)
async def update_application(app_id: int, data: ApplicationUpdate, db: AsyncSession = Depends(get_db)):
    application = await db.get(Application, app_id)
    if not application:
        raise HTTPException(status_code=404, detail="Bewerbung nicht gefunden")
    old_status = application.status
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(application, field, value)
    await db.commit()
    await db.refresh(application)
    if data.status and data.status != old_status:
        db.add(HistoryEntry(
            event_type="status_changed",
            description=f"Bewerbung {app_id}: Status geändert",
            meta={"old": old_status, "new": data.status},
        ))
        await db.commit()
    return application


@router.delete("/{app_id}", status_code=204)
async def delete_application(app_id: int, db: AsyncSession = Depends(get_db)):
    application = await db.get(Application, app_id)
    if not application:
        raise HTTPException(status_code=404, detail="Bewerbung nicht gefunden")
    await db.delete(application)
    await db.commit()
