"""PM stage — produces SPEC.md from feature description."""

from __future__ import annotations

from orchestrator.config import AstraConfig
from orchestrator.stages.base import Stage
from orchestrator.state import PipelineState


class SpecStage(Stage):
    name = "Spec"
    agent_name = "pm"
    readonly = True
    artifact_filename = "SPEC.md"

    def build_prompt(self, state: PipelineState, config: AstraConfig) -> str:
        parts = [
            f"Conduct product discovery for: {state.feature}",
            "",
            "Produce a complete product specification with:",
            "- Numbered requirements (R1, R2...) with stable IDs",
            "- RICE prioritization (Reach, Impact, Confidence, Effort)",
            "- Given/When/Then acceptance criteria for every requirement",
            "- No vague language — concrete metrics ('fast' → '<200ms p95')",
            "- Now/Next/Later priority tiers",
            "",
        ]

        # Add context cache
        context = self._read_context_cache(config)
        if context:
            parts.append("## Codebase Context (from cache)")
            parts.append(context)
            parts.append("")

        # Add PRODUCT.md context
        product = self._read_file_if_exists(config, "PRODUCT.md")
        if product:
            parts.append("## Existing Product Context (PRODUCT.md)")
            parts.append(product)
            parts.append("")
            parts.append("Frame requirements as deltas to existing features.")
        else:
            parts.append("No PRODUCT.md found — this is the first feature.")

        parts.append("")
        parts.append("Return ONLY the complete SPEC.md content. No explanations outside the spec.")

        return "\n".join(parts)
