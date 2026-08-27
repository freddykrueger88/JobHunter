"""
Tests fuer backend/services/market_analyzer.py + POST /api/applications/
{id}/market-analysis.

Bugfix-Sweep 2026-08-27: MarketAnalyzerPanel.tsx war fertig gebaut,
aber ohne Router (der Service war fertig und bugfrei, es fehlte nur
die Anbindung).
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.job import Job

pytestmark = pytest.mark.asyncio


def _mock_ollama_response(response_text: str):
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"response": response_text}
    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


class TestMarketAnalysis:
    async def test_returns_analysis(self, client: httpx.AsyncClient, db: AsyncSession):
        job = Job(title="Backend Engineer", company="Beispiel GmbH", description="Wir suchen ab sofort...")
        db.add(job)
        await db.commit()
        await db.refresh(job)
        app_res = await client.post("/api/applications/", json={"job_id": job.id})
        app_id = app_res.json()["id"]

        raw = '''{"wettbewerb": "mittel", "wettbewerb_begruendung": "x", "optimaler_zeitpunkt": "sofort",
            "zeitpunkt_begruendung": "x", "unternehmenstyp": "kmu", "strategie": "Direkt bewerben",
            "strategie_begruendung": "x", "chancen": ["a"], "risiken": ["b"]}'''
        with patch("httpx.AsyncClient", return_value=_mock_ollama_response(raw)):
            res = await client.post(f"/api/applications/{app_id}/market-analysis", json={
                "job_title": "Backend Engineer",
                "firma": "Beispiel GmbH",
                "job_description": "Wir suchen ab sofort...",
            })

        assert res.status_code == 200, res.text
        body = res.json()
        assert body["wettbewerb"] == "mittel"
        assert body["heuristik"]["dringlichkeit"] is True

    async def test_nonexistent_application_returns_404(self, client: httpx.AsyncClient):
        res = await client.post("/api/applications/999999/market-analysis", json={
            "job_title": "X", "firma": "Y", "job_description": "Z",
        })
        assert res.status_code == 404
