# Astra HEARTBEAT — Cron-Driven Pipeline Orchestration

Run on cron schedule. Each invocation checks pipeline state and takes the next appropriate action.

---

## State Machine

```
idle → scan → spec → [design + plan] → architect → implement → review → wrapup → idle
                       ↑ parallel ↑

Lite mode: idle → scan → spec → plan → implement → review → wrapup → idle
```

---

## On Each Heartbeat

### Priority 1: Active Build

Read `.astra-state/progress.json` and determine action.

```
current_stage = read progress.json → current_stage

IF current_stage == "idle":
    → go to Priority 2 (queue processing)

IF current_stage has status "in_progress":
    session = get session for this stage
    IF session is still running:
        heartbeat_count = count heartbeats since stage started
        IF heartbeat_count >= 3:
            → STALL: kill session, report stall, respawn agent
               python scripts/report.py --event stall --stage {current_stage} --details "Stalled after {heartbeat_count} heartbeats"
        ELSE:
            → WAIT: do nothing, exit
    IF session is done:
        → run stage-gate eval (see Gate Logic below)

IF current_stage has status "complete":
    → advance to next stage (see Advance Logic below)

IF current_stage has status "failed":
    retry_count = read progress.json → stages[current_stage].retry_count
    IF retry_count < 2:
        → RETRY: respawn agent, increment retry
           python scripts/update_progress.py --stage {current_stage} --status in_progress --retry
    ELSE:
        → BLOCKED: report failure, stop pipeline
           python scripts/report.py --event fail --stage {current_stage} --details "Failed after 2 attempts"
```

### Priority 2: Queue Processing

```
IF no active build (current_stage == "idle"):
    queue = read .astra-state/queue.json
    IF queue is non-empty:
        feature = pop highest priority item
        → start new pipeline:
           python scripts/update_progress.py --action init --feature "{feature}" --mode full
           python scripts/report.py --event start --stage pipeline --details "Feature: {feature}"
           → advance to "scan" stage
    ELSE:
        → check .astra-cache/backlog.md for unchecked items (nightly forge pattern)
        IF backlog has "- [ ]" items:
            feature = first unchecked item
            → start new pipeline (same as above)
```

### Priority 3: Health Check

```
# Only if idle with empty queue
git status → check for uncommitted changes (warn if dirty)
graphify graph staleness → if > 24h since last update, run graphify . --update
```

---

## Stage Execution

### Stage: scan
**Agent:** None (Dexter runs directly)
**Action:**
```bash
# Preferred: graphify
if [ -d "graphify-out" ]; then
    graphify . --update
else
    graphify . --no-viz
fi

# Fallback: manual scan → .astra-cache/context.md
```
**Gate:** Graph file exists or context.md exists
**On complete:**
```bash
python scripts/update_progress.py --stage scan --status complete
```

### Stage: spec
**Agent:** `product-manager`
**Spawn:** `sessions_spawn agentId="product-manager" message="Conduct product discovery for: {feature}. Read REQUIREMENTS.md template for output format."`
**Gate:** Run S1-S5 checks:
```bash
python scripts/run_stage_eval.py --stage spec --feature "{feature}" --project-dir .
```
**Mode detection:** After gate passes, detect full vs lite:
```bash
python scripts/update_progress.py --action detect-mode --spec REQUIREMENTS.md
```
**On complete:**
```bash
python scripts/update_progress.py --stage spec --status complete --artifact REQUIREMENTS.md
python scripts/report.py --event pass --stage spec --details "S1-S5 checks passed"
```

### Stage: design + plan (parallel — full mode only)
**Agents:** `ux-designer` AND `planner`
**Spawn both simultaneously:**
```bash
sessions_spawn agentId="ux-designer" message="Create UI/UX design from REQUIREMENTS.md. Use mediator scripts for output."
sessions_spawn agentId="planner" message="Create implementation plan from REQUIREMENTS.md. Write PLAN.md."
```
**Track:** Record both session IDs in progress.json
**Wait:** Both must complete before advancing
**Gate (design):** Run D1-D5 checks:
```bash
python scripts/run_stage_eval.py --stage design --project-dir .
```
**Gate (plan):** Run P1-P4 checks:
```bash
python scripts/run_stage_eval.py --stage plan --project-dir .
```
**On complete:**
```bash
python scripts/update_progress.py --stage design --status complete --artifact DESIGN_SPECS.md
python scripts/update_progress.py --stage plan --status complete --artifact PLAN.md
python scripts/report.py --event pass --stage "design+plan" --details "D1-D5 + P1-P4 passed"
```

In **lite mode:** Skip design, run only planner.

### Stage: architect (full mode only)
**Agent:** `architect`
**Spawn:** `sessions_spawn agentId="architect" message="Create technical design from REQUIREMENTS.md, DESIGN_SPECS.md, PLAN.md. Write TECHNICAL.md."`
**Gate:** Run T1-T5 checks:
```bash
python scripts/run_stage_eval.py --stage technical --project-dir .
```
**On complete:**
```bash
python scripts/update_progress.py --stage architect --status complete --artifact TECHNICAL.md
python scripts/report.py --event pass --stage architect --details "T1-T5 checks passed"
```

### Stage: implement
**Agent:** `coder`
**Spawn:** `sessions_spawn agentId="coder" message="Implement PLAN.md phases. Use claim_requirement.py / complete_requirement.py to track progress. Run tests after each phase."`
**Gate:** Run I1-I4 checks:
```bash
python scripts/run_stage_eval.py --stage phase --project-dir .
```
**On complete:**
```bash
python scripts/update_progress.py --stage implement --status complete
# Git commit
git add src/ app/ lib/ tests/ test/ __tests__/ pages/ && git commit -m "feat: implement {feature}"
python scripts/report.py --event pass --stage implement --details "I1-I4 checks passed"
```

### Stage: review
**Agent:** `reviewer`
**Spawn:** `sessions_spawn agentId="reviewer" message="Review all code changes. Run git diff. Cross-check against REQUIREMENTS.md, DESIGN_SPECS.md, TECHNICAL.md. Run stage-gate evals."`
**Gate:** Review findings contain no Critical issues
**On complete:**
```bash
python scripts/update_progress.py --stage review --status complete
python scripts/report.py --event pass --stage review --details "No critical issues"
```

### Stage: wrapup
**Agent:** None (Dexter runs directly)
**Actions:**
1. Archive artifacts:
   ```bash
   cp REQUIREMENTS.md docs/specs/REQUIREMENTS-$(date +%Y%m%d).md 2>/dev/null
   cp DESIGN_SPECS.md docs/designs/DESIGN_SPECS-$(date +%Y%m%d).md 2>/dev/null
   cp PLAN.md docs/plans/PLAN-$(date +%Y%m%d).md 2>/dev/null
   cp TECHNICAL.md docs/technical/TECHNICAL-$(date +%Y%m%d).md 2>/dev/null
   ```

2. Save agent memory:
   ```bash
   # Each agent saves its own memory via docs/.agent-memory/{name}.md
   # Dexter logs pipeline summary
   echo "## $(date +%Y-%m-%d) — {feature} ({mode} mode, pipeline {id})" >> docs/.agent-memory/dexter.md
   ```

3. Create PR:
   ```bash
   git push -u origin $(git rev-parse --abbrev-ref HEAD)
   gh pr create --title "feat: {feature}" --body "## Summary\n\nAutomated implementation via Astra Forge.\n\n## Requirements Checklist\n\n{R{n} checklist from REQUIREMENTS.md}"
   ```

4. Update graphify:
   ```bash
   graphify . --update 2>/dev/null
   ```

5. Send completion report:
   ```bash
   python scripts/report.py --event complete --stage pipeline --details "Feature: {feature}. Mode: {mode}. All stages passed."
   ```

6. Clean up and mark idle:
   ```bash
   python scripts/update_progress.py --stage wrapup --status complete
   python scripts/update_progress.py --action reset-idle
   ```

---

## Advance Logic

```
NEXT_STAGE map:
    idle     → scan
    scan     → spec
    spec     → design+plan (full) | plan (lite)
    design   → architect (after plan also complete)
    plan     → architect (after design also complete, full) | implement (lite)
    architect → implement
    implement → review
    review   → wrapup
    wrapup   → idle

To advance:
    next = NEXT_STAGE[current_stage]
    python scripts/update_progress.py --stage {next} --status pending
    → On next heartbeat, this stage will be picked up
```

For parallel stages (design+plan):
```
Both must be "complete" before advancing to architect.
If design is complete but plan is still running → wait.
If plan is complete but design is still running → wait.
```

---

## Lean Summaries

After each stage completes, save a 2-3 line summary to `.astra-state/forge-state.json`:

```json
{
  "scan": "Scanned 47 files. Stack: Next.js + Prisma + Tailwind. Tests: Jest.",
  "spec": "6 requirements (R1-R6). 4 Now, 1 Next, 1 Later. Mixed frontend+backend.",
  "design": "5 D-R{n} components. Design system: Radix + custom tokens.",
  "plan": "4 phases. Phase 1: data model. Phase 2-3: API+UI (parallel). Phase 4: integration tests.",
  "architect": "3 API endpoints. 2 new models. 1 ADR (chose Prisma over Drizzle).",
  "implement": "Phase 1-4 complete. 23 tests pass. 0 lint errors. 0 type errors.",
  "review": "0 critical, 2 warnings (missing error boundary, oversized component)."
}
```

At pipeline completion, print consolidated report from these summaries.

---

## Stall Detection

A stage is considered stalled if:
- Status is `in_progress` for >= 3 consecutive heartbeats
- The agent session has produced no new output

On stall:
1. Kill the stalled session
2. Report via `report.py --event stall`
3. Respawn the agent (counts as a retry)
4. If already retried once → mark as failed, report blocker

---

## Cron Configuration

| Job | Cron Expression | Purpose |
|-----|----------------|---------|
| Build marathon | `0 5-23 * * *` (hourly, 5AM-11PM UTC) | Main pipeline — advance phases |
| Continuous build | `0 */2 * * *` (every 2 hours) | Lighter check — stall detection |
| Graph update | `0 */8 * * *` (every 8 hours) | Rebuild graphify knowledge graph |

Configure via `openclaw/plugin.json` → `configSchema.cron`.

---

## Manual Trigger

User sends message to Dexter:
```
build: add notifications system
```

Dexter:
1. Adds to `.astra-state/queue.json` with priority 1
2. If idle → starts immediately
3. If busy → queued (picked up when current build completes)
