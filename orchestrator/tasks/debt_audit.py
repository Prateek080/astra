"""Debt audit task — runs tech debt analysis and writes report."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console

console = Console()


async def run_debt_audit() -> None:
    """Run debt audit agent and write report to docs/debt-reports/."""
    from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

    project_dir = Path.cwd()

    prompt = (
        "Conduct a technical debt audit of this project.\n"
        "Analyze: deprecated dependencies, code smells, missing tests, "
        "TODO/FIXME comments, dead code, security vulnerabilities.\n"
        "Produce a structured report with severity ratings and remediation suggestions."
    )

    console.print("[bold]Debt Audit[/] — scanning for technical debt...")

    try:
        output = ""
        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                allowed_tools=["Read", "Grep", "Glob", "Bash"],
                permission_mode="default",
                cwd=str(project_dir),
            ),
        ):
            if isinstance(message, ResultMessage) and hasattr(message, "result"):
                output = message.result or ""

        if output:
            reports_dir = project_dir / "docs" / "debt-reports"
            reports_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            report_path = reports_dir / f"debt-audit-{timestamp}.md"
            report_path.write_text(output, encoding="utf-8")
            console.print(f"[green]✓[/] Report saved: {report_path}")
        else:
            console.print("[dim]No audit output produced.[/]")

    except Exception as e:
        console.print(f"[red]Debt audit failed: {e}[/]")
