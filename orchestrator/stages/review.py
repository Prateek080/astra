"""Review stage — reviews all changes against spec and design."""

from __future__ import annotations

from orchestrator.config import AstraConfig
from orchestrator.stages.base import Stage
from orchestrator.state import PipelineState


class ReviewStage(Stage):
    name = "Review"
    agent_name = "reviewer"
    readonly = True
    artifact_filename = None  # Produces review findings, not a file

    def build_prompt(self, state: PipelineState, config: AstraConfig) -> str:
        spec = self._read_file_if_exists(config, "SPEC.md")
        design = self._read_file_if_exists(config, "DESIGN.md")
        technical = self._read_file_if_exists(config, "TECHNICAL.md")

        parts = [
            "Review all code changes in this project.",
            "Run `git diff` to see what changed.",
            "",
            "Check against these artifacts:",
            "",
            "## SPEC.md (acceptance criteria)",
            spec,
        ]

        if design:
            parts += ["", "## DESIGN.md (UI specs)", design]
        if technical:
            parts += ["", "## TECHNICAL.md (API/data contracts)", technical]

        parts += [
            "",
            "For each requirement R{n}, verify the Given/When/Then acceptance criteria are met.",
            "Organize findings as:",
            "- **Critical** — Must fix: security, data loss, broken functionality",
            "- **Warning** — Should fix: performance, missing edge cases",
            "- **Suggestion** — Consider: naming, minor refactors",
            "",
            "Return your findings. Be specific: file path, what's wrong, how to fix.",
        ]
        return "\n".join(parts)
