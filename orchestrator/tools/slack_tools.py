"""Slack notification tools."""

from __future__ import annotations

import json
import urllib.request
from typing import Any

from rich.console import Console

console = Console()


def notify_pipeline_event(
    webhook_url: str | None,
    event: str,
    stage: str,
    details: str = "",
    dry_run: bool = False,
) -> bool:
    """Send a pipeline event notification to Slack.

    Args:
        webhook_url: Slack webhook URL (None = skip)
        event: Event type (start, pass, warn, fail, complete)
        stage: Pipeline stage name
        details: Additional details
        dry_run: If True, log but don't send
    """
    if not webhook_url:
        return True  # Silently skip if not configured

    icons = {
        "start": ":arrow_forward:",
        "pass": ":white_check_mark:",
        "warn": ":warning:",
        "fail": ":x:",
        "complete": ":tada:",
    }

    icon = icons.get(event, ":information_source:")
    text = f"{icon} *Astra Forge* — {stage}"
    if details:
        text += f"\n{details}"

    if dry_run:
        console.print(f"  [dim]Slack (dry): {text}[/]")
        return True

    payload = json.dumps({"text": text}).encode("utf-8")

    try:
        req = urllib.request.Request(
            webhook_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        console.print(f"  [dim]Slack notification failed: {e}[/]")
        return False
