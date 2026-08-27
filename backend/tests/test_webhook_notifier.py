"""
Tests fuer backend/services/webhook_notifier.py (#82, G.3.4).

Slack/Discord/ntfy-Webhook-Benachrichtigungen bei neuen Suchprofil-
Treffern und/oder Bewerbungs-Statusaenderungen. Deckt die Payload-
Unterschiede der drei Dienste ab (Slack/Discord: JSON, ntfy: reiner
Text), sowie die Opt-in-Schalter (webhook_notify_new_jobs/
webhook_notify_status_change) und dass ein fehlendes/leeres Setup
keinen Request ausloest statt zu crashen.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.core.crypto import encrypt
from backend.services.webhook_notifier import (
    notify_new_jobs,
    notify_status_change,
    send_test_webhook,
    send_webhook,
)

pytestmark = pytest.mark.asyncio


def _mock_client(status_ok=True):
    mock_response = MagicMock()
    if status_ok:
        mock_response.raise_for_status = MagicMock()
    else:
        import httpx
        mock_response.raise_for_status = MagicMock(side_effect=httpx.HTTPStatusError(
            "err", request=MagicMock(), response=MagicMock(status_code=400),
        ))
    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


class TestSendWebhook:
    async def test_slack_sends_json_text_payload(self):
        mock_client = _mock_client()
        with patch("httpx.AsyncClient", return_value=mock_client):
            ok = await send_webhook("https://hooks.slack.com/x", "slack", "Hallo")

        assert ok is True
        assert mock_client.post.call_args.kwargs["json"] == {"text": "Hallo"}

    async def test_discord_sends_json_content_payload(self):
        mock_client = _mock_client()
        with patch("httpx.AsyncClient", return_value=mock_client):
            ok = await send_webhook("https://discord.com/api/webhooks/x", "discord", "Hallo")

        assert ok is True
        assert mock_client.post.call_args.kwargs["json"] == {"content": "Hallo"}

    async def test_ntfy_sends_plain_text_body(self):
        mock_client = _mock_client()
        with patch("httpx.AsyncClient", return_value=mock_client):
            ok = await send_webhook("https://ntfy.sh/mytopic", "ntfy", "Hallo")

        assert ok is True
        assert mock_client.post.call_args.kwargs["content"] == "Hallo".encode("utf-8")
        assert "json" not in mock_client.post.call_args.kwargs

    async def test_empty_url_returns_false_without_request(self):
        mock_client = _mock_client()
        with patch("httpx.AsyncClient", return_value=mock_client):
            ok = await send_webhook("", "slack", "Hallo")

        assert ok is False
        mock_client.post.assert_not_called()

    async def test_unknown_type_returns_false(self):
        ok = await send_webhook("https://example.com/x", "telegram", "Hallo")
        assert ok is False

    async def test_http_error_returns_false(self):
        mock_client = _mock_client(status_ok=False)
        with patch("httpx.AsyncClient", return_value=mock_client):
            ok = await send_webhook("https://hooks.slack.com/x", "slack", "Hallo")

        assert ok is False


def _settings(**overrides):
    defaults = dict(
        webhook_url_enc=None, webhook_type="slack",
        webhook_notify_new_jobs=False, webhook_notify_status_change=False,
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


class TestNotifyNewJobs:
    async def test_skips_when_no_url_configured(self):
        settings_row = _settings(webhook_notify_new_jobs=True)
        with patch("backend.services.webhook_notifier.send_webhook", new=AsyncMock()) as mock_send:
            await notify_new_jobs(settings_row, "Mein Profil", 3)

        mock_send.assert_not_called()

    async def test_skips_when_opted_out(self):
        settings_row = _settings(webhook_url_enc=encrypt("https://x"), webhook_notify_new_jobs=False)
        with patch("backend.services.webhook_notifier.send_webhook", new=AsyncMock()) as mock_send:
            await notify_new_jobs(settings_row, "Mein Profil", 3)

        mock_send.assert_not_called()

    async def test_sends_when_configured_and_opted_in(self):
        settings_row = _settings(webhook_url_enc=encrypt("https://hooks.slack.com/x"), webhook_notify_new_jobs=True)
        with patch("backend.services.webhook_notifier.send_webhook", new=AsyncMock(return_value=True)) as mock_send:
            await notify_new_jobs(settings_row, "Mein Profil", 3)

        mock_send.assert_called_once()
        args = mock_send.call_args.args
        assert args[0] == "https://hooks.slack.com/x"
        assert args[1] == "slack"
        assert "Mein Profil" in args[2]
        assert "3" in args[2]


class TestNotifyStatusChange:
    async def test_skips_when_opted_out(self):
        settings_row = _settings(webhook_url_enc=encrypt("https://x"), webhook_notify_status_change=False)
        with patch("backend.services.webhook_notifier.send_webhook", new=AsyncMock()) as mock_send:
            await notify_status_change(settings_row, "Backend Engineer", "Acme GmbH", "beworben", "interview")

        mock_send.assert_not_called()

    async def test_sends_with_old_and_new_status_in_message(self):
        settings_row = _settings(webhook_url_enc=encrypt("https://hooks.slack.com/x"), webhook_notify_status_change=True)
        with patch("backend.services.webhook_notifier.send_webhook", new=AsyncMock(return_value=True)) as mock_send:
            await notify_status_change(settings_row, "Backend Engineer", "Acme GmbH", "beworben", "interview")

        message = mock_send.call_args.args[2]
        assert "beworben" in message
        assert "interview" in message
        assert "Backend Engineer" in message
        assert "Acme GmbH" in message


class TestSendTestWebhook:
    async def test_returns_error_when_not_configured(self):
        settings_row = _settings(webhook_url_enc=None)
        result = await send_test_webhook(settings_row)

        assert result["success"] is False
        assert result["error"]

    async def test_returns_success_when_send_succeeds(self):
        settings_row = _settings(webhook_url_enc=encrypt("https://hooks.slack.com/x"))
        with patch("backend.services.webhook_notifier.send_webhook", new=AsyncMock(return_value=True)):
            result = await send_test_webhook(settings_row)

        assert result["success"] is True
        assert result["error"] is None
