"""Git automation tools — branch creation, phase commits, PR creation."""

from __future__ import annotations

import asyncio
import re
from pathlib import Path

from rich.console import Console

console = Console()


async def _run(cmd: str, cwd: Path) -> tuple[int, str]:
    """Run a git command."""
    proc = await asyncio.create_subprocess_shell(
        cmd,
        cwd=str(cwd),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    output = (stdout or b"").decode() + (stderr or b"").decode()
    return proc.returncode or 0, output.strip()


def _slugify(text: str) -> str:
    """Convert feature text to a branch-safe slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower().strip())
    return slug.strip("-")[:50]


async def create_feature_branch(feature: str, project_dir: Path, dry_run: bool = False) -> str:
    """Create a git branch for the feature."""
    slug = _slugify(feature)
    branch = f"feat/{slug}"

    if dry_run:
        console.print(f"  [dim]Dry run: would create branch '{branch}'[/]")
        return branch

    rc, _ = await _run(f"git checkout -b {branch}", project_dir)
    if rc != 0:
        # Branch might already exist
        rc, _ = await _run(f"git checkout {branch}", project_dir)

    console.print(f"  [green]✓[/] Branch: {branch}")
    return branch


async def commit_phase(
    phase_name: str,
    phase_number: int,
    project_dir: Path,
    dry_run: bool = False,
) -> bool:
    """Stage all changes and commit for a completed phase."""
    if dry_run:
        console.print(f"  [dim]Dry run: would commit Phase {phase_number}: {phase_name}[/]")
        return True

    # Stage all changes
    rc, _ = await _run("git add -A", project_dir)
    if rc != 0:
        return False

    # Check if there are staged changes
    rc, output = await _run("git diff --cached --stat", project_dir)
    if not output.strip():
        return True  # Nothing to commit

    # Commit
    msg = f"feat: implement {phase_name} (Phase {phase_number})"
    rc, _ = await _run(f'git commit -m "{msg}"', project_dir)
    if rc == 0:
        console.print(f"  [green]✓[/] Committed: {msg}")
    return rc == 0


async def create_pr(
    feature: str,
    spec_path: Path,
    project_dir: Path,
    dry_run: bool = False,
) -> str | None:
    """Create a pull request with R{n} checklist from SPEC.md."""
    # Parse requirements from spec
    checklist_items = []
    if spec_path.is_file():
        spec_text = spec_path.read_text(encoding="utf-8")
        req_pattern = re.compile(r"^###\s+(R\d+):\s*(.+)$", re.MULTILINE)
        for match in req_pattern.finditer(spec_text):
            checklist_items.append(f"- [ ] {match.group(1)}: {match.group(2).strip()}")

    checklist = "\n".join(checklist_items) if checklist_items else "- [ ] All requirements verified"

    title = f"feat: {feature}"
    if len(title) > 70:
        title = title[:67] + "..."

    body = f"""## Summary

Automated implementation via Astra Forge v2.

## Requirements Checklist

{checklist}

## Test Plan

- [ ] All tests pass
- [ ] Linter clean
- [ ] Type checker clean
- [ ] Acceptance criteria verified
"""

    if dry_run:
        console.print(f"  [dim]Dry run: would create PR '{title}'[/]")
        console.print(f"  [dim]  Checklist: {len(checklist_items)} requirements[/]")
        return None

    # Push current branch
    rc, output = await _run("git rev-parse --abbrev-ref HEAD", project_dir)
    branch = output.strip()
    await _run(f"git push -u origin {branch}", project_dir)

    # Create PR via gh CLI
    escaped_body = body.replace('"', '\\"').replace("\n", "\\n")
    rc, output = await _run(
        f'gh pr create --title "{title}" --body "{escaped_body}"',
        project_dir,
    )

    if rc == 0:
        pr_url = output.strip().split("\n")[-1]
        console.print(f"  [green]✓[/] PR created: {pr_url}")
        return pr_url
    else:
        console.print(f"  [yellow]PR creation failed: {output[:100]}[/]")
        return None
