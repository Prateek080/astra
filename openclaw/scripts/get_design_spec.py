"""Get the design spec for a specific requirement."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def get_design_spec(
    req_id: str,
    project_dir: Path | None = None,
) -> str | None:
    """Read and return the D-R{n} design spec for a requirement."""
    project_dir = project_dir or Path.cwd()
    design_path = project_dir / "DESIGN_SPECS.md"

    if not design_path.is_file():
        print("Error: DESIGN_SPECS.md not found.")
        return None

    content = design_path.read_text(encoding="utf-8")
    num = re.search(r"\d+", req_id)
    dr_id = f"D-R{num.group()}" if num else f"D-{req_id}"

    pattern = re.compile(
        rf"^### {re.escape(dr_id)}:.*?(?=^### D-R\d+:|^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )

    match = pattern.search(content)
    if match:
        return match.group(0).strip()

    print(f"No design spec found for {dr_id}")
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Get design spec for a requirement")
    parser.add_argument("--id", required=True, help="Requirement ID (e.g., R1)")
    parser.add_argument("--project-dir", type=str, default=None)
    args = parser.parse_args()

    project_dir = Path(args.project_dir) if args.project_dir else None
    spec = get_design_spec(args.id, project_dir)
    if spec:
        print(spec)


if __name__ == "__main__":
    main()
