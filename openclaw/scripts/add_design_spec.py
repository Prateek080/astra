"""Add a UI design spec for a requirement to DESIGN_SPECS.md."""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path


def add_design_spec(
    req_id: str,
    component: str,
    spec: str,
    project_dir: Path | None = None,
    template_dir: Path | None = None,
) -> None:
    """Add a D-R{n} design spec to DESIGN_SPECS.md."""
    project_dir = project_dir or Path.cwd()
    design_path = project_dir / "DESIGN_SPECS.md"

    if not design_path.is_file():
        _create_design_specs(design_path, project_dir, template_dir)

    content = design_path.read_text(encoding="utf-8")

    num = re.search(r"\d+", req_id)
    dr_id = f"D-R{num.group()}" if num else f"D-{req_id}"

    existing = re.search(
        rf"^### {re.escape(dr_id)}:.*?(?=^### D-R\d+:|^## |\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    )

    spec_block = f"### {dr_id}: {component}\n- **Requirement:** {req_id}\n- **Status:** pending\n\n{spec}\n\n"

    if existing:
        content = content[: existing.start()] + spec_block + content[existing.end() :]
        print(f"Updated {dr_id} in DESIGN_SPECS.md")
    else:
        marker = "## Component Specifications"
        if marker in content:
            idx = content.index(marker) + len(marker)
            content = content[:idx] + "\n\n" + spec_block + content[idx:]
        else:
            content += f"\n## Component Specifications\n\n{spec_block}"
        print(f"Added {dr_id} to DESIGN_SPECS.md")

    design_path.write_text(content, encoding="utf-8")


def _create_design_specs(
    design_path: Path, project_dir: Path, template_dir: Path | None
) -> None:
    if template_dir is None:
        template_dir = Path(__file__).resolve().parent.parent / "templates"

    template_path = template_dir / "DESIGN_SPECS.template.md"
    if template_path.is_file():
        content = template_path.read_text(encoding="utf-8")
    else:
        content = (
            "# Design Specs\n\n"
            "---\n\n"
            "## Component Specifications\n\n"
        )

    req_path = project_dir / "REQUIREMENTS.md"
    if req_path.is_file():
        title_match = re.search(
            r"^# Requirements:\s*(.+)$",
            req_path.read_text(encoding="utf-8"),
            re.MULTILINE,
        )
        if title_match:
            content = content.replace("{{FEATURE_NAME}}", title_match.group(1).strip())

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    content = content.replace("{{TIMESTAMP}}", timestamp)

    # Try to read pipeline_id from progress.json
    progress_path = project_dir / ".astra-state" / "progress.json"
    pipeline_id = ""
    if progress_path.is_file():
        import json
        try:
            state = json.loads(progress_path.read_text(encoding="utf-8"))
            pipeline_id = state.get("pipeline_id", "")
        except (json.JSONDecodeError, KeyError):
            pass
    content = content.replace("{{PIPELINE_ID}}", pipeline_id or "unknown")

    design_path.write_text(content, encoding="utf-8")
    print(f"Created {design_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Add design spec for a requirement")
    parser.add_argument("--req-id", required=True, help="Requirement ID (e.g., R1)")
    parser.add_argument("--component", required=True, help="Component name")
    parser.add_argument("--spec", required=True, help="Design spec content")
    parser.add_argument("--project-dir", type=str, default=None)
    parser.add_argument("--template-dir", type=str, default=None)
    args = parser.parse_args()

    project_dir = Path(args.project_dir) if args.project_dir else None
    template_dir = Path(args.template_dir) if args.template_dir else None
    add_design_spec(args.req_id, args.component, args.spec, project_dir, template_dir)


if __name__ == "__main__":
    main()
