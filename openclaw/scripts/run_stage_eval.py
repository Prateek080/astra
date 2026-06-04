"""Run stage-gate checks — wraps orchestrator/checks/*.py for OpenClaw.

Usage:
    python run_stage_eval.py --stage spec --feature "notifications" --project-dir .
    python run_stage_eval.py --stage design --project-dir .
    python run_stage_eval.py --stage plan --project-dir .
    python run_stage_eval.py --stage technical --project-dir .
    python run_stage_eval.py --stage phase --project-dir .

Outputs check results with pass/warn/fail per check.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path


def _ensure_orchestrator_on_path() -> None:
    """Add the Astra plugin directory to sys.path so orchestrator.checks is importable."""
    astra_dir = os.environ.get("ASTRA_PLUGIN_DIR")
    if astra_dir:
        sys.path.insert(0, astra_dir)
        return

    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "orchestrator" / "checks").is_dir():
            sys.path.insert(0, str(current))
            return
        current = current.parent

    home_astra = Path.home() / "astra"
    if (home_astra / "orchestrator" / "checks").is_dir():
        sys.path.insert(0, str(home_astra))


def run_checks(
    stage: str,
    project_dir: Path,
    feature: str = "",
    output_file: str | None = None,
) -> dict:
    """Run stage-gate checks and return results as dict."""
    _ensure_orchestrator_on_path()

    try:
        from orchestrator.checks.base import StageGateResult
    except ImportError:
        return {
            "stage": stage,
            "overall": "error",
            "error": "Could not import orchestrator.checks. Set ASTRA_PLUGIN_DIR or install astra.",
            "checks": [],
        }

    result: StageGateResult | None = None

    if stage == "spec":
        from orchestrator.checks.spec_checks import run_spec_checks
        spec_path = project_dir / "SPEC.md"
        if not spec_path.is_file():
            spec_path = project_dir / "REQUIREMENTS.md"
        result = run_spec_checks(feature, spec_path)

    elif stage == "design":
        from orchestrator.checks.design_checks import run_design_checks
        spec_path = project_dir / "SPEC.md"
        if not spec_path.is_file():
            spec_path = project_dir / "REQUIREMENTS.md"
        design_path = project_dir / "DESIGN.md"
        if not design_path.is_file():
            design_path = project_dir / "DESIGN_SPECS.md"
        result = run_design_checks(spec_path, design_path)

    elif stage == "plan":
        from orchestrator.checks.plan_checks import run_plan_checks
        spec_path = project_dir / "SPEC.md"
        if not spec_path.is_file():
            spec_path = project_dir / "REQUIREMENTS.md"
        plan_path = project_dir / "PLAN.md"
        result = run_plan_checks(spec_path, plan_path)

    elif stage == "technical":
        from orchestrator.checks.tech_checks import run_tech_checks
        spec_path = project_dir / "SPEC.md"
        if not spec_path.is_file():
            spec_path = project_dir / "REQUIREMENTS.md"
        tech_path = project_dir / "TECHNICAL.md"
        product_path = project_dir / "PRODUCT.md"
        result = run_tech_checks(spec_path, tech_path, product_path)

    elif stage == "phase":
        from orchestrator.checks.phase_checks import run_phase_checks
        spec_path = project_dir / "SPEC.md"
        if not spec_path.is_file():
            spec_path = project_dir / "REQUIREMENTS.md"
        result = asyncio.run(run_phase_checks(project_dir, spec_path))

    else:
        return {
            "stage": stage,
            "overall": "error",
            "error": f"Unknown stage: {stage}. Use: spec, design, plan, technical, phase",
            "checks": [],
        }

    if result is None:
        return {
            "stage": stage,
            "overall": "error",
            "error": f"No handler for stage: {stage}",
            "checks": [],
        }

    result_dict = result.to_dict()

    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result_dict, indent=2), encoding="utf-8")

    return result_dict


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Astra stage-gate checks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Stages:\n"
            "  spec       S1-S5: relevance, specificity, criteria, RICE, scope\n"
            "  design     D1-D5: R->D coverage, tokens, states, accessibility, orphans\n"
            "  plan       P1-P4: R->Phase coverage, test gates, task count, dependencies\n"
            "  technical  T1-T5: R->T coverage, API completeness, models, error codes, routes\n"
            "  phase      I1-I4: tests pass, lint, type-check, criteria spot-check\n"
        ),
    )
    parser.add_argument(
        "--stage", required=True,
        choices=["spec", "design", "plan", "technical", "phase"],
        help="Which stage gate to check",
    )
    parser.add_argument("--feature", default="", help="Feature description (for spec relevance check)")
    parser.add_argument("--project-dir", default=".", help="Project root directory")
    parser.add_argument("--output", default=None, help="Write results to this JSON file")
    parser.add_argument("--json", action="store_true", help="Output results as JSON to stdout")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    result = run_checks(args.stage, project_dir, args.feature, args.output)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        overall = result.get("overall", "unknown")
        checks = result.get("checks", [])
        icons = {"pass": "v", "warn": "!", "fail": "x", "error": "x"}

        print(f"\n{icons.get(overall, '?')} {result.get('stage', args.stage)}: {overall}")

        if result.get("error"):
            print(f"  Error: {result['error']}")

        for check in checks:
            icon = icons.get(check.get("status", ""), "?")
            line = f"  {icon} {check.get('id', '?')}: {check.get('name', '?')}"
            if check.get("reason"):
                line += f" -- {check['reason']}"
            print(line)

        print()
        passed = sum(1 for c in checks if c.get("status") == "pass")
        print(f"  {passed}/{len(checks)} pass")

    sys.exit(0 if result.get("overall") != "fail" else 1)


if __name__ == "__main__":
    main()
