"""Planner stage — produces PLAN.md from SPEC.md."""

from __future__ import annotations

from orchestrator.config import AstraConfig
from orchestrator.stages.base import Stage
from orchestrator.state import PipelineState


class PlanStage(Stage):
    name = "Plan"
    agent_name = "planner"
    readonly = True
    artifact_filename = "PLAN.md"

    def build_prompt(self, state: PipelineState, config: AstraConfig) -> str:
        spec = self._read_file_if_exists(config, "SPEC.md")
        context = self._read_context_cache(config)
        design = self._read_file_if_exists(config, "DESIGN.md")

        parts = [
            "Create a phased implementation plan from the spec below.",
            "Produce PLAN.md with phases, tasks, test gates.",
            "Reference R{n} requirements in each phase.",
            "Each phase must be independently verifiable and completable in <50% context.",
            "Mark independent phases for parallel execution.",
            "",
            "## SPEC.md",
            spec,
        ]

        if context:
            parts += ["", "## Codebase Context", context]
        if design:
            parts += ["", "## DESIGN.md (reference D-R{n} elements)", design]

        parts += ["", "Return ONLY the complete PLAN.md content."]
        return "\n".join(parts)
