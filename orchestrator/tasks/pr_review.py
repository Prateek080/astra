"""PR review task — reviews current branch changes."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

console = Console()


async def run_pr_review() -> None:
    """Run reviewer agent on current branch diff against main."""
    from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

    project_dir = Path.cwd()

    prompt = (
        "Review all changes on the current branch compared to main.\n"
        "Run `git diff main...HEAD` to see the changes.\n"
        "Apply the review-checklist: security, performance, quality, reusability, tech debt.\n"
        "Organize findings as Critical / Warning / Suggestion.\n"
        "Be specific: file path, what's wrong, how to fix."
    )

    console.print("[bold]PR Review[/] — reviewing branch changes...")

    try:
        async for message in query(
            prompt=prompt,
            options=ClaudeAgentOptions(
                allowed_tools=["Read", "Grep", "Glob", "Bash"],
                permission_mode="default",
                cwd=str(project_dir),
            ),
        ):
            if isinstance(message, ResultMessage) and hasattr(message, "result"):
                console.print(message.result or "No findings.")
    except Exception as e:
        console.print(f"[red]PR review failed: {e}[/]")
