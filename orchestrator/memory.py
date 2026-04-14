"""Agent memory persistence — cross-session learning per agent persona."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


MEMORY_DIR_NAME = "docs/.agent-memory"


def load_agent_memory(project_dir: Path, agent_name: str) -> str:
    """Load accumulated learnings for an agent persona."""
    memory_file = project_dir / MEMORY_DIR_NAME / f"{agent_name}.md"
    if memory_file.is_file():
        return memory_file.read_text(encoding="utf-8")
    return ""


def save_agent_memory(project_dir: Path, agent_name: str, learnings: str) -> None:
    """Append new learnings for an agent persona with timestamp."""
    if not learnings.strip():
        return

    memory_dir = project_dir / MEMORY_DIR_NAME
    memory_dir.mkdir(parents=True, exist_ok=True)
    memory_file = memory_dir / f"{agent_name}.md"

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entry = f"\n## {timestamp}\n\n{learnings.strip()}\n"

    with open(memory_file, "a", encoding="utf-8") as f:
        f.write(entry)


def get_memory_prompt_section(project_dir: Path, agent_name: str) -> str:
    """Get memory content formatted for inclusion in agent prompt."""
    memory = load_agent_memory(project_dir, agent_name)
    if not memory:
        return ""
    return f"\n## Your Past Learnings (from previous sessions)\n\n{memory}\n"
