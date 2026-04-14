"""SDK callback hooks — permissions, audit trail, context injection."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Read-only agent names
READONLY_AGENTS = {"pm", "designer", "architect", "planner", "reviewer"}

# Paths implementer is allowed to write to
ALLOWED_WRITE_PATHS = ["src/", "app/", "lib/", "tests/", "test/", "__tests__/", "pages/"]

# Paths no agent should write to
DENIED_WRITE_PATHS = [".env", ".git/", "node_modules/", ".astra-cache/", "package-lock.json"]


async def enforce_readonly(input_data: dict, tool_use_id: str, context: Any) -> dict:
    """PreToolUse: Deny Write/Edit for read-only agents."""
    tool_name = input_data.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        return {}

    # Try to determine current agent
    agent_id = input_data.get("agent_id", "")
    if agent_id in READONLY_AGENTS:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"{agent_id} agent is read-only",
            }
        }
    return {}


async def enforce_path_restrictions(input_data: dict, tool_use_id: str, context: Any) -> dict:
    """PreToolUse: Restrict write paths for implementer."""
    tool_name = input_data.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        return {}

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Check denied paths
    for denied in DENIED_WRITE_PATHS:
        if denied in file_path:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Writing to {denied} is not allowed",
                }
            }

    return {}


async def audit_trail(input_data: dict, tool_use_id: str, context: Any) -> dict:
    """PostToolUse: Log every tool call to .astra-cache/audit.jsonl."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": input_data.get("tool_name", "unknown"),
        "tool_use_id": tool_use_id,
    }

    # Extract key input info without full content
    tool_input = input_data.get("tool_input", {})
    if "file_path" in tool_input:
        entry["file_path"] = tool_input["file_path"]
    if "command" in tool_input:
        cmd = tool_input["command"]
        entry["command"] = cmd[:200] if isinstance(cmd, str) else str(cmd)[:200]
    if "pattern" in tool_input:
        entry["pattern"] = tool_input["pattern"]

    # Write async
    try:
        audit_path = Path(".astra-cache/audit.jsonl")
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        with open(audit_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass  # Don't fail the pipeline for audit logging

    return {}


async def inject_context(input_data: dict, tool_use_id: str, context: Any) -> dict:
    """SubagentStart: Remind subagents to read the context cache."""
    return {
        "systemMessage": (
            "IMPORTANT: If .astra-cache/context.md exists in the project root, "
            "read it FIRST for codebase context. Do not re-scan the codebase independently."
        )
    }


def build_hooks_config(readonly: bool = True) -> dict[str, list[dict]]:
    """Build hooks configuration dict for ClaudeAgentOptions."""
    hooks: dict[str, list] = {
        "PostToolUse": [{"hooks": [audit_trail]}],
        "SubagentStart": [{"hooks": [inject_context]}],
    }

    if readonly:
        hooks["PreToolUse"] = [
            {"matcher": "Write|Edit", "hooks": [enforce_readonly, enforce_path_restrictions]},
        ]
    else:
        hooks["PreToolUse"] = [
            {"matcher": "Write|Edit", "hooks": [enforce_path_restrictions]},
        ]

    return hooks
