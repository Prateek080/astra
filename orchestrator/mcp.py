"""MCP server configuration builder."""

from __future__ import annotations

from orchestrator.config import AstraConfig


def build_mcp_servers(config: AstraConfig) -> dict:
    """Build MCP server configuration for Agent SDK options."""
    servers: dict = {
        "context7": {
            "command": "npx",
            "args": ["-y", "@upstash/context7-mcp"],
        },
        "playwright": {
            "command": "npx",
            "args": ["-y", "@playwright/mcp@latest"],
        },
        "deepwiki": {
            "command": "npx",
            "args": ["-y", "deepwiki-mcp"],
        },
    }

    if config.has_github():
        servers["github"] = {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": config.github_token},
        }

    return servers
