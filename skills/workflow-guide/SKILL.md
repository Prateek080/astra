---
name: workflow-guide
description: How to use the astra workflow for new projects, new features, and optimizations. Invoke when unsure which commands to use.
disable-model-invocation: false
---

# Astra Workflow Guide

## When to Use What

Not every task needs the full workflow. Match the approach to the task size:

### Trivial (typo, rename, config change, one-line fix)
Just ask Claude directly. No astra commands needed. The overhead isn't worth it.

### Small (single file, clear scope, simple bug fix)
Just ask Claude directly. Optionally run `/astra:review` after to catch anything.

### Medium (2-5 files, clear approach, well-understood feature)
```
/astra:plan → /astra:implement → /astra:review → /astra:ship
```

### Large (new feature, unclear scope, multiple modules, needs discovery)
```
/astra:spec → /clear → /astra:plan → /astra:implement → /astra:review → /astra:ship
```
Start a fresh session (`/clear`) between spec and plan for clean context.

### Optimization / Refactor (improving existing code)
```
/astra:debt-audit → /astra:plan → /astra:implement → /astra:review → /astra:ship
```

---

## Scenario A: New Project from Scratch

1. **Initialize the project** — Set up repo, install dependencies, configure tooling.

2. **Set up Claude Code for the project:**
   - Run `/astra:init` to generate CLAUDE.md and `.claude/rules/` for the project.
   - Install relevant LSP plugin: run `/plugin` and search for your language.

3. **Spec the MVP** — `/astra:spec` to interview and produce SPEC.md.
   - Focus on MVP scope. Don't spec everything — spec the first milestone.

4. **Plan the MVP** — `/clear` then `/astra:plan` to create phased milestones.
   - Each phase should be independently deployable.

5. **Build phase by phase** — `/astra:implement` for each phase.
   - `/clear` between phases for clean context.
   - `/astra:review` after each phase, not just at the end.

6. **Ship incrementally** — `/astra:ship` per phase. Small PRs, not one giant PR.

---

## Scenario B: New Feature in Existing Project

1. **Spec with context** — `/astra:spec`
   - Claude interviews you about the feature, reading project context (CLAUDE.md, README).
   - The spec identifies requirements, constraints, and scope boundaries.

2. **Plan with awareness** — `/astra:plan`
   - The planner agent explores existing patterns and conventions.
   - Plan explicitly states "modify X" vs "create Y".
   - Plan references existing files to follow as templates.

3. **Build with reuse** — `/astra:implement`
   - Before writing new code, Claude searches for existing patterns.
   - Follows the project's existing conventions (naming, structure, error handling).
   - Runs existing tests after each change to catch regressions.

4. **Review and ship** — `/astra:review` then `/astra:ship`

---

## Scenario C: Optimization of Existing Feature

1. **Audit first** — `/astra:debt-audit`
   - Full scan of the feature area for tech debt, perf issues, dead code.
   - Produces a prioritized report.

2. **Measure baselines** — Before any changes, establish numbers:
   - Test coverage, bundle size, response times, memory usage (whatever applies).
   - Document baselines in PLAN.md so you can verify improvement.

3. **Plan incremental refactors** — `/astra:plan`
   - Each change must keep tests passing.
   - No rewrites — incremental improvements.
   - Strangler fig pattern: new code alongside old, then switch.

4. **Build and verify** — `/astra:implement`
   - After each phase, verify metrics improved.
   - If metrics don't improve, rewind and try a different approach.

5. **Review with extra scrutiny** — `/astra:review`
   - Focus on: reusability, debt prevention, performance, no regressions.

---

## Two Modes of Operation

### Command Mode (default)
Use `/astra:*` commands normally. Claude delegates to subagents as needed.
Best for most work — simple, low overhead.

### Coordinator Mode (power mode)
Run `claude --agent astra:coordinator` for complex multi-phase features.
The coordinator can spawn planner, implementer, reviewer, and debugger agents in parallel.
Use for large features that benefit from orchestrated parallel execution.

---

## Context Management Tips

- **`/clear` between unrelated tasks** — the #1 habit for maintaining quality.
- **`/clear` between phases** — don't let implementation phase N pollute phase N+1.
- **Use subagents for research** — keeps main context clean.
- **If you've corrected Claude twice on the same issue**, `/clear` and rephrase.
- **Set up a status line** — run `/statusline` to monitor context usage and cost.
- **Manual `/compact`** at ~50% context if you need to continue without clearing.
