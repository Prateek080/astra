"""Implementation stage — executes PLAN.md phases via implementer agent."""

from __future__ import annotations

import re
from typing import Any

from rich.console import Console

from orchestrator.config import AstraConfig
from orchestrator.stages.base import Stage, StageResult
from orchestrator.state import PipelineState

console = Console()


class ImplementStage(Stage):
    name = "Implement"
    agent_name = "implementer"
    readonly = False
    artifact_filename = None  # Produces code, not a single artifact

    def build_prompt(self, state: PipelineState, config: AstraConfig) -> str:
        """Build prompt for the full implementation run."""
        plan = self._read_file_if_exists(config, "PLAN.md")
        spec = self._read_file_if_exists(config, "SPEC.md")
        design = self._read_file_if_exists(config, "DESIGN.md")
        technical = self._read_file_if_exists(config, "TECHNICAL.md")
        context = self._read_context_cache(config)

        parts = [
            "Implement the plan below. Execute each phase in order.",
            "After each phase: run tests, lint, type-check. Fix failures before moving on.",
            "If something fails twice, stop and report what went wrong.",
            "",
            "## PLAN.md",
            plan,
            "",
            "## SPEC.md (requirements and acceptance criteria)",
            spec,
        ]

        if technical:
            parts += [
                "",
                "## TECHNICAL.md (exact API schemas, data models — follow precisely)",
                technical,
            ]
        if design:
            parts += [
                "",
                "## DESIGN.md (component specs, tokens, layouts — follow precisely)",
                design,
            ]
        if context:
            parts += ["", "## Codebase Context", context]

        parts += [
            "",
            "Implement all phases. Commit nothing — just write the code and verify it works.",
            "Return a summary of what was implemented, which tests pass, and any issues.",
        ]
        return "\n".join(parts)

    def get_allowed_tools(self) -> list[str]:
        return ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "Agent"]

    def get_permission_mode(self) -> str:
        return "acceptEdits"

    async def run(self, state: PipelineState, config: AstraConfig) -> StageResult:
        """Run implementation — delegates to the base Stage.run()."""
        return await super().run(state, config)
