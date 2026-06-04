"""Generate PRD.md summary from REQUIREMENTS.md."""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path


def generate_summary(project_dir: Path | None = None) -> Path:
    """Read REQUIREMENTS.md and produce a PRD.md narrative summary."""
    project_dir = project_dir or Path.cwd()
    req_path = project_dir / "REQUIREMENTS.md"
    prd_path = project_dir / "PRD.md"

    if not req_path.is_file():
        print("Error: REQUIREMENTS.md not found.")
        return prd_path

    content = req_path.read_text(encoding="utf-8")

    title_match = re.search(r"^# Requirements:\s*(.+)$", content, re.MULTILINE)
    feature_name = title_match.group(1).strip() if title_match else "Unknown Feature"

    summary_match = re.search(
        r"## Summary\s*\n\n(.+?)(?=\n---|\n## )", content, re.DOTALL
    )
    summary = summary_match.group(1).strip() if summary_match else ""

    req_pattern = re.compile(r"^### (R\d+):\s*(.+)$", re.MULTILINE)
    requirements = []
    for match in req_pattern.finditer(content):
        req_id = match.group(1)
        title = match.group(2).strip()

        start = match.start()
        next_match = req_pattern.search(content, match.end())
        end = next_match.start() if next_match else len(content)
        section = content[start:end]

        status_match = re.search(r"\*\*Status:\*\*\s*(\w+)", section)
        priority_match = re.search(r"\*\*Priority:\*\*\s*(.+?)$", section, re.MULTILINE)

        requirements.append({
            "id": req_id,
            "title": title,
            "status": status_match.group(1) if status_match else "pending",
            "priority": priority_match.group(1).strip() if priority_match else "—",
        })

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    def _classify_tier(priority: str) -> str:
        p = priority.strip()
        if p.startswith("P1") or "| Now" in p or p == "Now":
            return "now"
        if p.startswith("P2") or "| Next" in p or p == "Next":
            return "next"
        if p.startswith("P3") or "| Later" in p or p == "Later":
            return "later"
        return "now"

    now_reqs = [r for r in requirements if _classify_tier(r["priority"]) == "now"]
    next_reqs = [r for r in requirements if _classify_tier(r["priority"]) == "next"]
    later_reqs = [r for r in requirements if _classify_tier(r["priority"]) == "later"]

    prd_lines = [
        f"# PRD: {feature_name}",
        f"",
        f"**Generated:** {timestamp}",
        f"**Source:** REQUIREMENTS.md",
        f"**Total Requirements:** {len(requirements)}",
        f"",
        f"---",
        f"",
        f"## Overview",
        f"",
        f"{summary}" if summary else "_No summary available._",
        f"",
        f"---",
        f"",
        f"## Requirements Summary",
        f"",
        f"| ID | Title | Priority | Status |",
        f"|-----|-------|----------|--------|",
    ]

    for r in requirements:
        prd_lines.append(f"| {r['id']} | {r['title']} | {r['priority']} | {r['status']} |")

    prd_lines.extend([
        "",
        "---",
        "",
        "## Scope",
        "",
        f"### Now ({len(now_reqs)} requirements)",
    ])
    for r in now_reqs:
        prd_lines.append(f"- {r['id']}: {r['title']}")

    prd_lines.append(f"\n### Next ({len(next_reqs)} requirements)")
    for r in next_reqs:
        prd_lines.append(f"- {r['id']}: {r['title']}")

    prd_lines.append(f"\n### Later ({len(later_reqs)} requirements)")
    for r in later_reqs:
        prd_lines.append(f"- {r['id']}: {r['title']}")

    prd_lines.append("")
    prd_path.write_text("\n".join(prd_lines), encoding="utf-8")
    print(f"Generated {prd_path}")
    return prd_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate PRD.md from REQUIREMENTS.md")
    parser.add_argument("--project-dir", type=str, default=None)
    args = parser.parse_args()

    project_dir = Path(args.project_dir) if args.project_dir else None
    generate_summary(project_dir)


if __name__ == "__main__":
    main()
