"""
Tests fuer backend/services/backup.py.

War fertig gebaut, aber nie in den Scheduler eingehaengt (kein Cron-Job
lief je) - jetzt taeglich um 3 Uhr ueber scheduler.py verdrahtet. Dabei
ergaenzt: UserSettings und TextSnippet wurden importiert, aber nie in
die Export-Schleife aufgenommen - "Backup aller Tabellen" (Docstring)
sicherte bisher nur 4 von 6 relevanten Tabellen.
"""
from __future__ import annotations

import gzip
import json

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.job import Job
from backend.models.backup_log import BackupLog
from backend.services.backup import create_backup

pytestmark = pytest.mark.asyncio


class TestCreateBackup:
    async def test_creates_gzip_json_with_jobs(self, db: AsyncSession, tmp_path):
        db.add(Job(title="Backend Engineer", company="Beispiel GmbH"))
        await db.commit()

        filepath = await create_backup(db, backup_path=str(tmp_path))

        with gzip.open(filepath, "rb") as f:
            data = json.loads(f.read())
        assert len(data["jobs"]) == 1
        assert data["jobs"][0]["title"] == "Backend Engineer"

    async def test_includes_settings_and_text_snippets(self, db: AsyncSession, tmp_path):
        """Regression: UserSettings/TextSnippet waren importiert, aber nie
        exportiert."""
        from backend.models.settings import UserSettings
        db.add(UserSettings(id=1))
        await db.commit()

        filepath = await create_backup(db, backup_path=str(tmp_path))

        with gzip.open(filepath, "rb") as f:
            data = json.loads(f.read())
        assert "settings" in data
        assert "text_snippets" in data

    async def test_excludes_encrypted_fields(self, db: AsyncSession, tmp_path):
        from backend.models.settings import UserSettings
        db.add(UserSettings(id=1, adzuna_api_key_enc="geheim"))
        await db.commit()

        filepath = await create_backup(db, backup_path=str(tmp_path))

        with gzip.open(filepath, "rb") as f:
            raw = f.read()
        assert b"geheim" not in raw

    async def test_logs_backup_and_rotates_old_ones(self, db: AsyncSession, tmp_path):
        from backend.services.backup import MAX_BACKUPS
        for _ in range(MAX_BACKUPS + 2):
            await create_backup(db, backup_path=str(tmp_path))

        logs = (await db.execute(select(BackupLog))).scalars().all()
        assert len(logs) == MAX_BACKUPS
