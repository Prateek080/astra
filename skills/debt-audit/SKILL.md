---
name: debt-audit
description: Audit codebase for technical debt — dead code, TODOs, deprecated patterns, missing tests, hardcoded values
disable-model-invocation: true
context: fork
agent: general-purpose
allowed-tools: Read, Grep, Glob, Bash
---

# Tech Debt Audit

Perform a comprehensive audit of the codebase for technical debt. Do NOT make any changes — report only.

## Audit Checklist

### 1. Dead Code
- Search for unused exports, functions, and variables.
- Look for files that are not imported anywhere.
- Check for commented-out code blocks.
- Find unused dependencies in package.json / pyproject.toml.

### 2. TODOs and Fixmes
- Search for `TODO`, `FIXME`, `HACK`, `XXX`, `TEMP` comments.
- For each, note: file, line, age (git blame), and whether it has a linked issue.

### 3. Deprecated Patterns
- Check for deprecated API usage (e.g., old React lifecycle methods, deprecated Node.js APIs).
- Look for patterns that differ from the project's current conventions.
- Identify inconsistencies (e.g., some files use one pattern, others use another).

### 4. Hardcoded Values
- Search for hardcoded URLs, ports, API keys, feature flags, limits, and timeouts.
- Flag anything that should be environment configuration.

### 5. Missing Tests
- Identify modules, routes, or components with no corresponding test files.
- Find critical code paths that lack test coverage.

### 6. Dependency Health
- Check for outdated major versions (if tools available).
- Look for duplicate dependencies (same library, different versions).

### 7. Code Duplication
- Identify copy-pasted code blocks (3+ similar patterns that should be extracted).

## Output Format

```markdown
# Tech Debt Audit — [Date]

## Summary
- Dead code: X findings
- TODOs: X findings (Y without linked issues)
- Deprecated patterns: X findings
- Hardcoded values: X findings
- Missing tests: X modules without coverage
- Dependency issues: X findings
- Duplication: X findings

## Critical (fix soon)
[Findings that pose risk or actively slow development]

## Important (plan to fix)
[Findings that accumulate cost over time]

## Minor (fix opportunistically)
[Findings to address when touching nearby code]

## Detailed Findings
[Full list organized by category]
```
