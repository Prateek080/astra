---
description: Run a comprehensive code review on recent changes
argument-hint: "[file path or git ref]"
---

# Review Phase

Prefer delegating this review to the reviewer subagent to keep main context clean. If the Agent tool is unavailable, review directly but focus on the diff only — don't read entire files unless necessary.

## Process

1. Determine the review scope:
   - If $ARGUMENTS is a file path, review that file.
   - If $ARGUMENTS is a git ref (branch, commit), review changes in that ref.
   - Otherwise, review all uncommitted changes (`git diff` + `git diff --staged`).

2. Delegate to the reviewer subagent:
   "Use the reviewer subagent to review [scope]. The reviewer has a preloaded review-checklist covering security, performance, quality, reusability, and tech debt."

3. Present the reviewer's findings organized by severity:
   - **Critical** — must fix before shipping (security holes, data loss, broken functionality)
   - **Warning** — should fix (performance issues, missing edge cases, poor patterns)
   - **Suggestion** — consider improving (naming, structure, minor optimizations)

4. For each finding, include: file path, line reference, what's wrong, and how to fix it.

5. After the review, tell the user: "Review complete. Fix any critical/warning items, then run `/astra:ship` to commit and create a PR."
