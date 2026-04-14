"""TECHNICAL checks (T1-T5) — deterministic Python."""

from __future__ import annotations

import re
from pathlib import Path

from orchestrator.checks.base import CheckResult, CheckStatus, StageGateResult

TR_PATTERN = re.compile(r"T-R(\d+)", re.MULTILINE)
R_PATTERN = re.compile(r"^###\s+R(\d+):", re.MULTILINE)
ENDPOINT_PATTERN = re.compile(r"\*\*(?:Method|Path)\*\*|(?:GET|POST|PUT|PATCH|DELETE)\s+/", re.MULTILINE)
REQUEST_PATTERN = re.compile(r"\*\*Request\*\*|request.*schema|request.*body", re.IGNORECASE)
RESPONSE_PATTERN = re.compile(r"\*\*Response\*\*|response.*schema|response.*success", re.IGNORECASE)
FIELD_TYPE_PATTERN = re.compile(r"(?:varchar|integer|uuid|text|boolean|timestamp|jsonb|string|number|int)\b", re.IGNORECASE)
ERROR_CODE_PATTERN = re.compile(r"[A-Z_]+_[A-Z_]+|`[A-Z_]+`")


def t1_coverage(spec_path: Path, tech_text: str) -> CheckResult:
    """T1: Every backend R{n} has >=1 T-R{n}."""
    if not spec_path.is_file():
        return CheckResult("T1", "R→T Coverage", CheckStatus.WARN, "No SPEC.md")

    spec_text = spec_path.read_text(encoding="utf-8")
    spec_ids = {m.group(1) for m in R_PATTERN.finditer(spec_text)}
    tech_ids = {m.group(1) for m in TR_PATTERN.finditer(tech_text)}

    # UI-only requirements (noted in DESIGN.md) are OK to skip
    ui_pattern = re.compile(r"R(\d+).*(?:UI|designer|frontend)", re.IGNORECASE)
    ui_ids = {m.group(1) for m in ui_pattern.finditer(tech_text)}

    missing = spec_ids - tech_ids - ui_ids
    if not missing:
        return CheckResult("T1", "R→T Coverage", CheckStatus.PASS, f"{len(tech_ids)} T-R{{n}} found")
    elif len(missing) == 1:
        return CheckResult("T1", "R→T Coverage", CheckStatus.WARN, f"Missing: R{',R'.join(missing)}")
    else:
        return CheckResult("T1", "R→T Coverage", CheckStatus.FAIL, f"Missing: R{',R'.join(sorted(missing)[:3])}")


def t2_api_completeness(tech_text: str) -> CheckResult:
    """T2: API endpoints have request + response schemas."""
    endpoints = list(ENDPOINT_PATTERN.finditer(tech_text))
    if not endpoints:
        return CheckResult("T2", "API Completeness", CheckStatus.WARN, "No API endpoints found")

    has_request = bool(REQUEST_PATTERN.search(tech_text))
    has_response = bool(RESPONSE_PATTERN.search(tech_text))

    if has_request and has_response:
        return CheckResult("T2", "API Completeness", CheckStatus.PASS, f"{len(endpoints)} endpoints")
    elif has_request or has_response:
        missing = "response" if not has_response else "request"
        return CheckResult("T2", "API Completeness", CheckStatus.WARN, f"Missing {missing} schemas")
    else:
        return CheckResult("T2", "API Completeness", CheckStatus.FAIL, "No request/response schemas")


def t3_data_models(tech_text: str) -> CheckResult:
    """T3: Data models have field types and constraints."""
    has_fields = bool(FIELD_TYPE_PATTERN.search(tech_text))
    has_constraints = bool(re.search(r"NOT NULL|UNIQUE|PRIMARY|FK|foreign key|required|optional", tech_text, re.IGNORECASE))

    if has_fields and has_constraints:
        return CheckResult("T3", "Data Models", CheckStatus.PASS)
    elif has_fields:
        return CheckResult("T3", "Data Models", CheckStatus.WARN, "Fields found but no constraints")
    else:
        return CheckResult("T3", "Data Models", CheckStatus.FAIL, "No field type definitions found")


def t4_error_codes(tech_text: str) -> CheckResult:
    """T4: Error codes follow taxonomy format."""
    error_section = re.search(r"(?:##\s+)?Error\s+Handling(.*?)(?=\n##\s|\Z)", tech_text, re.DOTALL | re.IGNORECASE)

    if not error_section:
        return CheckResult("T4", "Error Codes", CheckStatus.FAIL, "No error handling section")

    error_text = error_section.group(1)
    codes = ERROR_CODE_PATTERN.findall(error_text)

    if len(codes) >= 3:
        return CheckResult("T4", "Error Codes", CheckStatus.PASS, f"{len(codes)} error codes")
    elif codes:
        return CheckResult("T4", "Error Codes", CheckStatus.WARN, f"Only {len(codes)} error codes")
    else:
        return CheckResult("T4", "Error Codes", CheckStatus.WARN, "No error codes in taxonomy format")


def t5_route_conflicts(tech_text: str, product_path: Path) -> CheckResult:
    """T5: No route path conflicts with existing PRODUCT.md routes."""
    if not product_path.is_file():
        return CheckResult("T5", "Route Conflicts", CheckStatus.PASS, "No PRODUCT.md to check against")

    product_text = product_path.read_text(encoding="utf-8")
    route_pattern = re.compile(r"(?:GET|POST|PUT|PATCH|DELETE)\s+(/[\w/{}\-]+)", re.IGNORECASE)

    existing_routes = {m.group(1) for m in route_pattern.finditer(product_text)}
    new_routes = {m.group(1) for m in route_pattern.finditer(tech_text)}

    conflicts = existing_routes & new_routes
    if not conflicts:
        return CheckResult("T5", "Route Conflicts", CheckStatus.PASS)
    else:
        return CheckResult("T5", "Route Conflicts", CheckStatus.FAIL, f"Conflicts: {', '.join(sorted(conflicts)[:3])}")


def run_tech_checks(spec_path: Path, tech_path: Path, product_path: Path) -> StageGateResult:
    """Run all T1-T5 checks."""
    if not tech_path.is_file():
        result = StageGateResult(stage="Technical Gate")
        result.checks.append(CheckResult("T0", "File", CheckStatus.FAIL, "TECHNICAL.md not found"))
        return result

    tech_text = tech_path.read_text(encoding="utf-8")
    result = StageGateResult(stage="Technical Gate")
    result.checks = [
        t1_coverage(spec_path, tech_text),
        t2_api_completeness(tech_text),
        t3_data_models(tech_text),
        t4_error_codes(tech_text),
        t5_route_conflicts(tech_text, product_path),
    ]
    return result
