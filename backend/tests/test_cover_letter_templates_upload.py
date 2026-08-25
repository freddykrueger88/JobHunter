"""
Tests fuer backend/routers/cover_letter_templates.py (Upload-Endpoint).

Regressionsschutz fuer den Path-Traversal-Fund aus Backlog Phase K.5:
der Upload-Endpoint aus PR #91 entstand nach dem in Phase A.5 fuer
routers/cv.py etablierten os.path.basename()-Fix und hatte ihn noch
nicht uebernommen - siehe docs/analysis/BACKLOG.md Phase K.5.
"""
from __future__ import annotations

import io

import httpx
import pytest
from docx import Document

pytestmark = pytest.mark.asyncio


def _make_docx_bytes() -> bytes:
    """Baut eine minimale, aber valide .docx-Datei im Speicher."""
    doc = Document()
    doc.add_paragraph("Sehr geehrte Damen und Herren,")
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


class TestUploadValidation:
    async def test_rejects_non_docx_extension(self, client: httpx.AsyncClient):
        files = {"file": ("malware.exe", io.BytesIO(b"beliebiger Inhalt"), "application/octet-stream")}
        res = await client.post("/api/cover-letter-templates/upload", files=files)

        assert res.status_code == 400

    async def test_sanitizes_path_traversal_filename(
        self, client: httpx.AsyncClient, tmp_path,
    ):
        malicious_name = "../../../../etc/evil_vorlage.docx"
        docx_bytes = _make_docx_bytes()

        files = {
            "file": (
                malicious_name,
                io.BytesIO(docx_bytes),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        }
        res = await client.post("/api/cover-letter-templates/upload", files=files)

        assert res.status_code == 201
        body = res.json()
        assert body["filename"] == "evil_vorlage.docx"
        assert "/" not in body["filename"] and ".." not in body["filename"]

        expected_path = tmp_path / "evil_vorlage.docx"
        assert expected_path.is_file()
        assert not (tmp_path.parent / "evil_vorlage.docx").exists()
        assert not (tmp_path.parent.parent / "etc" / "evil_vorlage.docx").exists()
