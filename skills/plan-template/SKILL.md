---
name: plan-template
description: Structure template for creating phased implementation plans
user-invocable: false
---

# Plan Template

Structure every implementation plan as follows. Write to PLAN.md in the project root.

## Format

```markdown
# Plan: [Feature Name]

## Goal
One sentence: what does "done" look like? Include measurable criteria.

## Context
- Existing patterns to follow: [reference specific files]
- Dependencies: [what must exist before this feature]
- Test infrastructure: [how to run tests, what framework]

## Phase 1: [Name]
**Scope**: What this phase accomplishes independently.

**Files to create:**
- `path/to/new-file.ts` — purpose

**Files to modify:**
- `path/to/existing-file.ts` — what changes and why

**Tasks:**
1. [Specific, actionable task]
2. [Another task]
3. ...

**Test gate:**
- [ ] [Specific test command or verification step]
- [ ] [Another verification]

**Parallel**: yes/no (can this run independently of other phases?)

> Phases are marked `**Status: complete**` by `/astra:implement` as they pass their test gates. This enables resuming across sessions.

## Phase 2: [Name]
(same structure)

## Phase N: [Name]
(same structure)

## Files Summary
**Create:** list all new files across all phases
**Modify:** list all existing files that change across all phases

## Risks
- [Known risk and mitigation]
```

## Rules

- Each phase MUST have a test gate — no exceptions.
- Each phase must be small enough to complete in under 50% context.
- Mark phases as `Parallel: yes` when they have no dependencies on other phases.
- Reference SPECIFIC existing files and patterns, not generic guidance.
- "Files to create" vs "Files to modify" must be explicit — no ambiguity.
- Tasks must be numbered and specific enough that someone else could execute them.
