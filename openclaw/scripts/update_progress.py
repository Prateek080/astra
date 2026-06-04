"""Pipeline state management for OpenClaw — adapts orchestrator/state.py."""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import json
import re
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = ".astra-state"
PROGRESS_FILE = "progress.json"
FORGE_STATE_FILE = "forge-state.json"

STAGE_ORDER_FULL = ["scan", "spec", "design", "plan", "architect", "implement", "review", "wrapup"]
STAGE_ORDER_LITE = ["scan", "spec", "plan", "implement", "review", "wrapup"]


def _state_path(project_dir: Path) -> Path:
    return project_dir / STATE_DIR / PROGRESS_FILE


def _forge_state_path(project_dir: Path) -> Path:
    return project_dir / STATE_DIR / FORGE_STATE_FILE


def _lock_path(file_path: Path) -> Path:
    return file_path.with_suffix(file_path.suffix + ".lock")


@contextlib.contextmanager
def _file_lock(file_path: Path):
    """Acquire an exclusive lock to prevent concurrent read-modify-write races."""
    lock_path = _lock_path(file_path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_fd = open(lock_path, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()


def load_state(project_dir: Path) -> dict:
    """Load pipeline state from progress.json."""
    path = _state_path(project_dir)
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "pipeline_id": None,
        "feature": None,
        "mode": "full",
        "current_stage": "idle",
        "stages": {},
        "started_at": None,
        "completed_at": None,
    }


def save_state(project_dir: Path, state: dict) -> None:
    """Save pipeline state to progress.json."""
    path = _state_path(project_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def init_pipeline(
    project_dir: Path,
    feature: str,
    mode: str = "full",
) -> dict:
    """Initialize a new pipeline run."""
    now = datetime.now(timezone.utc)
    pipeline_id = now.strftime("%Y%m%d-%H%M%S")

    stage_order = STAGE_ORDER_FULL if mode == "full" else STAGE_ORDER_LITE
    stages = {}
    for name in stage_order:
        stages[name] = {
            "status": "pending",
            "session_id": None,
            "artifact_path": None,
            "started_at": None,
            "completed_at": None,
            "retry_count": 0,
            "gate_result": None,
            "error": None,
        }

    state = {
        "pipeline_id": pipeline_id,
        "feature": feature,
        "mode": mode,
        "current_stage": "scan",
        "stages": stages,
        "started_at": now.isoformat(),
        "completed_at": None,
    }

    save_state(project_dir, state)
    print(f"Pipeline {pipeline_id} initialized for: {feature} ({mode} mode)")
    return state


def update_stage(
    project_dir: Path,
    stage: str,
    status: str,
    artifact: str | None = None,
    session_id: str | None = None,
    error: str | None = None,
    retry: bool = False,
) -> dict:
    """Update a stage's status in progress.json (locked)."""
    with _file_lock(_state_path(project_dir)):
        return _update_stage_locked(project_dir, stage, status, artifact, session_id, error, retry)


def _update_stage_locked(
    project_dir: Path,
    stage: str,
    status: str,
    artifact: str | None = None,
    session_id: str | None = None,
    error: str | None = None,
    retry: bool = False,
) -> dict:
    state = load_state(project_dir)
    now = datetime.now(timezone.utc).isoformat()

    if stage not in state["stages"]:
        state["stages"][stage] = {
            "status": "pending",
            "session_id": None,
            "artifact_path": None,
            "started_at": None,
            "completed_at": None,
            "retry_count": 0,
            "gate_result": None,
            "error": None,
        }

    record = state["stages"][stage]

    if retry:
        record["retry_count"] = record.get("retry_count", 0) + 1

    record["status"] = status

    if status == "in_progress":
        record["started_at"] = now
        state["current_stage"] = stage
    elif status == "complete":
        record["completed_at"] = now
        if artifact:
            record["artifact_path"] = artifact
        if session_id:
            record["session_id"] = session_id
    elif status == "failed":
        record["completed_at"] = now
        if error:
            record["error"] = error

    save_state(project_dir, state)
    print(f"Stage '{stage}' → {status}")
    return state


def record_gate(project_dir: Path, stage: str, gate_result: dict) -> None:
    """Record a stage-gate check result (locked)."""
    with _file_lock(_state_path(project_dir)):
        state = load_state(project_dir)
        if stage in state["stages"]:
            state["stages"][stage]["gate_result"] = gate_result
            save_state(project_dir, state)
            print(f"Gate result recorded for '{stage}': {gate_result.get('overall', 'unknown')}")


def detect_mode(project_dir: Path, spec_file: str = "REQUIREMENTS.md") -> str:
    """Detect full vs lite mode from spec content."""
    spec_path = project_dir / spec_file
    if not spec_path.is_file():
        return "full"

    spec_text = spec_path.read_text(encoding="utf-8")
    req_pattern = re.compile(r"^###\s+R\d+:", re.MULTILINE)
    req_count = len(req_pattern.findall(spec_text))

    has_frontend = bool(re.search(r"UI|component|page|frontend|button|form|display", spec_text, re.IGNORECASE))
    has_backend = bool(re.search(r"\bAPI\b|\bendpoint\b|\bdatabase\b|\bmigration\b|\bbackend\b", spec_text, re.IGNORECASE))
    is_mixed = has_frontend and has_backend

    mode = "lite" if req_count <= 3 and not is_mixed else "full"

    state = load_state(project_dir)
    if state["mode"] != mode:
        state["mode"] = mode
        stage_order = STAGE_ORDER_FULL if mode == "full" else STAGE_ORDER_LITE
        for name in stage_order:
            if name not in state["stages"]:
                state["stages"][name] = {
                    "status": "pending",
                    "session_id": None,
                    "artifact_path": None,
                    "started_at": None,
                    "completed_at": None,
                    "retry_count": 0,
                    "gate_result": None,
                    "error": None,
                }
        save_state(project_dir, state)

    print(f"Mode detected: {mode} ({req_count} requirements, mixed={is_mixed})")
    return mode


def reset_idle(project_dir: Path) -> None:
    """Reset pipeline to idle state after completion (locked)."""
    with _file_lock(_state_path(project_dir)):
        state = load_state(project_dir)
        state["current_stage"] = "idle"
        state["completed_at"] = datetime.now(timezone.utc).isoformat()
        save_state(project_dir, state)
        print("Pipeline reset to idle")


def save_summary(project_dir: Path, stage: str, summary: str) -> None:
    """Save a lean summary for a stage to forge-state.json."""
    path = _forge_state_path(project_dir)
    path.parent.mkdir(parents=True, exist_ok=True)

    data = {}
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))

    data[stage] = summary
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_status(project_dir: Path) -> dict:
    """Get current pipeline status."""
    return load_state(project_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage Astra pipeline state")
    parser.add_argument(
        "--action",
        choices=["init", "update", "gate", "detect-mode", "reset-idle", "summary", "status"],
        default="update",
        help="Action to perform",
    )
    parser.add_argument("--feature", default="", help="Feature description (for init)")
    parser.add_argument("--mode", default="full", choices=["full", "lite"])
    parser.add_argument("--stage", default="", help="Stage name")
    parser.add_argument("--status", default="", help="New status")
    parser.add_argument("--artifact", default=None, help="Artifact path")
    parser.add_argument("--session-id", default=None, help="Agent session ID")
    parser.add_argument("--error", default=None, help="Error message")
    parser.add_argument("--retry", action="store_true", help="Increment retry count")
    parser.add_argument("--gate-result", default=None, help="Gate result JSON string")
    parser.add_argument("--summary-text", default="", help="Stage summary text")
    parser.add_argument("--spec", default="REQUIREMENTS.md", help="Spec file for mode detection")
    parser.add_argument("--project-dir", default=".", help="Project root directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()

    if args.action == "init":
        result = init_pipeline(project_dir, args.feature, args.mode)
        if args.json:
            print(json.dumps(result, indent=2))

    elif args.action == "update":
        if not args.stage or not args.status:
            parser.error("--stage and --status required for update")
        result = update_stage(
            project_dir, args.stage, args.status,
            args.artifact, args.session_id, args.error, args.retry,
        )
        if args.json:
            print(json.dumps(result, indent=2))

    elif args.action == "gate":
        if not args.stage or not args.gate_result:
            parser.error("--stage and --gate-result required for gate")
        gate_data = json.loads(args.gate_result)
        record_gate(project_dir, args.stage, gate_data)

    elif args.action == "detect-mode":
        mode = detect_mode(project_dir, args.spec)
        if args.json:
            print(json.dumps({"mode": mode}))

    elif args.action == "reset-idle":
        reset_idle(project_dir)

    elif args.action == "summary":
        if not args.stage or not args.summary_text:
            parser.error("--stage and --summary-text required for summary")
        save_summary(project_dir, args.stage, args.summary_text)

    elif args.action == "status":
        result = get_status(project_dir)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Pipeline: {result.get('pipeline_id', 'none')}")
            print(f"Feature: {result.get('feature', 'none')}")
            print(f"Mode: {result.get('mode', 'unknown')}")
            print(f"Current stage: {result.get('current_stage', 'idle')}")
            print()
            for name, record in result.get("stages", {}).items():
                status = record.get("status", "unknown")
                icons = {"pending": ".", "in_progress": ">", "complete": "v", "failed": "x", "skipped": "-"}
                icon = icons.get(status, "?")
                line = f"  {icon} {name}: {status}"
                if record.get("artifact_path"):
                    line += f" ({record['artifact_path']})"
                if record.get("error"):
                    line += f" ERROR: {record['error']}"
                print(line)


if __name__ == "__main__":
    main()
