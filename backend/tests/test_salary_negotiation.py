"""
Tests fuer backend/services/salary_negotiation.py + POST /api/salary/negotiate.

Bugfix-Sweep 2026-08-27: SalaryNegotiationModal.tsx + der Service waren
fertig gebaut, aber ohne Router (POST /api/salary/negotiate gab es
nirgends) und ohne jede Einbindung im Frontend. Ausserdem erwartete das
Modal gehaltWunsch als festen Prop, den niemand liefern konnte - jetzt
ein Eingabefeld im Modal selbst.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

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


class TestSalaryNegotiate:
    async def test_returns_scenarios(self, client: httpx.AsyncClient):
        raw = '''{"analyse": "Gute Position", "szenarien": [
            {"typ": "konservativ", "betrag": 48000, "begruendung": "x", "formulierung_email": "e", "formulierung_telefonat": "t"},
            {"typ": "realistisch", "betrag": 52000, "begruendung": "x", "formulierung_email": "e", "formulierung_telefonat": "t"},
            {"typ": "optimistisch", "betrag": 56000, "begruendung": "x", "formulierung_email": "e", "formulierung_telefonat": "t"}
        ], "tipps": ["Tipp 1"]}'''
        with patch("httpx.AsyncClient", return_value=_mock_ollama_response(raw)):
            res = await client.post("/api/salary/negotiate", json={
                "stelle": "Backend Engineer",
                "ort": "Bremen",
                "erfahrung_jahre": 5,
                "gehalt_wunsch": 52000,
                "gehalt_anzeige_min": 45000,
                "gehalt_anzeige_max": 55000,
            })

        assert res.status_code == 200, res.text
        body = res.json()
        assert len(body["szenarien"]) == 3
        assert body["szenarien"][1]["betrag"] == 52000

    async def test_missing_gehalt_wunsch_returns_422(self, client: httpx.AsyncClient):
        res = await client.post("/api/salary/negotiate", json={"stelle": "Backend Engineer"})
        assert res.status_code == 422
