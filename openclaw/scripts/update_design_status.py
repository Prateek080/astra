"""Update design status for a requirement in DESIGN_SPECS.md."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def update_design_status(
    req_id: str,
    status: str,
    project_dir: Path | None = None,
) -> None:
    """Mark a D-R{n} design spec with a new status."""
    project_dir = project_dir or Path.cwd()
    design_path = project_dir / "DESIGN_SPECS.md"

    if not design_path.is_file():
        print("Error: DESIGN_SPECS.md not found.")
        return

    content = design_path.read_text(encoding="utf-8")
    num = re.search(r"\d+", req_id)
    dr_id = f"D-R{num.group()}" if num else f"D-{req_id}"

    # Find the D-R section and update its status line (within 5 lines of heading)
    lines = content.split("\n")
    found = False
    for i, line in enumerate(lines):
        if line.startswith(f"### {dr_id}:"):
            for j in range(i + 1, min(i + 6, len(lines))):
                if "**Status:**" in lines[j]:
                    lines[j] = re.sub(r"(\*\*Status:\*\*\s*)\w+", rf"\g<1>{status}", lines[j])
                    found = True
                    break
            break

    if found:
        design_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Updated {dr_id} status to '{status}'")
    else:
        print(f"Error: {dr_id} not found in DESIGN_SPECS.md")

    # Also update REQUIREMENTS.md design status
    req_path = project_dir / "REQUIREMENTS.md"
    if req_path.is_file():
        req_lines = req_path.read_text(encoding="utf-8").split("\n")
        for i, line in enumerate(req_lines):
            if line.startswith(f"### {req_id}:"):
                for j in range(i + 1, min(i + 8, len(req_lines))):
                    if "**Design:**" in req_lines[j]:
                        req_lines[j] = re.sub(r"(\*\*Design:\*\*\s*)\w+", rf"\g<1>{status}", req_lines[j])
                        req_path.write_text("\n".join(req_lines), encoding="utf-8")
                        print(f"Updated {req_id} design status in REQUIREMENTS.md")
                        break
                break


def main() -> None:
    parser = argparse.ArgumentParser(description="Update design status for a requirement")
    parser.add_argument("--req-id", required=True, help="Requirement ID (e.g., R1)")
    parser.add_argument("--status", required=True, choices=["pending", "in_progress", "complete"])
    parser.add_argument("--project-dir", type=str, default=None)
    args = parser.parse_args()

    project_dir = Path(args.project_dir) if args.project_dir else None
    update_design_status(args.req_id, args.status, project_dir)


if __name__ == "__main__":
    main()
