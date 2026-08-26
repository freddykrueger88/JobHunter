"""
Tests fuer backend/routers/jobs_image.py (Foto-Upload -> Job per OCR+KI).

Regressionsschutz: der Endpoint war komplett kaputt - `from backend.
services.ai_client import get_ai_client` importierte ein nie existierendes
Modul (ImportError beim Start), und Job(...) wurde mit deutschen
Feldnamen (titel/firma/ort/gehalt_min/...) aufgerufen, die auf dem
Job-Modell nie existierten (echte Felder: title/company/city/...) -
TypeError bei jedem Upload. OCR (pytesseract) + KI-Parsing werden hier
gemockt, damit die Tests deterministisch und ohne echtes Ollama laufen;
die komplette Pipeline wurde zusaetzlich per echtem End-to-End-Test mit
einem synthetischen Testbild gegen die laufende Instanz verifiziert
(siehe BACKLOG.md).
"""
from __future__ import annotations

import io

import httpx
import pytest

import backend.routers.jobs_image as jobs_image_module

pytestmark = pytest.mark.asyncio


class TestFromImage:
    async def test_rejects_non_image_content_type(self, client: httpx.AsyncClient):
        files = {"file": ("doc.pdf", io.BytesIO(b"not an image"), "application/pdf")}
        res = await client.post("/api/jobs/from-image", files=files)
        assert res.status_code == 400

    async def test_successful_upload_creates_job_with_correct_fields(
        self, client: httpx.AsyncClient, monkeypatch,
    ):
        async def fake_extract(image_bytes: bytes) -> str:
            return "Stellenanzeige: Backend Entwickler bei Beispiel GmbH, Bremen"

        async def fake_parse(text: str, model: str = "mistral") -> dict:
            return {
                "title": "Backend Entwickler",
                "company": "Beispiel GmbH",
                "city": "Bremen",
                "description": text,
            }

        monkeypatch.setattr(jobs_image_module, "extract_text_from_image", fake_extract)
        monkeypatch.setattr(jobs_image_module, "parse_job_from_text", fake_parse)

        files = {"file": ("anzeige.png", io.BytesIO(b"fake-png-bytes"), "image/png")}
        res = await client.post("/api/jobs/from-image", files=files)

        assert res.status_code == 200, res.text
        body = res.json()
        assert body["job"]["title"] == "Backend Entwickler"
        assert body["job"]["company"] == "Beispiel GmbH"
        assert body["job"]["city"] == "Bremen"
        assert body["job"]["source_portal"] == "foto-upload"
        assert "id" in body["job"]

    async def test_blurry_image_returns_422(self, client: httpx.AsyncClient, monkeypatch):
        async def fake_extract_fails(image_bytes: bytes) -> str:
            raise ValueError("Kein ausreichender Text erkannt.")

        monkeypatch.setattr(jobs_image_module, "extract_text_from_image", fake_extract_fails)

        files = {"file": ("blurry.png", io.BytesIO(b"fake-png-bytes"), "image/png")}
        res = await client.post("/api/jobs/from-image", files=files)

        assert res.status_code == 422

    async def test_unparseable_text_returns_422(self, client: httpx.AsyncClient, monkeypatch):
        async def fake_extract(image_bytes: bytes) -> str:
            return "irgendein Text ohne erkennbare Stellenangabe"

        async def fake_parse_empty(text: str, model: str = "mistral") -> dict:
            return {"title": "", "company": "", "city": "", "description": text}

        monkeypatch.setattr(jobs_image_module, "extract_text_from_image", fake_extract)
        monkeypatch.setattr(jobs_image_module, "parse_job_from_text", fake_parse_empty)

        files = {"file": ("anzeige.png", io.BytesIO(b"fake-png-bytes"), "image/png")}
        res = await client.post("/api/jobs/from-image", files=files)

        assert res.status_code == 422
