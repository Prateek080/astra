"""Initialize REQUIREMENTS.md from a feature description and template."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


def init_requirements(
    feature: str,
    pipeline_id: str,
    mode: str = "full",
    project_dir: Path | None = None,
    template_dir: Path | None = None,
) -> Path:
    """Create REQUIREMENTS.md from the template with placeholders filled."""
    project_dir = project_dir or Path.cwd()
    output_path = project_dir / "REQUIREMENTS.md"

    if output_path.exists():
        print(f"REQUIREMENTS.md already exists at {output_path}")
        return output_path

    if template_dir is None:
        template_dir = Path(__file__).resolve().parent.parent / "templates"

    template_path = template_dir / "REQUIREMENTS.template.md"
    if template_path.is_file():
        content = template_path.read_text(encoding="utf-8")
    else:
        content = _default_template()

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    content = content.replace("{{FEATURE_NAME}}", feature)
    content = content.replace("{{FEATURE_DESCRIPTION}}", feature)
    content = content.replace("{{TIMESTAMP}}", timestamp)
    content = content.replace("{{MODE}}", mode)
    content = content.replace("{{PIPELINE_ID}}", pipeline_id)

    output_path.write_text(content, encoding="utf-8")
    print(f"Created {output_path}")
    return output_path


def _default_template() -> str:
    return (
        "# Requirements: {{FEATURE_NAME}}\n\n"
        "**Generated:** {{TIMESTAMP}}\n"
        "**Mode:** {{MODE}}\n"
        "**Pipeline ID:** {{PIPELINE_ID}}\n\n"
        "---\n\n"
        "## Summary\n\n{{FEATURE_DESCRIPTION}}\n\n"
        "---\n\n"
        "## Requirements\n\n"
        "_No requirements yet. Use add_requirement.py to add._\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialize REQUIREMENTS.md from feature description",
    )
    parser.add_argument("--feature", required=True, help="Feature description")
    parser.add_argument("--pipeline-id", required=True, help="Pipeline ID")
    parser.add_argument("--mode", default="full", choices=["full", "lite"])
    parser.add_argument("--project-dir", type=str, default=None)
    parser.add_argument("--template-dir", type=str, default=None)
    args = parser.parse_args()

    project_dir = Path(args.project_dir) if args.project_dir else None
    template_dir = Path(args.template_dir) if args.template_dir else None
    init_requirements(args.feature, args.pipeline_id, args.mode, project_dir, template_dir)


if __name__ == "__main__":
    main()
