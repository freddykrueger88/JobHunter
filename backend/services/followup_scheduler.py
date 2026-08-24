"""Wiedervorlagen-Service fuer JobHunter (Issue #64).

Verantwortlich fuer:
- Ampel-Berechnung (urgent / soon / later / done)
- CRUD-Operationen auf der followups-Tabelle
- Dashboard-Zusammenfassung (Stats-Widget)
- Vorgefertigte Nachfass-E-Mail-Vorlage
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any, Literal, Optional

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models import Application, FollowUp

AmpelStatus = Literal["urgent", "soon", "later", "done"]

# Sentinel: unterscheidet "nicht uebergeben" von explizitem None
_UNSET: Any = object()


# ---------------------------------------------------------------------------
# Ampel-Logik
# ---------------------------------------------------------------------------

def berechne_ampel(followup: FollowUp) -> AmpelStatus:
    """Berechnet den Ampel-Status eines FollowUp-Eintrags.

    Returns:
        'done'   - bereits erledigt
        'urgent' - heute oder ueberfaellig  (diff <= 0)
        'soon'   - morgen faellig            (diff == 1)
        'later'  - ab uebermorgen (kein Limit nach oben)
    """
    if followup.erledigt:
        return "done"

    heute = date.today()
    faellig = followup.faellig_am.date() if isinstance(followup.faellig_am, datetime) else followup.faellig_am
    diff = (faellig - heute).days

    if diff <= 0:
        return "urgent"
    if diff == 1:
        return "soon"
    return "later"


def tage_bis_faellig(followup: FollowUp) -> int:
    """Gibt die Anzahl der Tage bis zur Faelligkeit zurueck (negativ = ueberfaellig)."""
    heute = date.today()
    faellig = followup.faellig_am.date() if isinstance(followup.faellig_am, datetime) else followup.faellig_am
    return (faellig - heute).days


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

async def erstelle_followup(
    db: AsyncSession,
    application_id: int,
    tage: int,
    notiz: Optional[str] = None,
) -> FollowUp:
    """Legt eine neue Wiedervorlage an.

    Args:
        db:             Async-DB-Session
        application_id: ID der verknuepften Bewerbung
        tage:           In wie vielen Tagen soll nachgefasst werden (1/3/7/14)
        notiz:          Optionaler Freitext

    Returns:
        Das persistierte FollowUp-Objekt
    """
    faellig_am = datetime.now(timezone.utc) + timedelta(days=tage)
    followup = FollowUp(
        application_id=application_id,
        faellig_am=faellig_am,
        notiz=notiz,
    )
    db.add(followup)
    await db.commit()
    await db.refresh(followup)
    return followup


async def hole_followups_fuer_bewerbung(
    db: AsyncSession,
    application_id: int,
    nur_offene: bool = False,
) -> list[FollowUp]:
    """Gibt alle Wiedervorlagen einer Bewerbung zurueck."""
    stmt = (
        select(FollowUp)
        .where(FollowUp.application_id == application_id)
        .order_by(FollowUp.faellig_am)
    )
    if nur_offene:
        stmt = stmt.where(FollowUp.erledigt.is_(False))
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def hole_alle_offenen_followups(
    db: AsyncSession,
) -> list[FollowUp]:
    """Gibt alle offenen Wiedervorlagen zurueck, sortiert nach Faelligkeit.

    Laedt die verknuepfte Application (inkl. Job) per selectinload,
    damit kein zusaetzlicher DB-Aufruf im Router noetig ist.
    """
    stmt = (
        select(FollowUp)
        .where(FollowUp.erledigt.is_(False))
        .options(selectinload(FollowUp.application).selectinload(Application.job))
        .order_by(FollowUp.faellig_am)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def markiere_erledigt(
    db: AsyncSession,
    followup_id: int,
) -> Optional[FollowUp]:
    """Markiert eine Wiedervorlage als erledigt.

    Returns:
        Das aktualisierte FollowUp-Objekt oder None wenn nicht gefunden.
    """
    result = await db.execute(select(FollowUp).where(FollowUp.id == followup_id))
    followup = result.scalar_one_or_none()
    if not followup:
        return None
    followup.erledigt = True
    followup.erledigt_am = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(followup)
    return followup


async def aktualisiere_followup(
    db: AsyncSession,
    followup_id: int,
    tage: Optional[int] = None,
    notiz: Any = _UNSET,
) -> Optional[FollowUp]:
    """Aktualisiert Faelligkeit und/oder Notiz einer Wiedervorlage.

    Args:
        tage:  Neues Faelligkeitsdatum als Offset ab heute (None = unveraendert)
        notiz: Neuer Notiztext. Explizit None uebergeben um die Notiz zu loeschen.
               Nicht uebergeben (_UNSET) bedeutet unveraendert.
    """
    result = await db.execute(select(FollowUp).where(FollowUp.id == followup_id))
    followup = result.scalar_one_or_none()
    if not followup:
        return None
    if tage is not None:
        followup.faellig_am = datetime.now(timezone.utc) + timedelta(days=tage)
    if notiz is not _UNSET:
        followup.notiz = notiz  # None loescht die Notiz, String setzt sie
    await db.commit()
    await db.refresh(followup)
    return followup


async def loesche_followup(db: AsyncSession, followup_id: int) -> bool:
    """Loescht eine Wiedervorlage. Gibt True zurueck wenn erfolgreich."""
    result = await db.execute(select(FollowUp).where(FollowUp.id == followup_id))
    followup = result.scalar_one_or_none()
    if not followup:
        return False
    await db.delete(followup)
    await db.commit()
    return True


# ---------------------------------------------------------------------------
# Dashboard-Stats  (einzelner SQL GROUP-BY-Query statt N+1)
# ---------------------------------------------------------------------------

async def berechne_dashboard_stats(db: AsyncSession) -> dict:
    """Berechnet die Ampel-Statistik fuer das Dashboard-Widget.

    Verwendet einen einzigen GROUP-BY-Query statt alle Objekte in Python
    zu laden. Skaliert damit auch bei vielen Eintraegen.

    Returns ein Dict mit den Zaehlen pro Ampel-Status sowie Gesamt.

    Beispiel::

        {
            'urgent': 2,
            'soon': 1,
            'later': 4,
            'done': 12,
            'gesamt_offen': 7,
        }
    """
    # In Python statt in SQL berechnet (nicht func.current_date() + 1): SQLite
    # behandelt "TEXT-Datum + 1" als schwach typisierte Arithmetik und liefert
    # keine gueltige Tages-Verschiebung (der "soon"-Bucket blieb dadurch immer
    # leer) - als gebundene Parameter funktioniert der Vergleich auf beiden
    # Dialekten korrekt. Gefunden bei Testfall test_stats_zaehlt_korrekt.
    today = date.today()
    tomorrow = today + timedelta(days=1)

    bucket = case(
        (FollowUp.erledigt.is_(True), "done"),
        (func.date(FollowUp.faellig_am) <= today, "urgent"),
        (func.date(FollowUp.faellig_am) == tomorrow, "soon"),
        else_="later",
    ).label("bucket")

    stmt = (
        select(bucket, func.count().label("n"))
        .select_from(FollowUp)
        .group_by("bucket")
    )
    rows = (await db.execute(stmt)).all()

    stats: dict[str, int] = {"urgent": 0, "soon": 0, "later": 0, "done": 0}
    for row in rows:
        if row.bucket in stats:
            stats[row.bucket] = row.n

    stats["gesamt_offen"] = stats["urgent"] + stats["soon"] + stats["later"]
    return stats


# ---------------------------------------------------------------------------
# E-Mail-Vorlage
# ---------------------------------------------------------------------------

def generiere_nachfass_vorlage(
    stelle: str,
    firma: str,
    anrede: str = "Sehr geehrte Damen und Herren",
) -> str:
    """Generiert eine Nachfass-E-Mail-Vorlage als reinen Text.

    Args:
        stelle:  Stellenbezeichnung (z.B. 'IT-Support Specialist')
        firma:   Firmenname (z.B. 'Dataport AoeR')
        anrede:  Optionale persoenliche Anrede

    Returns:
        Fertige E-Mail als String, kopierbereit.
    """
    return (
        f"{anrede},\n\n"
        f"meine Bewerbung fuer die Stelle als {stelle} bei {firma} "
        f"liegt Ihnen seit einigen Tagen vor. Ich moechte mein Interesse "
        f"bestaetigen und fragen, ob es zum aktuellen Stand der "
        f"Auswahlentscheidung bereits Neuigkeiten gibt.\n\n"
        f"Fuer Rueckfragen stehe ich Ihnen gerne zur Verfuegung.\n\n"
        f"Mit freundlichen Gruessen"
    )
