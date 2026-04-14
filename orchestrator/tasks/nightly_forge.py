"""Nightly forge task — reads backlog, runs next feature."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

console = Console()


async def run_nightly_forge() -> None:
    """Read .astra-cache/backlog.md, pick next feature, run pipeline."""
    from orchestrator.config import AstraConfig
    from orchestrator.pipeline import run_pipeline

    project_dir = Path.cwd()
    backlog_path = project_dir / ".astra-cache" / "backlog.md"

    if not backlog_path.is_file():
        console.print("[dim]No backlog found at .astra-cache/backlog.md[/]")
        console.print("[dim]Create one with features listed as '- [ ] feature description'[/]")
        return

    # Parse backlog — find first unchecked item
    lines = backlog_path.read_text(encoding="utf-8").strip().split("\n")
    feature = None
    feature_line_idx = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("- [ ]"):
            feature = stripped[5:].strip()
            feature_line_idx = i
            break

    if not feature:
        console.print("[dim]All backlog items complete. Nothing to build.[/]")
        return

    console.print(f"[bold]Nightly forge:[/] {feature}")

    # Mark as in progress
    lines[feature_line_idx] = lines[feature_line_idx].replace("- [ ]", "- [~]")
    backlog_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Run pipeline
    config = AstraConfig.load(project_dir=project_dir)

    try:
        await run_pipeline(config=config, feature=feature)

        # Mark as complete
        lines[feature_line_idx] = lines[feature_line_idx].replace("- [~]", "- [x]")
        backlog_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except Exception as e:
        console.print(f"[red]Nightly forge failed: {e}[/]")
        # Mark as failed
        lines[feature_line_idx] = lines[feature_line_idx].replace("- [~]", "- [!]")
        backlog_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
