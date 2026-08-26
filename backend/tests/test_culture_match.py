"""
Tests fuer backend/services/culture_match.py (#75/G.3.10, Backlog Phase H.4).

Mockt die Ollama-Antwort, um die JSON-Validierung/-Koerzierung deterministisch
zu testen - inkl. Regressionsschutz fuer einen echten, live beim manuellen
Testen gefundenen Bug: Mistral liefert "score" nicht immer als JSON-Zahl,
manchmal als String ("20" statt 20) - das ließ die strikte Validierung
faelschlich in den Fallback laufen, obwohl die Antwort inhaltlich brauchbar
war.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.services.culture_match import _FALLBACK, analyze_culture_match

pytestmark = pytest.mark.asyncio


def _mock_ollama_response(response_text: str):
    """Baut einen Kontextmanager-Mock, der httpx.AsyncClient().post(...) ersetzt."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"response": response_text}

    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


class TestAnalyzeCultureMatch:
    async def test_valid_json_with_numeric_score(self):
        raw = '{"score": 85, "unternehmenstyp_erkannt": "startup", "passende_punkte": ["flach"], "abweichende_punkte": [], "kurzfazit": "Guter Match"}'
        with patch("backend.services.culture_match.httpx.AsyncClient", return_value=_mock_ollama_response(raw)):
            result = await analyze_culture_match("Beschreibung", "Firma", "startup", "flach", "mistral")

        assert result["score"] == 85
        assert result["unternehmenstyp_erkannt"] == "startup"
        assert result["passende_punkte"] == ["flach"]

    async def test_score_as_string_is_coerced_not_rejected(self):
        """Regression: 'score': '20' (String statt Zahl) darf nicht in den Fallback laufen."""
        raw = '{"score": "20", "unternehmenstyp_erkannt": "konzern", "passende_punkte": [], "abweichende_punkte": ["a"], "kurzfazit": "Kein Match"}'
        with patch("backend.services.culture_match.httpx.AsyncClient", return_value=_mock_ollama_response(raw)):
            result = await analyze_culture_match("Beschreibung", "Firma", "startup", "flach", "mistral")

        assert result["score"] == 20
        assert result["unternehmenstyp_erkannt"] == "konzern"
        assert result != _FALLBACK

    async def test_score_out_of_range_is_clamped(self):
        raw = '{"score": 150, "unternehmenstyp_erkannt": "startup", "passende_punkte": [], "abweichende_punkte": [], "kurzfazit": "x"}'
        with patch("backend.services.culture_match.httpx.AsyncClient", return_value=_mock_ollama_response(raw)):
            result = await analyze_culture_match("Beschreibung", "Firma", "startup", "flach", "mistral")

        assert result["score"] == 100

    async def test_non_json_response_returns_fallback(self):
        raw = "Entschuldigung, ich kann diese Anfrage nicht bearbeiten."
        with patch("backend.services.culture_match.httpx.AsyncClient", return_value=_mock_ollama_response(raw)):
            result = await analyze_culture_match("Beschreibung", "Firma", "startup", "flach", "mistral")

        assert result == _FALLBACK

    async def test_malformed_json_shape_returns_fallback(self):
        """Fehlt ein Pflichtfeld (hier kurzfazit) -> Fallback statt kaputtem Objekt."""
        raw = '{"score": 50, "unternehmenstyp_erkannt": "startup", "passende_punkte": [], "abweichende_punkte": []}'
        with patch("backend.services.culture_match.httpx.AsyncClient", return_value=_mock_ollama_response(raw)):
            result = await analyze_culture_match("Beschreibung", "Firma", "startup", "flach", "mistral")

        assert result == _FALLBACK
