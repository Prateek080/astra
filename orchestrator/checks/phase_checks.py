"""PHASE checks (I1-I4) — mostly subprocess, I4 needs small LLM call."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from orchestrator.checks.base import CheckResult, CheckStatus, StageGateResult


async def _run_cmd(cmd: str, cwd: Path, timeout: int = 120) -> tuple[int, str, str]:
    """Run a shell command and return (returncode, stdout, stderr)."""
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            cwd=str(cwd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return (
            proc.returncode or 0,
            stdout.decode("utf-8", errors="replace"),
            stderr.decode("utf-8", errors="replace"),
        )
    except asyncio.TimeoutError:
        return (1, "", f"Command timed out after {timeout}s")
    except Exception as e:
        return (1, "", str(e))


def _detect_test_command(project_dir: Path) -> str | None:
    """Detect the project's test command from config files."""
    pkg_json = project_dir / "package.json"
    if pkg_json.is_file():
        try:
            pkg = json.loads(pkg_json.read_text())
            scripts = pkg.get("scripts", {})
            if "test" in scripts:
                return "npm test"
        except (json.JSONDecodeError, KeyError):
            pass

    # Python
    if (project_dir / "pyproject.toml").is_file() or (project_dir / "pytest.ini").is_file():
        return "python -m pytest"

    # Go
    if (project_dir / "go.mod").is_file():
        return "go test ./..."

    return None


def _detect_lint_command(project_dir: Path) -> str | None:
    """Detect the project's lint command."""
    pkg_json = project_dir / "package.json"
    if pkg_json.is_file():
        try:
            pkg = json.loads(pkg_json.read_text())
            scripts = pkg.get("scripts", {})
            if "lint" in scripts:
                return "npm run lint"
        except (json.JSONDecodeError, KeyError):
            pass

    if (project_dir / "pyproject.toml").is_file():
        return "python -m ruff check ."

    return None


def _detect_typecheck_command(project_dir: Path) -> str | None:
    """Detect the project's type-check command."""
    if (project_dir / "tsconfig.json").is_file():
        return "npx tsc --noEmit"

    if (project_dir / "pyproject.toml").is_file():
        return "python -m mypy ."

    return None


async def i1_tests(project_dir: Path) -> CheckResult:
    """I1: Tests pass."""
    cmd = _detect_test_command(project_dir)
    if not cmd:
        return CheckResult("I1", "Tests", CheckStatus.WARN, "No test command detected")

    rc, stdout, stderr = await _run_cmd(cmd, project_dir, timeout=300)
    if rc == 0:
        return CheckResult("I1", "Tests", CheckStatus.PASS)
    else:
        # Extract brief error
        error_lines = (stderr or stdout).strip().split("\n")
        brief = error_lines[-1][:100] if error_lines else "Tests failed"
        return CheckResult("I1", "Tests", CheckStatus.FAIL, brief)


async def i2_lint(project_dir: Path) -> CheckResult:
    """I2: Linter passes."""
    cmd = _detect_lint_command(project_dir)
    if not cmd:
        return CheckResult("I2", "Lint", CheckStatus.WARN, "No lint command detected")

    rc, stdout, stderr = await _run_cmd(cmd, project_dir)
    if rc == 0:
        return CheckResult("I2", "Lint", CheckStatus.PASS)
    else:
        output = (stderr or stdout).strip()
        # Check if only warnings (no errors)
        if "error" not in output.lower():
            return CheckResult("I2", "Lint", CheckStatus.WARN, "Lint warnings present")
        return CheckResult("I2", "Lint", CheckStatus.FAIL, "Lint errors")


async def i3_types(project_dir: Path) -> CheckResult:
    """I3: Type checker passes."""
    cmd = _detect_typecheck_command(project_dir)
    if not cmd:
        return CheckResult("I3", "Types", CheckStatus.WARN, "No type checker detected")

    rc, stdout, stderr = await _run_cmd(cmd, project_dir)
    if rc == 0:
        return CheckResult("I3", "Types", CheckStatus.PASS)
    else:
        return CheckResult("I3", "Types", CheckStatus.FAIL, "Type errors found")


async def i4_criteria_spot_check(project_dir: Path, spec_path: Path) -> CheckResult:
    """I4: Spot-check — does a sampled Given/When/Then have a matching test?

    This is a lighter check: just verify test files exist for the feature.
    Full criteria verification happens in the review stage.
    """
    if not spec_path.is_file():
        return CheckResult("I4", "Criteria Spot", CheckStatus.WARN, "No SPEC.md")

    # Check if any test files exist in the project
    test_patterns = ["**/*.test.*", "**/*.spec.*", "tests/**", "test/**"]
    test_files = []
    for pattern in test_patterns:
        test_files.extend(project_dir.glob(pattern))

    if test_files:
        return CheckResult("I4", "Criteria Spot", CheckStatus.PASS, f"{len(test_files)} test files found")
    else:
        return CheckResult("I4", "Criteria Spot", CheckStatus.WARN, "No test files found")


async def run_phase_checks(project_dir: Path, spec_path: Path) -> StageGateResult:
    """Run all I1-I4 checks."""
    result = StageGateResult(stage="Phase Gate")

    # Run I1-I3 in parallel, I4 is fast
    i1_task = asyncio.create_task(i1_tests(project_dir))
    i2_task = asyncio.create_task(i2_lint(project_dir))
    i3_task = asyncio.create_task(i3_types(project_dir))
    i4_task = asyncio.create_task(i4_criteria_spot_check(project_dir, spec_path))

    result.checks = await asyncio.gather(i1_task, i2_task, i3_task, i4_task)
    return result
