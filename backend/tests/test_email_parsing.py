"""
Tests fuer backend/routers/email_parsing.py.

Regressionsschutz: POST /api/email/connect rief conn.logout() nur nach
erfolgreichem Login auf - schlug der Login fehl (z.B. falsches Passwort),
blieb die IMAP-Socket-Verbindung offen (kein finally). Jetzt wird
logout() in jedem Fall versucht.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

pytestmark = pytest.mark.asyncio


class TestConnectEndpoint:
    async def test_logout_called_on_successful_login(self, client: httpx.AsyncClient):
        mock_conn = MagicMock()
        with patch("imaplib.IMAP4_SSL", return_value=mock_conn):
            res = await client.post("/api/email/connect", json={
                "host": "imap.example.com", "username": "user@example.com", "password": "pw",
            })

        assert res.status_code == 200, res.text
        mock_conn.logout.assert_called_once()

    async def test_logout_called_even_when_login_fails(self, client: httpx.AsyncClient):
        """Regression: die Verbindung blieb offen, wenn login() eine
        Exception warf - logout() stand nur im Erfolgspfad."""
        mock_conn = MagicMock()
        mock_conn.login.side_effect = Exception("Authentication failed")
        with patch("imaplib.IMAP4_SSL", return_value=mock_conn):
            res = await client.post("/api/email/connect", json={
                "host": "imap.example.com", "username": "user@example.com", "password": "wrong",
            })

        assert res.status_code == 400
        mock_conn.logout.assert_called_once()
