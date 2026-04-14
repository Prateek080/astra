"""PLAN checks (P1-P4) — deterministic Python."""

from __future__ import annotations

import re
from pathlib import Path

from orchestrator.checks.base import CheckResult, CheckStatus, StageGateResult

R_PATTERN = re.compile(r"\bR(\d+)\b")
PHASE_PATTERN = re.compile(r"^##\s+Phase\s+(\d+)", re.MULTILINE | re.IGNORECASE)
TEST_GATE_PATTERN = re.compile(r"\*\*Test gate\*\*|test gate:", re.IGNORECASE)
TASKS_PATTERN = re.compile(r"^[-*]\s+", re.MULTILINE)


def _extract_phases(plan_text: str) -> list[tuple[str, str]]:
    """Extract (phase_number, phase_text) pairs."""
    matches = list(PHASE_PATTERN.finditer(plan_text))
    phases = []
    for i, match in enumerate(matches):
        num = match.group(1)
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(plan_text)
        phases.append((num, plan_text[start:end]))
    return phases


def p1_coverage(spec_path: Path, plan_text: str) -> CheckResult:
    """P1: Every R{n} appears in at least one phase."""
    if not spec_path.is_file():
        return CheckResult("P1", "R→Phase Coverage", CheckStatus.WARN, "No SPEC.md")

    spec_text = spec_path.read_text(encoding="utf-8")
    spec_req_pattern = re.compile(r"^###\s+R(\d+):", re.MULTILINE)
    spec_ids = {m.group(1) for m in spec_req_pattern.finditer(spec_text)}
    plan_ids = {m.group(1) for m in R_PATTERN.finditer(plan_text)}

    missing = spec_ids - plan_ids
    if not missing:
        return CheckResult("P1", "R→Phase Coverage", CheckStatus.PASS, f"{len(plan_ids)} R{{n}} referenced")
    elif len(missing) == 1:
        return CheckResult("P1", "R→Phase Coverage", CheckStatus.WARN, f"Missing: R{',R'.join(missing)}")
    else:
        return CheckResult("P1", "R→Phase Coverage", CheckStatus.FAIL, f"Missing: R{',R'.join(sorted(missing)[:3])}")


def p2_test_gates(plan_text: str) -> CheckResult:
    """P2: Every phase has a test gate."""
    phases = _extract_phases(plan_text)
    if not phases:
        return CheckResult("P2", "Test Gates", CheckStatus.FAIL, "No phases found")

    missing_gates = []
    for num, text in phases:
        if not TEST_GATE_PATTERN.search(text):
            missing_gates.append(num)

    if not missing_gates:
        return CheckResult("P2", "Test Gates", CheckStatus.PASS, f"{len(phases)} phases with gates")
    elif len(missing_gates) == 1:
        return CheckResult("P2", "Test Gates", CheckStatus.WARN, f"Phase {missing_gates[0]} missing gate")
    else:
        return CheckResult("P2", "Test Gates", CheckStatus.FAIL, f"Phases {','.join(missing_gates)} missing gates")


def p3_task_count(plan_text: str) -> CheckResult:
    """P3: Phases have 1-8 tasks (not too many)."""
    phases = _extract_phases(plan_text)
    if not phases:
        return CheckResult("P3", "Task Count", CheckStatus.FAIL, "No phases found")

    oversized = []
    for num, text in phases:
        task_count = len(TASKS_PATTERN.findall(text))
        if task_count > 12:
            oversized.append(f"Phase {num} ({task_count})")

    if not oversized:
        return CheckResult("P3", "Task Count", CheckStatus.PASS)
    elif len(oversized) == 1 and all("9" in o or "10" in o or "11" in o or "12" in o for o in oversized):
        return CheckResult("P3", "Task Count", CheckStatus.WARN, f"{oversized[0]} is large")
    else:
        return CheckResult("P3", "Task Count", CheckStatus.FAIL, f"Too many tasks: {', '.join(oversized)}")


def p4_dependencies(plan_text: str) -> CheckResult:
    """P4: Phase order makes sense (data before UI, generally)."""
    phases = _extract_phases(plan_text)
    if len(phases) < 2:
        return CheckResult("P4", "Dependencies", CheckStatus.PASS, "Single phase")

    data_keywords = {"model", "schema", "migration", "database", "table", "prisma", "drizzle"}
    ui_keywords = {"component", "page", "layout", "css", "style", "frontend", "ui"}

    first_data_phase = None
    first_ui_phase = None

    for num, text in phases:
        text_lower = text.lower()
        if any(kw in text_lower for kw in data_keywords) and first_data_phase is None:
            first_data_phase = int(num)
        if any(kw in text_lower for kw in ui_keywords) and first_ui_phase is None:
            first_ui_phase = int(num)

    if first_data_phase and first_ui_phase and first_ui_phase < first_data_phase:
        return CheckResult("P4", "Dependencies", CheckStatus.WARN, "UI phase before data phase")

    return CheckResult("P4", "Dependencies", CheckStatus.PASS)


def run_plan_checks(spec_path: Path, plan_path: Path) -> StageGateResult:
    """Run all P1-P4 checks."""
    if not plan_path.is_file():
        result = StageGateResult(stage="Plan Gate")
        result.checks.append(CheckResult("P0", "File", CheckStatus.FAIL, "PLAN.md not found"))
        return result

    plan_text = plan_path.read_text(encoding="utf-8")
    result = StageGateResult(stage="Plan Gate")
    result.checks = [
        p1_coverage(spec_path, plan_text),
        p2_test_gates(plan_text),
        p3_task_count(plan_text),
        p4_dependencies(plan_text),
    ]
    return result
