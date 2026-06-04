"""Claim a requirement for implementation — marks it as in_progress."""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import re
from pathlib import Path


@contextlib.contextmanager
def _file_lock(file_path: Path):
    """Acquire an exclusive lock to prevent concurrent read-modify-write races."""
    lock_path = file_path.with_suffix(file_path.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_fd = open(lock_path, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        yield
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()


def claim_requirement(
    req_id: str,
    agent: str = "coder",
    session_id: str = "",
    project_dir: Path | None = None,
) -> bool:
    """Mark a requirement as in_progress and assign it to an agent (locked)."""
    project_dir = project_dir or Path.cwd()
    req_path = project_dir / "REQUIREMENTS.md"

    if not req_path.is_file():
        print("Error: REQUIREMENTS.md not found.")
        return False

    with _file_lock(req_path):
        return _claim_locked(req_id, agent, session_id, req_path)


def _claim_locked(req_id: str, agent: str, session_id: str, req_path: Path) -> bool:
    content = req_path.read_text(encoding="utf-8")

    # Verify requirement exists
    req_match = re.search(rf"^### {re.escape(req_id)}:", content, re.MULTILINE)
    if not req_match:
        print(f"Error: {req_id} not found in REQUIREMENTS.md")
        return False

    # Check current status
    start = req_match.start()
    next_req = re.search(r"^### R\d+:", content[req_match.end():], re.MULTILINE)
    end = req_match.end() + next_req.start() if next_req else len(content)
    section = content[start:end]

    status_match = re.search(r"\*\*Status:\*\*\s*(\w+)", section)
    current_status = status_match.group(1) if status_match else "pending"

    if current_status == "in_progress":
        print(f"Warning: {req_id} is already in_progress")
        return False
    if current_status in {"implemented", "verified"}:
        print(f"Warning: {req_id} is already {current_status}")
        return False

    # Update status to in_progress
    updated_section = re.sub(
        r"(\*\*Status:\*\*\s*)\w+", r"\g<1>in_progress", section
    )

    # Update assigned to
    assigned_value = f"{agent} ({session_id})" if session_id else agent
    updated_section = re.sub(
        r"(\*\*Assigned to:\*\*\s*).*$", rf"\g<1>{assigned_value}", updated_section, flags=re.MULTILINE
    )

    content = content[:start] + updated_section + content[end:]
    req_path.write_text(content, encoding="utf-8")
    print(f"Claimed {req_id} for {agent}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Claim a requirement for implementation")
    parser.add_argument("--id", required=True, help="Requirement ID (e.g., R1)")
    parser.add_argument("--agent", default="coder", help="Agent claiming the work")
    parser.add_argument("--session-id", default="", help="Agent session ID")
    parser.add_argument("--project-dir", type=str, default=None)
    args = parser.parse_args()

    project_dir = Path(args.project_dir) if args.project_dir else None
    claim_requirement(args.id, args.agent, args.session_id, project_dir)


if __name__ == "__main__":
    main()
