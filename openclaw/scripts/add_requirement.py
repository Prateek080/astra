"""Add or update a requirement in REQUIREMENTS.md."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def add_requirement(
    req_id: str,
    title: str,
    priority: str = "P1",
    tier: str = "Now",
    criteria: str = "",
    rice: str = "",
    project_dir: Path | None = None,
) -> None:
    """Add a new requirement or update an existing one."""
    project_dir = project_dir or Path.cwd()
    req_path = project_dir / "REQUIREMENTS.md"

    if not req_path.is_file():
        print(f"Error: REQUIREMENTS.md not found. Run init_requirements.py first.")
        return

    content = req_path.read_text(encoding="utf-8")

    existing_pattern = re.compile(
        rf"^### {re.escape(req_id)}:.*?(?=^### R\d+:|^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )

    req_block = _build_requirement_block(req_id, title, priority, tier, criteria, rice)

    if existing_pattern.search(content):
        content = existing_pattern.sub(req_block, content)
        print(f"Updated {req_id} in REQUIREMENTS.md")
    else:
        insert_marker = "## Requirements\n"
        if insert_marker in content:
            # Find end of requirements section to append
            lines = content.split("\n")
            insert_idx = None
            in_requirements = False
            for i, line in enumerate(lines):
                if line.strip() == "## Requirements":
                    in_requirements = True
                    continue
                if in_requirements and line.startswith("## ") and not line.startswith("### R"):
                    insert_idx = i
                    break
            if insert_idx is None:
                insert_idx = len(lines)

            lines.insert(insert_idx, req_block)
            content = "\n".join(lines)
        else:
            content += f"\n{req_block}"

        print(f"Added {req_id} to REQUIREMENTS.md")

    req_path.write_text(content, encoding="utf-8")


def _build_requirement_block(
    req_id: str, title: str, priority: str, tier: str, criteria: str, rice: str
) -> str:
    parts = [
        f"### {req_id}: {title}",
        f"- **Status:** pending",
        f"- **Priority:** {priority} | {tier}",
    ]

    if rice:
        parts.append(f"- **RICE:** {rice}")
    else:
        parts.append(f"- **RICE:** Reach: _ | Impact: _ | Confidence: _ | Effort: _ | Score: _")

    parts.extend([
        "- **Assigned to:** —",
        "- **Design:** pending",
        "- **Technical:** pending",
        "",
        "#### Acceptance Criteria",
        "",
    ])

    if criteria:
        for line in criteria.strip().split("\n"):
            parts.append(f"- {line.strip()}")
    else:
        parts.extend([
            "- **Given** _precondition_",
            "- **When** _action_",
            "- **Then** _expected outcome_",
        ])

    parts.append("")
    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Add/update a requirement in REQUIREMENTS.md")
    parser.add_argument("--id", required=True, help="Requirement ID (e.g., R1)")
    parser.add_argument("--title", required=True, help="Requirement title")
    parser.add_argument("--priority", default="P1", help="Priority (P1, P2, P3)")
    parser.add_argument("--tier", default="Now", choices=["Now", "Next", "Later"])
    parser.add_argument("--criteria", default="", help="Acceptance criteria (Given/When/Then)")
    parser.add_argument("--rice", default="", help="RICE score string")
    parser.add_argument("--project-dir", type=str, default=None)
    args = parser.parse_args()

    project_dir = Path(args.project_dir) if args.project_dir else None
    add_requirement(args.id, args.title, args.priority, args.tier, args.criteria, args.rice, project_dir)


if __name__ == "__main__":
    main()
