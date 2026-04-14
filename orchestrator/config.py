"""Configuration loading for Astra Forge orchestrator."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class AgentMeta:
    """Parsed metadata from an agent .md file's YAML frontmatter."""

    name: str
    description: str
    tools: list[str]
    model: str
    color: str
    memory: str
    readonly: bool
    skills: list[str]
    body: str  # The markdown content after frontmatter


@dataclass
class AstraConfig:
    """Configuration for a single Astra pipeline run."""

    # Paths
    project_dir: Path
    astra_plugin_dir: Path

    # Mode
    lite: bool = False
    interactive: bool = False
    dry_run: bool = False

    # API tokens (from environment)
    anthropic_api_key: str = ""
    github_token: str = ""
    slack_webhook_url: str = ""

    # Loaded agent metadata
    agents: dict[str, AgentMeta] = field(default_factory=dict)

    # Loaded skill paths
    skill_paths: dict[str, Path] = field(default_factory=dict)

    @classmethod
    def load(
        cls,
        project_dir: Path,
        lite: bool = False,
        interactive: bool = False,
        dry_run: bool = False,
    ) -> AstraConfig:
        """Load configuration from environment, filesystem, and arguments."""
        # Resolve plugin directory: ASTRA_PLUGIN_DIR env or ~/astra
        plugin_dir_env = os.environ.get("ASTRA_PLUGIN_DIR")
        if plugin_dir_env:
            astra_plugin_dir = Path(plugin_dir_env)
        else:
            astra_plugin_dir = Path(__file__).resolve().parent.parent

        config = cls(
            project_dir=project_dir.resolve(),
            astra_plugin_dir=astra_plugin_dir.resolve(),
            lite=lite,
            interactive=interactive,
            dry_run=dry_run,
            anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
            github_token=os.environ.get("GITHUB_TOKEN", ""),
            slack_webhook_url=os.environ.get("SLACK_WEBHOOK_URL", ""),
        )

        config.agents = _load_agents(config.astra_plugin_dir / "agents")
        config.skill_paths = _load_skill_paths(config.astra_plugin_dir / "skills")

        return config

    @property
    def cache_dir(self) -> Path:
        """Pipeline cache directory within the project."""
        d = self.project_dir / ".astra-cache"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def state_path(self) -> Path:
        return self.cache_dir / "pipeline-state.json"

    @property
    def audit_log_path(self) -> Path:
        return self.cache_dir / "audit.jsonl"

    @property
    def context_cache_path(self) -> Path:
        return self.cache_dir / "context.md"

    def has_github(self) -> bool:
        return bool(self.github_token)

    def has_slack(self) -> bool:
        return bool(self.slack_webhook_url)


def _load_agents(agents_dir: Path) -> dict[str, AgentMeta]:
    """Parse all agent .md files and extract YAML frontmatter + body."""
    agents: dict[str, AgentMeta] = {}
    if not agents_dir.is_dir():
        return agents

    for md_file in sorted(agents_dir.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(text)
        if not meta or "name" not in meta:
            continue

        agents[meta["name"]] = AgentMeta(
            name=meta["name"],
            description=meta.get("description", ""),
            tools=_parse_tools(meta.get("tools", "")),
            model=meta.get("model", "inherit"),
            color=meta.get("color", "white"),
            memory=meta.get("memory", ""),
            readonly=meta.get("readonly", True),
            skills=meta.get("skills", []),
            body=body,
        )

    return agents


def _load_skill_paths(skills_dir: Path) -> dict[str, Path]:
    """Discover skill directories and their SKILL.md files."""
    paths: dict[str, Path] = {}
    if not skills_dir.is_dir():
        return paths

    for skill_dir in sorted(skills_dir.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if skill_md.is_file():
            text = skill_md.read_text(encoding="utf-8")
            meta, _ = _parse_frontmatter(text)
            name = meta.get("name", skill_dir.name) if meta else skill_dir.name
            paths[name] = skill_md

    return paths


def _parse_frontmatter(text: str) -> tuple[dict[str, Any] | None, str]:
    """Split YAML frontmatter from markdown body."""
    if not text.startswith("---"):
        return None, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text

    try:
        meta = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None, text

    body = parts[2].strip()
    return meta if isinstance(meta, dict) else None, body


def _parse_tools(tools_str: str | list[str]) -> list[str]:
    """Parse tools from either comma-separated string or list."""
    if isinstance(tools_str, list):
        return tools_str
    return [t.strip() for t in tools_str.split(",") if t.strip()]
