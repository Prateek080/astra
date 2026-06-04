"""Mark a requirement as implemented."""

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


def complete_requirement(
    req_id: str,
    project_dir: Path | None = None,
) -> bool:
    """Mark a requirement as implemented in REQUIREMENTS.md (locked)."""
    project_dir = project_dir or Path.cwd()
    req_path = project_dir / "REQUIREMENTS.md"

    if not req_path.is_file():
        print("Error: REQUIREMENTS.md not found.")
        return False

    with _file_lock(req_path):
        return _complete_locked(req_id, req_path)


def _complete_locked(req_id: str, req_path: Path) -> bool:
    content = req_path.read_text(encoding="utf-8")

    req_match = re.search(rf"^### {re.escape(req_id)}:", content, re.MULTILINE)
    if not req_match:
        print(f"Error: {req_id} not found in REQUIREMENTS.md")
        return False

    start = req_match.start()
    next_req = re.search(r"^### R\d+:", content[req_match.end():], re.MULTILINE)
    end = req_match.end() + next_req.start() if next_req else len(content)
    section = content[start:end]

    updated_section = re.sub(
        r"(\*\*Status:\*\*\s*)\w+", r"\g<1>implemented", section
    )

    content = content[:start] + updated_section + content[end:]
    req_path.write_text(content, encoding="utf-8")
    print(f"Marked {req_id} as implemented")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Mark a requirement as implemented")
    parser.add_argument("--id", required=True, help="Requirement ID (e.g., R1)")
    parser.add_argument("--project-dir", type=str, default=None)
    args = parser.parse_args()

    project_dir = Path(args.project_dir) if args.project_dir else None
    complete_requirement(args.id, project_dir)


if __name__ == "__main__":
    main()
