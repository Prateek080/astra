"""Multi-channel notification tool for the Astra OpenClaw pipeline.

Replaces orchestrator/tools/slack_tools.py with support for Telegram Bot API,
Discord webhooks, and a silent 'none' channel.

Usage:
    python -m openclaw.scripts.report --channel telegram --event pass --stage S1
    python -m openclaw.scripts.report --channel discord --event fail --stage D3 --details "Lint errors"
    python -m openclaw.scripts.report --dry-run --channel telegram --event start --stage P1
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.request
from typing import Any

ICONS: dict[str, str] = {
    "start": "▶️",
    "pass": "✅",
    "warn": "⚠️",
    "fail": "❌",
    "complete": "\U0001f389",
    "stall": "\U0001f504",
}

EVENTS = list(ICONS.keys())
CHANNELS = ("telegram", "discord", "none")


def _format_message(event: str, stage: str, details: str = "") -> str:
    """Build the notification message string.

    Format: ``{icon} *Astra Forge* — {stage}\\n{details}``
    """
    icon = ICONS.get(event, "ℹ️")
    text = f"{icon} *Astra Forge* — {stage}"
    if details:
        text += f"\n{details}"
    return text


def _send_telegram(
    text: str, token: str, chat_id: str, timeout: int = 10
) -> bool:
    """POST a message via the Telegram Bot API."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps(
        {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status == 200


def _send_discord(text: str, webhook_url: str, timeout: int = 10) -> bool:
    """POST a message via a Discord webhook."""
    payload = json.dumps({"content": text}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status in (200, 204)


def notify_pipeline_event(
    channel: str,
    event: str,
    stage: str,
    details: str = "",
    dry_run: bool = False,
    **config: Any,
) -> bool:
    """Send a pipeline event notification to the configured channel.

    Args:
        channel: One of ``"telegram"``, ``"discord"``, ``"none"``.
        event: Event type — ``start``, ``pass``, ``warn``, ``fail``,
               ``complete``, or ``stall``.
        stage: Pipeline stage name (e.g. ``"S1"``, ``"D3"``).
        details: Optional human-readable details.
        dry_run: If ``True``, print the formatted message without sending.
        **config: Channel-specific settings:
            - ``telegram_token`` / ``telegram_chat_id`` for Telegram.
            - ``discord_webhook_url`` for Discord.

    Returns:
        ``True`` on success (or skip), ``False`` on failure.
    """
    if channel == "none":
        return True

    text = _format_message(event, stage, details)

    if dry_run:
        print(f"[DRY RUN] {text}")
        return True

    try:
        if channel == "telegram":
            token = config.get("telegram_token") or ""
            chat_id = config.get("telegram_chat_id") or ""
            if not token or not chat_id:
                print("error: telegram requires --telegram-token and --telegram-chat-id")
                return False
            return _send_telegram(text, token, chat_id)

        if channel == "discord":
            webhook_url = config.get("discord_webhook_url") or ""
            if not webhook_url:
                print("error: discord requires --discord-webhook-url")
                return False
            return _send_discord(text, webhook_url)

        print(f"error: unknown channel '{channel}'")
        return False
    except Exception as exc:
        print(f"error: notification failed: {exc}")
        return False


def _load_config(path: str) -> dict[str, Any]:
    """Load reporting config from an OpenClaw plugin.json file.

    Reads ``configSchema.properties.reporting`` and extracts default values
    and any overrides present in the file.
    """
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)

    reporting: dict[str, Any] = {}
    props = (
        data.get("configSchema", {})
        .get("properties", {})
        .get("reporting", {})
        .get("properties", {})
    )
    for key, schema in props.items():
        if "default" in schema:
            reporting[key] = schema["default"]
    return reporting


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="report",
        description="Send Astra pipeline notifications via Telegram or Discord.",
    )
    parser.add_argument(
        "--channel",
        choices=CHANNELS,
        default="none",
        help="Notification channel (default: none)",
    )
    parser.add_argument(
        "--event",
        choices=EVENTS,
        required=True,
        help="Pipeline event type",
    )
    parser.add_argument(
        "--stage",
        required=True,
        help="Pipeline stage name (e.g. S1, D3)",
    )
    parser.add_argument(
        "--details",
        default="",
        help="Optional details to include in the message",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print formatted message without sending",
    )
    parser.add_argument(
        "--telegram-token",
        default=os.environ.get("TELEGRAM_BOT_TOKEN", ""),
        help="Telegram Bot API token (env: TELEGRAM_BOT_TOKEN)",
    )
    parser.add_argument(
        "--telegram-chat-id",
        default=os.environ.get("TELEGRAM_CHAT_ID", ""),
        help="Telegram chat ID (env: TELEGRAM_CHAT_ID)",
    )
    parser.add_argument(
        "--discord-webhook-url",
        default=os.environ.get("DISCORD_WEBHOOK_URL", ""),
        help="Discord webhook URL (env: DISCORD_WEBHOOK_URL)",
    )
    parser.add_argument(
        "--config",
        default="",
        help="Path to openclaw/plugin.json to read reporting defaults",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    """CLI entry point."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Merge plugin.json defaults (CLI args and env vars take precedence)
    if args.config:
        file_cfg = _load_config(args.config)
        if not args.channel or args.channel == "none":
            args.channel = file_cfg.get("channel", args.channel)
        if not args.telegram_token:
            args.telegram_token = file_cfg.get("telegramBotToken", "")
        if not args.telegram_chat_id:
            args.telegram_chat_id = file_cfg.get("telegramChatId", "")
        if not args.discord_webhook_url:
            args.discord_webhook_url = file_cfg.get("discordWebhookUrl", "")

    success = notify_pipeline_event(
        channel=args.channel,
        event=args.event,
        stage=args.stage,
        details=args.details,
        dry_run=args.dry_run,
        telegram_token=args.telegram_token,
        telegram_chat_id=args.telegram_chat_id,
        discord_webhook_url=args.discord_webhook_url,
    )
    if not success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
