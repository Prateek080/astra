"""Architect stage — produces TECHNICAL.md from SPEC.md, DESIGN.md, PLAN.md."""

from __future__ import annotations

from orchestrator.config import AstraConfig
from orchestrator.stages.base import Stage
from orchestrator.state import PipelineState


class ArchitectStage(Stage):
    name = "Architect"
    agent_name = "architect"
    readonly = True
    artifact_filename = "TECHNICAL.md"

    def build_prompt(self, state: PipelineState, config: AstraConfig) -> str:
        spec = self._read_file_if_exists(config, "SPEC.md")
        design = self._read_file_if_exists(config, "DESIGN.md")
        plan = self._read_file_if_exists(config, "PLAN.md")
        context = self._read_context_cache(config)

        parts = [
            "Create a technical design from the artifacts below.",
            "Produce TECHNICAL.md with T-R{n} traceability, ADRs, API contracts, data models.",
            "",
            "## SPEC.md",
            spec,
        ]

        if design:
            parts += ["", "## DESIGN.md", design]
        if plan:
            parts += ["", "## PLAN.md", plan]
        if context:
            parts += ["", "## Codebase Context", context]

        parts += ["", "Return ONLY the complete TECHNICAL.md content."]
        return "\n".join(parts)
