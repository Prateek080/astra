---
name: workflow-guide
description: How to use the astra workflow for new projects, new features, and optimizations. Invoke when unsure which commands to use.
user-invocable: true
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
/astra:spec → fresh session → /astra:design → fresh session → /astra:plan → /astra:architect → /astra:implement → /astra:review → /astra:ship
```
Start a fresh session between stages for clean context (Claude Code: `/clear`, Cursor: new chat).

### End-to-End (full automation with review gates at every stage)
```
/astra:forge "feature description"
```
Forge chains spec → design → plan → architect → implement → review automatically, with user approval gates between each stage. Best for features where you want the full pipeline managed for you.

### Optimization / Refactor (improving existing code)
```
/astra:debt-audit → /astra:plan → /astra:implement → /astra:review → /astra:ship
```

---

## Scenario A: New Project from Scratch

1. **Initialize the project** — Set up repo, install dependencies, configure tooling.

2. **Set up for the project:**
   - Run `/astra:init` to generate CLAUDE.md and project rules (`.claude/rules/` and `.cursor/rules/`).
   - Claude Code: install relevant LSP plugin via `/plugin`.

3. **Spec the MVP** — `/astra:spec` to interview and produce SPEC.md.
   - Focus on MVP scope. Don't spec everything — spec the first milestone.

4. **Design the MVP** — Start a fresh session, then `/astra:design` to create DESIGN.md.
   - Establishes UI component patterns, visual design, and user flows.
   - Skip for backend-only projects.

5. **Plan the MVP** — Start a fresh session, then `/astra:plan` to create phased milestones.
   - Each phase should be independently deployable.

6. **Architect the MVP** — Start a fresh session, then `/astra:architect` to create TECHNICAL.md.
   - Locks down API contracts, data models, and system architecture.
   - Skip for frontend-only projects with no backend.

7. **Build phase by phase** — `/astra:implement` for each phase.
   - Start fresh between phases for clean context.
   - `/astra:review` after each phase, not just at the end.

8. **Ship incrementally** — `/astra:ship` per phase. Small PRs, not one giant PR.

---

## Scenario B: New Feature in Existing Project

1. **Spec with context** — `/astra:spec`
   - Claude interviews you about the feature, reading project context (CLAUDE.md, README, PRODUCT.md).
   - The spec identifies requirements, constraints, and scope boundaries.

2. **Design with awareness** — `/astra:design`
   - Designer explores existing UI patterns (components, tokens, layout conventions).
   - Produces DESIGN.md with UI/UX specs mapped to each requirement (D-R{n} → R{n}).
   - Skip for backend-only features or when the UI approach is already clear.

3. **Plan with awareness** — `/astra:plan`
   - The planner agent explores existing patterns and conventions.
   - Plan explicitly states "modify X" vs "create Y".
   - Plan references existing files and design elements (D-R{n}) to follow.

4. **Architect with awareness** — `/astra:architect`
   - Architect explores existing API patterns, data models, and service architecture.
   - Produces TECHNICAL.md with API contracts, data models, ADRs mapped to each requirement (T-R{n} → R{n}).
   - Skip for frontend-only features with no backend changes.

5. **Build with reuse** — `/astra:implement`
   - Before writing new code, Claude searches for existing patterns.
   - Follows the project's existing conventions (naming, structure, error handling).
   - Runs existing tests after each change to catch regressions.

6. **Review and ship** — `/astra:review` then `/astra:ship`

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

## Scenario D: Automated End-to-End Feature (Forge)

1. **Run forge** — `/astra:forge "add notifications system"`
   - PM agent interviews you, produces SPEC.md with numbered requirements (R1, R2...) and acceptance criteria
   - You review and approve the spec
   - Designer agent explores the codebase, produces DESIGN.md mapping UI requirements to design elements (D-R{n})
   - You review and approve the UI/UX design
   - Planner agent produces PLAN.md with full traceability (R{n} → D-R{n} → Phase tasks)
   - You review and approve the plan
   - Architect agent produces TECHNICAL.md with API contracts, data models, and ADRs (T-R{n})
   - You review and approve the technical design
   - Implementer executes phase by phase with reviewer checking each phase
   - Final review validates all acceptance criteria are met
   - PRODUCT.md is updated with the new feature, artifacts are archived

2. **Ship** — `/astra:ship` to commit and create a PR

Forge is for features where you want the full pipeline automated with review gates between stages. For smaller tasks, use individual commands (`/astra:spec`, `/astra:design`, `/astra:plan`, etc.).

**Using individual stages manually:** You can also run the design stage standalone with `/astra:design` — it reads SPEC.md and produces DESIGN.md. This lets you use the manual flow: `/astra:spec` → `/astra:design` → `/astra:plan` → `/astra:implement` with full control over each step.

---

## When Plans Change

Real development isn't linear. Here's how to handle common disruptions:

| Situation | What to do |
|---|---|
| Spec changed after planning | Update SPEC.md, then re-run `/astra:design` (if using design), `/astra:plan`, and `/astra:architect` |
| Design changed after planning | Update DESIGN.md, then re-run `/astra:plan` — it reads the updated design |
| Technical design changed | Update TECHNICAL.md, then re-run `/astra:implement` — it reads the updated technical design |
| Review found architectural issues | Small: fix in place. Fundamental: re-plan the affected phases |
| Later phase reveals earlier phase was wrong | Fix the earlier phase, update PLAN.md, then continue |
| Scope creep during implementation | Stop. Update SPEC.md with the new scope, re-run design and plan |
| Stuck after 2 attempts on a phase | Run `/astra:debug` or re-plan that phase with a different approach |

The key principle: **update the artifact** (SPEC.md, DESIGN.md, or PLAN.md), **then re-run the corresponding command**. Don't try to hold changes in your head across sessions.

---

## How It Works

Use `/astra:*` commands normally. The AI delegates to subagents as needed.
When your plan has phases marked `Parallel: yes`, the implement command automatically spawns parallel subagents to execute them concurrently.

---

## Context Management Tips

- **Start fresh between unrelated tasks** — the #1 habit for maintaining quality. In Claude Code: `/clear`. In Cursor: start a new chat.
- **Start fresh between phases** — don't let implementation phase N pollute phase N+1.
- **Use subagents for research** — keeps main context clean.
- **If you've corrected the AI twice on the same issue**, start fresh and rephrase.
- **Claude Code:** run `/statusline` to monitor context usage. Run `/compact` at ~50% context if you need to continue without clearing.
- **Cursor:** context usage is visible in the UI. Start a new chat when context feels heavy.
