"""SPEC checks (S1-S5) — deterministic Python, no LLM needed."""

from __future__ import annotations

import re
from pathlib import Path

from orchestrator.checks.base import CheckResult, CheckStatus, StageGateResult

# Vague words banned in requirement titles and acceptance criteria
BANNED_VAGUE_WORDS = {
    "fast",
    "intuitive",
    "secure",
    "scalable",
    "robust",
    "user-friendly",
    "efficient",
    "seamless",
    "elegant",
    "modern",
}

# Pattern to match requirement sections: ### R1: Title, ### R2: Title, etc.
REQ_PATTERN = re.compile(r"^###\s+R(\d+):\s*(.+)$", re.MULTILINE)

# Pattern for Given/When/Then blocks
GWT_PATTERN = re.compile(r"\b(Given|When|Then)\b", re.IGNORECASE)

# Pattern for RICE scores
RICE_PATTERN = re.compile(r"\*\*RICE\*\*|RICE\s*[:\|]|\|\s*RICE\s*\|", re.IGNORECASE)


def _extract_requirements(spec_text: str) -> list[tuple[str, str, str]]:
    """Extract (id, title, section_text) for each R{n} in the spec."""
    matches = list(REQ_PATTERN.finditer(spec_text))
    requirements = []

    for i, match in enumerate(matches):
        req_id = f"R{match.group(1)}"
        title = match.group(2).strip()
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(spec_text)
        section_text = spec_text[start:end]
        requirements.append((req_id, title, section_text))

    return requirements


def _extract_keywords(feature_desc: str) -> set[str]:
    """Extract meaningful keywords from feature description."""
    stop_words = {
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "can", "shall", "to", "of", "in", "for",
        "on", "with", "at", "by", "from", "as", "into", "through", "during",
        "before", "after", "above", "below", "between", "and", "but", "or",
        "not", "no", "nor", "so", "if", "then", "than", "too", "very",
        "just", "about", "up", "out", "that", "this", "it", "its",
        "add", "build", "create", "implement", "make", "system", "feature",
        "new", "want", "need", "like", "i",
    }
    words = set(re.findall(r"\b[a-z]+\b", feature_desc.lower()))
    return words - stop_words


def s1_relevance(feature_desc: str, spec_text: str) -> CheckResult:
    """S1: Do requirement titles match the feature description keywords?"""
    keywords = _extract_keywords(feature_desc)
    if not keywords:
        return CheckResult("S1", "Relevance", CheckStatus.PASS, "No keywords to match")

    requirements = _extract_requirements(spec_text)
    if not requirements:
        return CheckResult("S1", "Relevance", CheckStatus.FAIL, "No requirements found")

    titles_combined = " ".join(title.lower() for _, title, _ in requirements)
    body_combined = spec_text.lower()

    title_hits = sum(1 for kw in keywords if kw in titles_combined)
    body_hits = sum(1 for kw in keywords if kw in body_combined)

    if title_hits >= len(keywords) * 0.3:
        return CheckResult("S1", "Relevance", CheckStatus.PASS)
    elif body_hits >= len(keywords) * 0.3:
        return CheckResult("S1", "Relevance", CheckStatus.WARN, "Keywords in body, not titles")
    else:
        return CheckResult("S1", "Relevance", CheckStatus.FAIL, "Requirements don't match feature")


def s2_specificity(spec_text: str) -> CheckResult:
    """S2: Are there banned vague words in requirement titles or criteria?"""
    requirements = _extract_requirements(spec_text)
    if not requirements:
        return CheckResult("S2", "Specificity", CheckStatus.FAIL, "No requirements found")

    vague_in_titles = []
    vague_in_criteria = []

    for req_id, title, section in requirements:
        title_lower = title.lower()
        for word in BANNED_VAGUE_WORDS:
            if re.search(rf"\b{word}\b", title_lower):
                # Check if followed by a metric (number within 20 chars)
                idx = title_lower.index(word)
                context = title_lower[idx : idx + 30]
                if not re.search(r"\d", context):
                    vague_in_titles.append(f"{req_id}: '{word}'")

        # Check Given/When/Then sections
        gwt_sections = re.findall(
            r"(?:Given|When|Then)\s+.+",
            section,
            re.IGNORECASE,
        )
        for gwt in gwt_sections:
            for word in BANNED_VAGUE_WORDS:
                if re.search(rf"\b{word}\b", gwt.lower()):
                    if not re.search(r"\d", gwt[gwt.lower().index(word) :]):
                        vague_in_criteria.append(f"{req_id}: '{word}'")

    if vague_in_titles:
        return CheckResult(
            "S2", "Specificity", CheckStatus.FAIL,
            f"Vague titles: {', '.join(vague_in_titles[:3])}"
        )
    if vague_in_criteria:
        return CheckResult(
            "S2", "Specificity", CheckStatus.WARN,
            f"Vague criteria: {', '.join(vague_in_criteria[:3])}"
        )
    return CheckResult("S2", "Specificity", CheckStatus.PASS)


def s3_criteria(spec_text: str) -> CheckResult:
    """S3: Does every R{n} have Given/When/Then acceptance criteria?"""
    requirements = _extract_requirements(spec_text)
    if not requirements:
        return CheckResult("S3", "Criteria", CheckStatus.FAIL, "No requirements found")

    total = len(requirements)
    with_gwt = 0

    for req_id, _, section in requirements:
        gwt_keywords = set()
        for match in GWT_PATTERN.finditer(section):
            gwt_keywords.add(match.group(1).lower())
        # Need at least Given + Then or When + Then
        if len(gwt_keywords) >= 2:
            with_gwt += 1

    ratio = with_gwt / total if total > 0 else 0

    if ratio >= 0.8:
        return CheckResult("S3", "Criteria", CheckStatus.PASS, f"{with_gwt}/{total}")
    elif ratio >= 0.5:
        return CheckResult("S3", "Criteria", CheckStatus.WARN, f"Only {with_gwt}/{total} have criteria")
    else:
        return CheckResult("S3", "Criteria", CheckStatus.FAIL, f"Only {with_gwt}/{total} have criteria")


def s4_rice(spec_text: str) -> CheckResult:
    """S4: Are RICE scores present?"""
    requirements = _extract_requirements(spec_text)
    if not requirements:
        return CheckResult("S4", "RICE", CheckStatus.FAIL, "No requirements found")

    # Check for RICE anywhere in the spec (could be a table or per-requirement)
    has_rice_global = bool(RICE_PATTERN.search(spec_text))

    # Check per requirement for Reach/Impact/Confidence/Effort keywords
    rice_dims = {"reach", "impact", "confidence", "effort"}
    per_req_rice = 0
    for _, _, section in requirements:
        section_lower = section.lower()
        found_dims = sum(1 for d in rice_dims if d in section_lower)
        if found_dims >= 3:
            per_req_rice += 1

    if has_rice_global or per_req_rice > 0:
        return CheckResult("S4", "RICE", CheckStatus.PASS)
    else:
        return CheckResult("S4", "RICE", CheckStatus.WARN, "No RICE scores found")


def s5_scope(spec_text: str) -> CheckResult:
    """S5: Is scope reasonable (<=10 Now-tier requirements)?"""
    requirements = _extract_requirements(spec_text)
    count = len(requirements)

    if count == 0:
        return CheckResult("S5", "Scope", CheckStatus.FAIL, "No requirements found")
    elif count <= 10:
        return CheckResult("S5", "Scope", CheckStatus.PASS, f"{count} requirements")
    elif count <= 15:
        return CheckResult("S5", "Scope", CheckStatus.WARN, f"{count} requirements (consider trimming)")
    else:
        return CheckResult("S5", "Scope", CheckStatus.FAIL, f"{count} requirements (scope creep)")


def run_spec_checks(feature_desc: str, spec_path: Path) -> StageGateResult:
    """Run all S1-S5 checks on a SPEC.md file."""
    if not spec_path.is_file():
        result = StageGateResult(stage="Spec Gate")
        result.checks.append(
            CheckResult("S0", "File", CheckStatus.FAIL, "SPEC.md not found")
        )
        return result

    spec_text = spec_path.read_text(encoding="utf-8")

    result = StageGateResult(stage="Spec Gate")
    result.checks = [
        s1_relevance(feature_desc, spec_text),
        s2_specificity(spec_text),
        s3_criteria(spec_text),
        s4_rice(spec_text),
        s5_scope(spec_text),
    ]
    return result
