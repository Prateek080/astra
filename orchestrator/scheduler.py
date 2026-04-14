"""Scheduled task management — create, list, run tasks via crontab."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()

TASKS_DIR = Path.home() / ".astra" / "tasks"
TASKS_FILE = TASKS_DIR / "tasks.json"


def _load_tasks() -> list[dict]:
    if TASKS_FILE.is_file():
        return json.loads(TASKS_FILE.read_text())
    return []


def _save_tasks(tasks: list[dict]) -> None:
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))


def _get_astra_forge_path() -> str:
    """Get the path to astra-forge executable."""
    # Try to find it in PATH
    try:
        result = subprocess.run(["which", "astra-forge"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    # Fallback to python -m
    return f"{sys.executable} -m orchestrator"


def handle_schedule_command(args) -> None:
    """Handle `astra-forge schedule` subcommands."""
    action = getattr(args, "schedule_action", None)

    if action == "list":
        _list_tasks()
    elif action == "create":
        _create_task(args.task_name, args.cron)
    elif action == "run":
        _run_task(args.task_name)
    else:
        console.print("Usage: astra-forge schedule [list|create|run]")


def _list_tasks() -> None:
    tasks = _load_tasks()
    if not tasks:
        console.print("[dim]No scheduled tasks configured.[/]")
        console.print("[dim]Create one: astra-forge schedule create nightly-forge --cron '0 2 * * *'[/]")
        return

    table = Table(title="Scheduled Tasks")
    table.add_column("Name")
    table.add_column("Cron")
    table.add_column("Type")
    table.add_column("Status")

    for task in tasks:
        table.add_row(
            task["name"],
            task["cron"],
            task.get("type", "forge"),
            task.get("status", "active"),
        )

    console.print(table)


def _create_task(name: str, cron: str) -> None:
    tasks = _load_tasks()

    # Check for duplicates
    for t in tasks:
        if t["name"] == name:
            console.print(f"[yellow]Task '{name}' already exists. Updating cron.[/]")
            t["cron"] = cron
            _save_tasks(tasks)
            _install_cron(name, cron)
            return

    # Determine task type from name
    task_type = "forge"
    if "review" in name:
        task_type = "pr-review"
    elif "debt" in name:
        task_type = "debt-audit"

    task = {
        "name": name,
        "cron": cron,
        "type": task_type,
        "status": "active",
    }
    tasks.append(task)
    _save_tasks(tasks)
    _install_cron(name, cron)

    console.print(f"[green]✓[/] Task '{name}' created with schedule: {cron}")


def _install_cron(name: str, cron: str) -> None:
    """Install a crontab entry for the task."""
    astra_path = _get_astra_forge_path()
    cron_cmd = f'{cron} {astra_path} schedule run {name} >> ~/.astra/tasks/{name}.log 2>&1'
    cron_marker = f"# astra:{name}"

    try:
        # Read existing crontab
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        existing = result.stdout if result.returncode == 0 else ""

        # Remove old entry if exists
        lines = [l for l in existing.strip().split("\n") if cron_marker not in l and l.strip()]

        # Add new entry
        lines.append(f"{cron_cmd} {cron_marker}")

        # Install
        new_crontab = "\n".join(lines) + "\n"
        proc = subprocess.run(
            ["crontab", "-"],
            input=new_crontab,
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            console.print(f"  [dim]Cron installed: {cron} → astra-forge schedule run {name}[/]")
        else:
            console.print(f"  [yellow]Cron install failed: {proc.stderr}[/]")
    except Exception as e:
        console.print(f"  [yellow]Could not install cron: {e}[/]")
        console.print(f"  [dim]Manual: add to crontab: {cron_cmd}[/]")


def _run_task(name: str) -> None:
    """Run a scheduled task immediately."""
    tasks = _load_tasks()
    task = next((t for t in tasks if t["name"] == name), None)

    if not task:
        console.print(f"[red]Task '{name}' not found.[/]")
        return

    task_type = task.get("type", "forge")
    console.print(f"Running task: {name} (type: {task_type})")

    if task_type == "forge":
        from orchestrator.tasks.nightly_forge import run_nightly_forge

        import asyncio
        asyncio.run(run_nightly_forge())

    elif task_type == "pr-review":
        from orchestrator.tasks.pr_review import run_pr_review

        import asyncio
        asyncio.run(run_pr_review())

    elif task_type == "debt-audit":
        from orchestrator.tasks.debt_audit import run_debt_audit

        import asyncio
        asyncio.run(run_debt_audit())

    else:
        console.print(f"[red]Unknown task type: {task_type}[/]")
