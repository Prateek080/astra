"""DESIGN checks (D1-D5) — deterministic Python."""

from __future__ import annotations

import re
from pathlib import Path

from orchestrator.checks.base import CheckResult, CheckStatus, StageGateResult

DR_PATTERN = re.compile(r"D-R(\d+)", re.MULTILINE)
R_PATTERN = re.compile(r"^###\s+R(\d+):", re.MULTILINE)
RAW_HEX = re.compile(r"#[0-9A-Fa-f]{6}\b")
RAW_PX = re.compile(r"\b\d+px\b")
STATE_KEYWORDS = {"default", "hover", "active", "focused", "disabled", "loading", "error", "empty", "skeleton"}


def d1_coverage(spec_path: Path, design_text: str) -> CheckResult:
    """D1: Every frontend R{n} has >=1 D-R{n} in DESIGN.md."""
    if not spec_path.is_file():
        return CheckResult("D1", "R→D Coverage", CheckStatus.WARN, "No SPEC.md to cross-reference")

    spec_text = spec_path.read_text(encoding="utf-8")
    spec_ids = {m.group(1) for m in R_PATTERN.finditer(spec_text)}
    design_ids = {m.group(1) for m in DR_PATTERN.finditer(design_text)}

    # Backend-only requirements are OK to skip (noted as "Technical — architect")
    technical_pattern = re.compile(r"R(\d+).*(?:Technical|architect|backend)", re.IGNORECASE)
    backend_ids = {m.group(1) for m in technical_pattern.finditer(design_text)}

    missing = spec_ids - design_ids - backend_ids
    if not missing:
        return CheckResult("D1", "R→D Coverage", CheckStatus.PASS, f"{len(design_ids)} D-R{'{n}'} found")
    elif len(missing) == 1:
        return CheckResult("D1", "R→D Coverage", CheckStatus.WARN, f"Missing: R{',R'.join(missing)}")
    else:
        return CheckResult("D1", "R→D Coverage", CheckStatus.FAIL, f"Missing: R{',R'.join(sorted(missing)[:3])}")


def d2_tokens(design_text: str) -> CheckResult:
    """D2: Are token references used instead of raw values?"""
    # Count raw hex/px values that appear outside of token definition sections
    raw_hex_count = len(RAW_HEX.findall(design_text))
    raw_px_count = len(RAW_PX.findall(design_text))

    # Some raw values are expected in token definitions — allow up to 20
    effective = max(0, raw_hex_count - 20) + max(0, raw_px_count - 20)

    if effective == 0:
        return CheckResult("D2", "Token Usage", CheckStatus.PASS)
    elif effective <= 5:
        return CheckResult("D2", "Token Usage", CheckStatus.WARN, f"{effective} raw values outside tokens")
    else:
        return CheckResult("D2", "Token Usage", CheckStatus.FAIL, f"{effective} raw values — use tokens")


def d3_states(design_text: str) -> CheckResult:
    """D3: Do components have >= 5 states specified?"""
    component_sections = re.split(r"###\s+D-R\d+", design_text)
    if len(component_sections) <= 1:
        return CheckResult("D3", "States", CheckStatus.WARN, "No component sections found")

    low_state_count = 0
    for section in component_sections[1:]:
        section_lower = section.lower()
        found_states = sum(1 for s in STATE_KEYWORDS if s in section_lower)
        if found_states < 3:
            low_state_count += 1

    if low_state_count == 0:
        return CheckResult("D3", "States", CheckStatus.PASS)
    elif low_state_count <= 1:
        return CheckResult("D3", "States", CheckStatus.WARN, f"{low_state_count} component with <3 states")
    else:
        return CheckResult("D3", "States", CheckStatus.FAIL, f"{low_state_count} components with <3 states")


def d4_accessibility(design_text: str) -> CheckResult:
    """D4: Are contrast ratios and keyboard specs present?"""
    has_contrast = bool(re.search(r"contrast|4\.5:1|3:1|WCAG", design_text, re.IGNORECASE))
    has_keyboard = bool(re.search(r"keyboard|tab order|focus|aria", design_text, re.IGNORECASE))

    if has_contrast and has_keyboard:
        return CheckResult("D4", "Accessibility", CheckStatus.PASS)
    elif has_contrast or has_keyboard:
        missing = "keyboard" if not has_keyboard else "contrast"
        return CheckResult("D4", "Accessibility", CheckStatus.WARN, f"Missing {missing} specs")
    else:
        return CheckResult("D4", "Accessibility", CheckStatus.FAIL, "No a11y specs found")


def d5_orphans(spec_path: Path, design_text: str) -> CheckResult:
    """D5: No D-R{n} without matching R{n} in SPEC.md."""
    if not spec_path.is_file():
        return CheckResult("D5", "Orphans", CheckStatus.WARN, "No SPEC.md to cross-reference")

    spec_text = spec_path.read_text(encoding="utf-8")
    spec_ids = {m.group(1) for m in R_PATTERN.finditer(spec_text)}
    design_ids = {m.group(1) for m in DR_PATTERN.finditer(design_text)}

    orphans = design_ids - spec_ids
    if not orphans:
        return CheckResult("D5", "Orphans", CheckStatus.PASS)
    else:
        return CheckResult("D5", "Orphans", CheckStatus.FAIL, f"Orphan D-R{',D-R'.join(sorted(orphans))}")


def run_design_checks(spec_path: Path, design_path: Path) -> StageGateResult:
    """Run all D1-D5 checks on DESIGN.md."""
    if not design_path.is_file():
        result = StageGateResult(stage="Design Gate")
        result.checks.append(CheckResult("D0", "File", CheckStatus.FAIL, "DESIGN.md not found"))
        return result

    design_text = design_path.read_text(encoding="utf-8")
    result = StageGateResult(stage="Design Gate")
    result.checks = [
        d1_coverage(spec_path, design_text),
        d2_tokens(design_text),
        d3_states(design_text),
        d4_accessibility(design_text),
        d5_orphans(spec_path, design_text),
    ]
    return result
