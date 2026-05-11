"""Automatisches lokales Backup mit 7-Tage-Rotation."""
import json
import os
import gzip
from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models import (
    Job, Application, Reminder, SearchProfile,
    UserSettings, CoverLetterTemplate, BackupLog
)

MAX_BACKUPS = 7

async def create_backup(db: AsyncSession, backup_path: str = './backups') -> str:
    """Erstellt ein komprimiertes JSON-Backup aller Tabellen."""
    Path(backup_path).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'jobhunter_backup_{timestamp}.json.gz'
    filepath = Path(backup_path) / filename

    # Alle Daten sammeln
    data = {}
    for model, key in [
        (Job, 'jobs'), (Application, 'applications'),
        (Reminder, 'reminders'), (SearchProfile, 'search_profiles'),
    ]:
        result = await db.execute(select(model))
        rows = result.scalars().all()
        data[key] = [
            {c.name: getattr(row, c.name) for c in model.__table__.columns
             if not c.name.endswith('_enc')}
            for row in rows
        ]

    # Datumsfelder serialisieren
    def default(obj):
        if isinstance(obj, datetime): return obj.isoformat()
        raise TypeError()

    json_bytes = json.dumps(data, default=default, ensure_ascii=False).encode('utf-8')
    with gzip.open(filepath, 'wb') as f:
        f.write(json_bytes)

    size = filepath.stat().st_size

    # Backup-Log speichern
    log = BackupLog(dateiname=filename, groesse_bytes=size, erfolgreich=True)
    db.add(log)
    await db.commit()

    # Rotation: nur MAX_BACKUPS behalten
    await rotate_backups(backup_path, db)

    return str(filepath)

async def rotate_backups(backup_path: str, db: AsyncSession):
    """Loescht aelteste Backups wenn mehr als MAX_BACKUPS vorhanden."""
    result = await db.execute(
        select(BackupLog).order_by(BackupLog.erstellt_am.desc())
    )
    logs = result.scalars().all()

    if len(logs) > MAX_BACKUPS:
        to_delete = logs[MAX_BACKUPS:]
        for log in to_delete:
            path = Path(backup_path) / log.dateiname
            if path.exists():
                path.unlink()
            await db.delete(log)
        await db.commit()
