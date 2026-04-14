"""CLI entry point for astra-forge."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from rich.console import Console

from orchestrator import __version__

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="astra-forge",
        description="Astra v2 — Agent SDK orchestrator for the development lifecycle pipeline.",
    )
    parser.add_argument("--version", action="version", version=f"astra-forge {__version__}")

    sub = parser.add_subparsers(dest="command")

    # --- forge (default) ---
    forge = sub.add_parser("forge", help="Run the full development pipeline")
    forge.add_argument("feature", help="Feature description to build")
    forge.add_argument("--lite", action="store_true", help="Force lite mode (skip design+architect)")
    forge.add_argument(
        "--interactive", action="store_true", help="Add manual approval gates between stages"
    )
    forge.add_argument("--resume", type=str, default=None, help="Resume from pipeline state ID")
    forge.add_argument(
        "--dry-run", action="store_true", help="Simulate git/slack actions without executing"
    )
    forge.add_argument(
        "--project-dir",
        type=str,
        default=None,
        help="Project directory (defaults to cwd)",
    )

    # --- schedule ---
    sched = sub.add_parser("schedule", help="Manage scheduled tasks")
    sched_sub = sched.add_subparsers(dest="schedule_action")

    sched_sub.add_parser("list", help="List scheduled tasks")

    sched_create = sched_sub.add_parser("create", help="Create a scheduled task")
    sched_create.add_argument("task_name", help="Task name (e.g., nightly-forge)")
    sched_create.add_argument("--cron", required=True, help="Cron expression")

    sched_run = sched_sub.add_parser("run", help="Run a scheduled task now")
    sched_run.add_argument("task_name", help="Task name to run")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        # If bare `astra-forge "feature text"` — treat as forge
        if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
            args.command = "forge"
            args.feature = sys.argv[1]
            args.lite = "--lite" in sys.argv
            args.interactive = "--interactive" in sys.argv
            args.resume = None
            args.dry_run = "--dry-run" in sys.argv
            args.project_dir = None
        else:
            parser.print_help()
            sys.exit(0)

    if args.command == "forge":
        from orchestrator.config import AstraConfig
        from orchestrator.pipeline import run_pipeline

        project_dir = Path(args.project_dir) if args.project_dir else Path.cwd()
        config = AstraConfig.load(
            project_dir=project_dir,
            lite=args.lite,
            interactive=args.interactive,
            dry_run=args.dry_run,
        )
        asyncio.run(run_pipeline(config=config, feature=args.feature, resume_id=args.resume))

    elif args.command == "schedule":
        from orchestrator.scheduler import handle_schedule_command

        handle_schedule_command(args)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
