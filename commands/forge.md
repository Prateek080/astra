---
description: "Automated pipeline: task → spec → design → plan → architect → code. Fully autonomous with parallel stages — only stops on failures."
argument-hint: "[feature description] [--lite] [--interactive]"
---

> **Arguments**: Text after the command name is the feature description. Flags: `--lite` forces lite mode (skip design/architect), `--interactive` forces manual review gates at every stage.

# Forge — Automated Development Pipeline

You are orchestrating a complete development pipeline. You handle ALL agent communication, validate outputs, maintain the traceability chain R{n} → D-R{n}/T-R{n} → Phase → Test, and manage review gates.

**Speed optimizations active by default:**
- **Knowledge graph context** — `/graphify` builds persistent graph in Step 0. Agents use `/graphify query` for targeted lookups first, only read full `GRAPH_REPORT.md` when queries are insufficient. Falls back to `.astra-cache/context.md` if graphify unavailable.
- **Lean orchestrator** — After each step's gate passes, summarize the output in 2-3 lines and save to `forge-state.json`. Do NOT carry full artifact content forward. Agents read full files from disk — you only need summaries to coordinate.
- **Parallel stages** — Designer + Planner run concurrently
- **Zero-stop** — stages validate internally and proceed automatically. Only stops on failures (two-strike rule) or blockers.
- **Lite mode** — auto-detected for simple features (≤3 requirements, single type)

Use `--interactive` to add manual approval gates between stages. Use `--lite` to force lite mode.

---

## Step 0: Prerequisites & Context

### 0a. Check global setup

Check if `~/.claude/CLAUDE.md` contains `<!-- astra:managed -->`.
**If NOT found:** "First-time Astra — running setup." Execute `/astra:setup` inline, then continue.

### 0b. Check project setup

Check if project root `CLAUDE.md` contains `<!-- astra:managed -->`.
**If NOT found:** "Project not set up — running init." Execute `/astra:init` inline, then continue.

### 0c. Check for resumption (early — before loading context)

Create `.astra-cache/` dir first (`mkdir -p .astra-cache`).

**State file (preferred):** Check `.astra-cache/forge-state.json`. If it exists:
- Read `last_completed_step`, `feature`, `mode`, `timestamp`, `summaries`, `gates`
- Load the `summaries` object — this is your context for what happened in prior steps (replaces full artifacts you don't need to re-read)
- "Previous forge run for [feature] completed Step [N] at [timestamp]. Resume from Step [N+1]?" → Resume jumps to that step, **skipping 0d-0e below**.
- "Start fresh?" → Archive existing artifacts (same logic as Step 1a), delete `forge-state.json`, continue below.

**Artifact-based fallback** (if no forge-state.json):
- **All exist + PLAN.md has phases:** "Previous forge artifacts found for [feature]. Resume or start fresh?" → Resume jumps to Step 4.
- **SPEC.md + DESIGN.md + PLAN.md, no TECHNICAL.md:** Resume jumps to Step 3.
- **SPEC.md + DESIGN.md, no PLAN.md:** Resume jumps to Step 2.
- **Only SPEC.md:** Resume jumps to Step 2.
- **None exist:** Proceed normally.

When starting fresh, archive existing artifacts to `docs/` first (same logic as Step 1a).

### 0d. Load context (skipped on resume)

1. Read project CLAUDE.md and `docs/.agent-memory/forge-feedback.md` (if exists).
2. Read PRODUCT.md if exists — summarize existing features. If not: "First forge run. PRODUCT.md created after completion."

### 0e. Codebase context (skipped on resume)

**Knowledge graph (preferred):**
1. If `graphify-out/graph.json` exists → run `/graphify --update` (incremental — fast, code-only changes skip LLM)
2. If no `graph.json` → run `/graphify` (full build — auto-installs on first use)
3. If graphify fails or is unavailable → fall back to flat scan below

The graph persists across forge runs. Each run enriches it. Agents use `/graphify query` for targeted lookups first; they only read full `GRAPH_REPORT.md` when queries are insufficient.

**Flat scan fallback:**
Scan codebase and write `.astra-cache/context.md` with these sections:
- **Tech Stack** — framework, language, database, styling, testing (from package.json/config files)
- **Project Structure** — component paths, API routes, models, tests, config files
- **Frontend Patterns** — component library, design tokens, CSS approach, layout patterns
- **Backend Patterns** — API style, auth mechanism, ORM/DB, error handling
- **Conventions** — file naming, test location, import aliases

**Scan strategy:** Read config files → targeted Glob for dirs → read 1-2 representative files per category. Don't read every file.

### 0f. Get feature description

If $ARGUMENTS is empty and not resuming, ask the user what to build. Don't proceed without a clear description.

---

## Step 1: PM Agent → SPEC.md

### 1a. Archive existing artifacts

If SPEC.md exists: extract feature name → kebab-case slug → move SPEC.md, DESIGN.md, PLAN.md, TECHNICAL.md to `docs/{type}/{slug}.md` (create dirs, timestamp suffix if destination exists).

### 1b. Delegate to PM agent

"Conduct product discovery for [$ARGUMENTS]. Produce spec with numbered requirements (R1, R2...), RICE prioritization, Given/When/Then acceptance criteria."

### 1c. Write SPEC.md

Write output to SPEC.md. Verify structure: `# Feature:`, `## Requirements` with `### R` entries, `## Non-Functional Requirements`. If missing headings, send back to PM once.

### 1d. Detect complexity

Scan `### R{n}` patterns → build ID list. Count frontend vs backend vs full-stack.
- **Lite mode:** ≤3 requirements AND single type (frontend-only OR backend-only)
- **Full mode:** 4+ requirements OR full-stack
`--interactive` is orthogonal — it adds approval gates to whichever mode is detected, it does not force full mode.

### 1e. Stage gate — SPEC eval

Run **SPEC Eval** from stage-gate skill (S1–S5). Pass/warn/fail logic applies.

**Interactive mode:** Pause with full summary after eval passes. Wait for approval.

### 1f. Summarize and checkpoint

**Summarize** SPEC.md output in 2-3 lines (requirement count, IDs, types, mode detected). Discard full spec content from your working memory — agents read the file from disk.

Write `.astra-cache/forge-state.json`:
```json
{"last_completed_step": 1, "feature": "...", "mode": "full|lite", "timestamp": "<ISO>",
 "summaries": {"spec": "<2-3 line summary>"},
 "gates": {"S1": "pass", "S2": "pass", ...}}
```

---

## Step 2: Design + Planning

### Full Mode — Parallel Execution

Launch Designer and Planner as **parallel subagents**:

**Designer subagent:** "Create UI/UX design from SPEC.md. Produce DESIGN.md with D-R{n} traceability. Backend requirements → 'Technical — architect agent'."

**Planner subagent:** "Create phased plan from SPEC.md. Produce PLAN.md with phases, tasks, test gates. Reference R{n} in each phase."

Wait for both to complete. Write DESIGN.md and PLAN.md.

### Lite Mode — Plan Only

Skip Designer entirely. Launch Planner subagent only:

"Create phased plan from SPEC.md. Produce PLAN.md with phases, tasks, test gates."

Write PLAN.md.

### 2a. Stage gate — DESIGN eval (full mode only)

Run **DESIGN Eval** from stage-gate skill (D1–D5). Pass/warn/fail logic applies.

### 2b. Stage gate — PLAN eval

Run **PLAN Eval** from stage-gate skill (P1–P4). Pass/warn/fail logic applies.

**Interactive mode:** Pause with full design + plan summary after evals pass. Wait for approval.

### 2c. Summarize and checkpoint

**Summarize** DESIGN.md (component count, D-R coverage, key flows) and PLAN.md (phase count, parallel groups, total tasks) in 2-3 lines each. Discard full design and plan content from your working memory.

Update `forge-state.json` with `last_completed_step: 2`, add `summaries.design` and `summaries.plan`, add gate results.

---

## Step 3: Architect Agent → TECHNICAL.md

**Skip entirely in lite mode** — jump to Step 4.

### 3a. Delegate to Architect agent

"Create technical design. Read SPEC.md and DESIGN.md from disk. Produce TECHNICAL.md with T-R{n} traceability, ADRs, API contracts, data models."

### 3b. Stage gate — TECHNICAL eval

Write output to TECHNICAL.md. Run **TECHNICAL Eval** from stage-gate skill (T1–T5). Pass/warn/fail logic applies.

**Interactive mode:** Pause with full ADR + API + data model summary after eval passes. Wait for approval.

### 3c. Summarize and checkpoint

**Summarize** TECHNICAL.md (ADR count, API endpoint count, data models, T-R coverage) in 2-3 lines. Discard full technical content from your working memory.

Update `forge-state.json` with `last_completed_step: 3`, add `summaries.technical`, add gate results.

---

## Step 4: Implementation

Delegate to `commands/implement.md` logic.

### 4a. Scope

Delegate scoping to the implementer — it reads PLAN.md from disk. Pass only the mode (full/lite) and phase count from your summary. Do not re-read PLAN.md in the orchestrator.

### 4b. Execute phases

Follow `commands/implement.md` for phase execution — sequential phases, parallel batches, verification gates, status updates.

### 4c. Stage gate — PHASE eval

After each phase, run **PHASE Eval** from stage-gate skill (I1–I4). Pass/warn/fail logic applies. Critical findings → fix + re-test.

### 4d. Between phases

**Interactive mode:** Pause with phase summary after each phase gate passes. Wait for approval before next phase.
If context is heavy: "Recommend `/clear` before next phase."

### 4e. Summarize and checkpoint

**Summarize** implementation results (phases completed, tests passing, files changed count) in 2-3 lines. Discard per-phase implementation details from your working memory.

Update `forge-state.json` with `last_completed_step: 4`, add `summaries.implementation`, add per-phase gate results.

---

## Step 5: Final Review

1. Spawn reviewer: **Full mode:** "Review all changes. Verify acceptance criteria (Given/When/Then) for each R{n}. Cross-check implementation against DESIGN.md and TECHNICAL.md." **Lite mode:** "Review all changes. Verify acceptance criteria for each R{n}. Validate against SPEC.md and PLAN.md."

2. Present findings: Critical (must fix) / Warning (should fix) / Suggestion (consider).

3. Fix criticals, re-test. Two-strike rule applies.

4. Acceptance check: "R1: PASS — [evidence]" or "R2: FAIL — [gap]". Fix failures.

### 5a. Summarize and checkpoint

**Summarize** review results (criticals fixed, warnings noted, acceptance per R{n}) in 2-3 lines.

Update `forge-state.json` with `last_completed_step: 5`, add `summaries.review`, add acceptance results.

---

## Step 6: Wrap-Up

### 6a. Update PRODUCT.md

Create or update PRODUCT.md with: new feature in Current Features table, new design tokens, API endpoints, data models, conventions. Compact if >150 lines.

### 6b. Archive artifacts

Move SPEC.md → `docs/specs/`, DESIGN.md → `docs/designs/`, PLAN.md → `docs/plans/`, TECHNICAL.md → `docs/technical/`. Kebab-case slug, timestamp suffix if exists.

### 6c. Update knowledge graph

Run `/graphify --update` to absorb new code into the knowledge graph (best-effort — failure does not block wrap-up). Do NOT delete `graphify-out/` — it persists and enriches across runs.

### 6d. Clean up cache

Delete `.astra-cache/` directory (including `forge-state.json`) — it's only valid for this forge run.

### 6e. Document solutions

If non-obvious problems were solved: "Want me to run `/astra:compound` to document these?"

### 6f. Collect feedback

"Forge complete! (1) What worked well? (2) What to improve?" Persist to `docs/.agent-memory/forge-feedback.md`.

### 6g. Next steps

"Run `/astra:ship` to commit and PR. Or `/astra:retrospective` for process assessment."

---

## Key Rules

1. **You are the coordinator.** All communication flows through you. Agents never talk to each other.

2. **Agents query graphify first, read full report only if needed.** Pattern: `/graphify query "topic"` → targeted subgraph. Only read `graphify-out/GRAPH_REPORT.md` if query returns insufficient context. Fall back to `.astra-cache/context.md` if graphify unavailable. Agents never re-scan independently.

3. **Zero-stop is default.** Validate internally, print one-line progress, proceed. Only stop on failures (two-strike) or blockers. `--interactive` adds manual approval gates.

4. **Two-strike rule.** If any step fails twice, stop and ask the user.

5. **Traceability is non-negotiable.** R{n} → D-R{n}/T-R{n} → Phase → Test. Every requirement traced end-to-end.

6. **Lite mode skips design + architect.** Pipeline: PM → Plan → Implement → Review. For ≤3 requirements, single type.

7. **Parallel stages.** Designer + Planner run concurrently in full mode. Neither depends on the other's output.

8. **Lean orchestrator.** After each step's gate passes, summarize the output and discard full content. You carry summaries + gate results, not artifacts. Agents read files from disk. This keeps your context under ~3k tokens instead of 15k+.

9. **Context hygiene.** Delegate to subagents. Recommend `/clear` between phase groups.

10. **Handle interruptions.** "Resume by running `/astra:forge` again — it reads `forge-state.json` to pick up from the last completed step."

11. **No partial artifacts.** Either produce a valid artifact or leave previous state intact.
