"""Stage-gate check infrastructure."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from rich.console import Console
from rich.table import Table

console = Console()


class CheckStatus(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass
class CheckResult:
    """Result of a single check."""

    id: str  # e.g., "S1"
    name: str  # e.g., "Relevance"
    status: CheckStatus
    reason: str = ""


@dataclass
class StageGateResult:
    """Aggregated result of all checks for a stage."""

    stage: str
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def overall(self) -> CheckStatus:
        if any(c.status == CheckStatus.FAIL for c in self.checks):
            return CheckStatus.FAIL
        if any(c.status == CheckStatus.WARN for c in self.checks):
            return CheckStatus.WARN
        return CheckStatus.PASS

    @property
    def passed(self) -> bool:
        return self.overall != CheckStatus.FAIL

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "overall": self.overall.value,
            "checks": [
                {"id": c.id, "name": c.name, "status": c.status.value, "reason": c.reason}
                for c in self.checks
            ],
        }

    def print_summary(self) -> None:
        """Print a rich summary of check results."""
        status_icons = {
            CheckStatus.PASS: "[green]✓[/]",
            CheckStatus.WARN: "[yellow]⚠[/]",
            CheckStatus.FAIL: "[red]✗[/]",
        }

        overall_icon = status_icons[self.overall]
        pass_count = sum(1 for c in self.checks if c.status == CheckStatus.PASS)
        total = len(self.checks)

        console.print(
            f"  {overall_icon} [bold]{self.stage}[/]: "
            f"{pass_count}/{total} pass",
            end="",
        )

        # Inline check details
        details = []
        for c in self.checks:
            icon = status_icons[c.status]
            detail = f"{icon} {c.id}"
            if c.status != CheckStatus.PASS and c.reason:
                detail += f" ({c.reason})"
            details.append(detail)

        if details:
            console.print(" | " + " | ".join(details))
        else:
            console.print()
