"""Erfolgs-Timeline pro Bewerbung + Vergleich mit Durchschnittswerten (#83, G.3.3).

Der reine Zeitstrahl (Status-Verlauf einer einzelnen Bewerbung) existierte
bereits (GET /api/applications/{id}/timeline, ApplicationStatusLog) und
wurde im Kanban-Detail-Modal angezeigt. Was fehlte, war der im Issue
explizit gewuenschte "Vergleich mit Durchschnittswerten": wie lange
verbringen Bewerbungen im Schnitt in einem bestimmten Status, verglichen
mit dieser einen Bewerbung hier?

Berechnung: ApplicationStatusLog speichert nur Zeitpunkte von
Statuswechseln, keine Dauer. Die Verweildauer in einem Status wird daher
aus der Differenz zweier aufeinanderfolgender Log-Eintraege derselben
Bewerbung abgeleitet (bzw. bis "jetzt", wenn es der letzte/aktuelle
Status ist) - ueber ALLE Bewerbungen aggregiert und pro Status
gemittelt.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.application_status_log import ApplicationStatusLog


async def get_avg_days_by_status(db: AsyncSession) -> dict[str, float]:
    """Durchschnittliche Verweildauer (in Tagen) je Status, ueber alle
    Bewerbungen hinweg. Bewerbungen, die aktuell noch in einem Status
    stehen, zaehlen mit der bisherigen Dauer bis jetzt mit rein - so
    fliessen auch offene, noch laufende Bewerbungen in den Schnitt ein,
    nicht nur abgeschlossene."""
    result = await db.execute(
        select(ApplicationStatusLog).order_by(
            ApplicationStatusLog.application_id, ApplicationStatusLog.changed_at,
        )
    )
    entries = result.scalars().all()

    logs_by_app: dict[int, list[ApplicationStatusLog]] = {}
    for entry in entries:
        logs_by_app.setdefault(entry.application_id, []).append(entry)

    now = datetime.now(timezone.utc)
    durations_by_status: dict[str, list[float]] = {}
    for app_entries in logs_by_app.values():
        for i, entry in enumerate(app_entries):
            # SQLite (Testumgebung) liefert DateTime(timezone=True)-Spalten
            # als naive datetime zurueck, Postgres (Produktion) als aware -
            # gleiches Muster wie zuvor in ghost_job_detector.py.
            start = entry.changed_at
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            if i + 1 < len(app_entries):
                end = app_entries[i + 1].changed_at
                if end.tzinfo is None:
                    end = end.replace(tzinfo=timezone.utc)
            else:
                end = now
            days = (end - start).total_seconds() / 86400
            durations_by_status.setdefault(entry.status, []).append(max(days, 0.0))

    return {
        status: round(sum(days_list) / len(days_list), 1)
        for status, days_list in durations_by_status.items()
    }
