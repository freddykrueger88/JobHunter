"""
Tests fuer backend/api/cv.py (Rework-Plan Phase E.2, Testpyramide).

Prioritaet 1 laut docs/analysis/REWORK_PLAN_DE.md Phase E: Regressionsschutz
fuer den in Phase A behobenen Sicherheitsfund (Path Traversal ueber
praeparierte Upload-Dateinamen, docs/analysis/REPOSITORY_AUDIT_DE.md 1.6)
sowie die in Phase C.4 eingefuehrten Fehlercodes (X-Error-Code-Header).
"""
from __future__ import annotations

import io
import os

import httpx
import pytest

pytestmark = pytest.mark.asyncio


class TestUploadValidation:
    async def test_rejects_unsupported_file_extension(self, client: httpx.AsyncClient):
        files = {"file": ("malware.exe", io.BytesIO(b"beliebiger Inhalt"), "application/octet-stream")}
        res = await client.post("/api/cv/upload", files=files)

        assert res.status_code == 400
        assert res.headers.get("x-error-code") == "cv.invalid_file_type"

    async def test_accepts_pdf_and_sanitizes_path_traversal_filename(
        self, client: httpx.AsyncClient, tmp_path,
    ):
        # Praeparierter Dateiname mit Verzeichnis-Anteilen - genau der in
        # Phase A gefixte Angriffsvektor (os.path.basename() in cv.py).
        malicious_name = "../../../../etc/evil_cv.pdf"
        files = {"file": (malicious_name, io.BytesIO(b"%PDF-1.4 fake"), "application/pdf")}
        res = await client.post("/api/cv/upload", files=files)

        assert res.status_code == 201
        body = res.json()
        # Nur der Basisname darf ankommen, keine Pfadanteile.
        assert body["filename"] == "evil_cv.pdf"
        assert "/" not in body["filename"] and ".." not in body["filename"]

        # Die Datei darf ausschliesslich innerhalb des Upload-Verzeichnisses
        # gelandet sein, nicht ausserhalb (das waere der eigentliche
        # Path-Traversal-Schaden).
        expected_path = tmp_path / "evil_cv.pdf"
        assert expected_path.is_file()
        assert not (tmp_path.parent / "evil_cv.pdf").exists()
        assert not (tmp_path.parent.parent / "etc" / "evil_cv.pdf").exists()


class TestCvNotFoundErrorCode:
    async def test_get_unknown_cv_returns_error_code(self, client: httpx.AsyncClient):
        res = await client.get("/api/cv/999999")

        assert res.status_code == 404
        assert res.headers.get("x-error-code") == "cv.not_found"

    async def test_delete_unknown_cv_returns_error_code(self, client: httpx.AsyncClient):
        res = await client.delete("/api/cv/999999")

        assert res.status_code == 404
        assert res.headers.get("x-error-code") == "cv.not_found"
