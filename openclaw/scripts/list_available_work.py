"""List requirements ready for implementation."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def list_available_work(project_dir: Path | None = None) -> list[dict]:
    """List requirements that are ready for implementation.

    A requirement is ready when:
    - Status is 'pending' or 'designed' or 'specced'
    - Not already 'in_progress' or 'implemented' or 'verified'
    - Design is 'complete' or N/A (backend-only)
    """
    project_dir = project_dir or Path.cwd()
    req_path = project_dir / "REQUIREMENTS.md"

    if not req_path.is_file():
        print("Error: REQUIREMENTS.md not found.")
        return []

    content = req_path.read_text(encoding="utf-8")
    req_pattern = re.compile(r"^### (R\d+):\s*(.+)$", re.MULTILINE)
    available = []

    for match in req_pattern.finditer(content):
        req_id = match.group(1)
        title = match.group(2).strip()

        start = match.start()
        next_match = req_pattern.search(content, match.end())
        end = next_match.start() if next_match else len(content)
        section = content[start:end]

        status_match = re.search(r"\*\*Status:\*\*\s*(\w+)", section)
        status = status_match.group(1) if status_match else "pending"

        design_match = re.search(r"\*\*Design:\*\*\s*(\w+)", section)
        design_status = design_match.group(1) if design_match else "pending"

        priority_match = re.search(r"\*\*Priority:\*\*\s*(.+?)$", section, re.MULTILINE)
        priority = priority_match.group(1).strip() if priority_match else "—"

        blocked_statuses = {"in_progress", "implemented", "verified"}
        if status in blocked_statuses:
            continue

        ready = True
        if design_status not in {"complete", "N/A", "pending"}:
            ready = True  # still show, but will be sorted lower

        available.append({
            "id": req_id,
            "title": title,
            "status": status,
            "design": design_status,
            "priority": priority,
            "ready": design_status in {"complete", "N/A"},
        })

    # Sort: design-complete first, then by requirement ID
    available.sort(key=lambda r: (not r["ready"], r["id"]))

    return available


def main() -> None:
    parser = argparse.ArgumentParser(description="List requirements ready for implementation")
    parser.add_argument("--project-dir", type=str, default=None)
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    project_dir = Path(args.project_dir) if args.project_dir else None
    work = list_available_work(project_dir)

    if args.json:
        import json
        print(json.dumps(work, indent=2))
    elif work:
        print(f"Available work ({len(work)} requirements):\n")
        for item in work:
            print(f"  {item['id']}: {item['title']}")
            print(f"    Status: {item['status']} | Design: {item['design']} | Priority: {item['priority']}")
            print()
    else:
        print("No available work. All requirements are in progress or complete.")


if __name__ == "__main__":
    main()
