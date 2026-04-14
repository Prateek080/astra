"""Designer stage — produces DESIGN.md from SPEC.md."""

from __future__ import annotations

from orchestrator.config import AstraConfig
from orchestrator.stages.base import Stage
from orchestrator.state import PipelineState


class DesignStage(Stage):
    name = "Design"
    agent_name = "designer"
    readonly = True
    artifact_filename = "DESIGN.md"

    def build_prompt(self, state: PipelineState, config: AstraConfig) -> str:
        spec = self._read_file_if_exists(config, "SPEC.md")
        context = self._read_context_cache(config)
        product = self._read_file_if_exists(config, "PRODUCT.md")

        parts = [
            "Create a UI/UX design from the spec below.",
            "Produce DESIGN.md with D-R{n} traceability for every frontend requirement.",
            "Backend-only requirements: note as 'Technical — handled by architect agent'.",
            "",
            "## SPEC.md",
            spec,
        ]

        if context:
            parts += ["", "## Codebase Context", context]
        if product:
            parts += ["", "## PRODUCT.md", product]

        parts += ["", "Return ONLY the complete DESIGN.md content."]
        return "\n".join(parts)
