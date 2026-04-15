# Astra Architecture

Astra is a methodology and enforcement layer on top of AI editors. Editors provide subagents, hooks, and memory. Astra provides the structured pipeline, specialized agents, and deterministic quality gates they lack.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ASTRA                                          │
│                                                                             │
│  ┌─────────────┐   ┌──────────────┐   ┌──────────────┐   ┌─────────────┐  │
│  │  7 Agents   │   │  12 Skills   │   │  24 Checks   │   │  Pipeline   │  │
│  │  (personas) │   │ (methodology)│   │ (quality     │   │  (forge)    │  │
│  │             │   │              │   │  gates)      │   │             │  │
│  │  PM         │   │  pm-framework│   │  S1-S5 spec  │   │  scan       │  │
│  │  Designer   │   │  design-sys  │   │  D1-D5 design│   │  spec       │  │
│  │  Architect  │   │  tech-arch   │   │  P1-P4 plan  │   │  design ║   │  │
│  │  Planner    │   │  plan-tmpl   │   │  T1-T5 tech  │   │  plan   ║   │  │
│  │  Implementer│   │  impl-ptrns  │   │  I1-I4 phase │   │  architect  │  │
│  │  Reviewer   │   │  review-chk  │   │              │   │  implement  │  │
│  │  Debugger   │   │  stage-gate  │   │  Python,     │   │  review     │  │
│  │             │   │  debug-meth  │   │  no LLM      │   │  wrap-up    │  │
│  │  R/O except │   │  debt-audit  │   │              │   │             │  │
│  │  Impl + Dbg │   │  retro       │   │              │   │  zero-stop  │  │
│  │             │   │  workflow     │   │              │   │  two-strike │  │
│  └─────────────┘   └──────────────┘   └──────────────┘   └─────────────┘  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                         EDITOR ADAPTERS                                     │
│                                                                             │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐  │
│  │   Claude Code    │  │     Cursor       │  │       OpenClaw           │  │
│  │                  │  │                  │  │                          │  │
│  │  /astra:forge    │  │  /astra:forge    │  │  HEARTBEAT.md (cron)     │  │
│  │  forge.md        │  │  forge.md        │  │  AGENTS.md               │  │
│  │  + hooks.json    │  │  (no hooks)      │  │  Per-agent model routing │  │
│  │  + orchestrator/ │  │                  │  │  Aider for impl          │  │
│  │    (SDK CLI)     │  │                  │  │                          │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Pipeline Flow

Legend: `🟣 agent` `📄 artifact` `🔒 gate (deterministic)` `⚙️ action` `🔀 decision`

### Full Mode (4+ requirements or full-stack)

```
  ╔══════════════════════════════════════════════════════════════════════════════╗
  ║                                                                            ║
  ║   "add notifications system"                                               ║
  ║         │                                                                  ║
  ║         ▼                                                                  ║
  ║   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ║
  ║   ┃ ⚙️  STEP 0 — SCAN & SETUP                                         ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  Check ~/.claude/CLAUDE.md ──▶ missing? ──▶ run /astra:setup       ┃  ║
  ║   ┃  Check project CLAUDE.md   ──▶ missing? ──▶ run /astra:init        ┃  ║
  ║   ┃  Check forge-state.json ──▶ resume from last step (skip below)      ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  Load PRODUCT.md (existing features)   [skipped on resume]          ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  🔀 Knowledge graph (preferred):       [skipped on resume]          ┃  ║
  ║   ┃     graphify-out/graph.json exists? ──▶ /graphify --update          ┃  ║
  ║   ┃     no graph.json? ──▶ /graphify (full build)                       ┃  ║
  ║   ┃     graphify unavailable? ──▶ flat scan fallback below              ┃  ║
  ║   ┃  Flat scan fallback ──▶ .astra-cache/context.md                     ┃  ║
  ║   ┃               (tech stack, structure, patterns, conventions)        ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  🔀 Detect mode:                                                   ┃  ║
  ║   ┃     ≤3 reqs + single type ──▶ LITE (skip design + architect)       ┃  ║
  ║   ┃     4+ reqs or full-stack ──▶ FULL                                 ┃  ║
  ║   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  ║
  ║         │                                                                  ║
  ║         ▼                                                                  ║
  ║   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ║
  ║   ┃ 🟣 STEP 1 — PM AGENT                                 [read-only]  ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  Context: /graphify query → GRAPH_REPORT.md → context.md            ┃  ║
  ║   ┃  Skill: pm-framework (RICE, Given/When/Then)                        ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  Ask 3-5 deep questions                                             ┃  ║
  ║   ┃  Challenge assumptions, push back on scope                          ┃  ║
  ║   ┃  Produce requirements with stable IDs: R1, R2, R3...               ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  ──▶ 📄 SPEC.md                                                    ┃  ║
  ║   ┃       ├── ## Requirements (R1..Rn)                                  ┃  ║
  ║   ┃       ├── Given/When/Then per requirement                           ┃  ║
  ║   ┃       ├── RICE scores (Reach, Impact, Confidence, Effort)           ┃  ║
  ║   ┃       └── ## Non-Functional Requirements                            ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  ──▶ 🔒 GATE S1-S5                                                 ┃  ║
  ║   ┃       S1 relevance    — keywords match ≥30% reqs                    ┃  ║
  ║   ┃       S2 specificity  — no vague words in titles                    ┃  ║
  ║   ┃       S3 criteria     — ≥80% have Given/When/Then                   ┃  ║
  ║   ┃       S4 RICE         — scores present                              ┃  ║
  ║   ┃       S5 scope        — ≤10 reqs                                    ┃  ║
  ║   ┃       ┌──────────────────────────────────────┐                      ┃  ║
  ║   ┃       │ ✅ PASS ──▶ proceed                   │                      ┃  ║
  ║   ┃       │ ⚠️  WARN ──▶ auto-fix, re-eval        │                      ┃  ║
  ║   ┃       │ ❌ FAIL ──▶ fix + re-eval or STOP     │                      ┃  ║
  ║   ┃       └──────────────────────────────────────┘                      ┃  ║
  ║   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  ║
  ║         │                                                                  ║
  ║         ▼                                                                  ║
  ║   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ║
  ║   ┃ 🟣🟣 STEP 2 — DESIGN + PLAN                    ║║ PARALLEL ║║     ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  ┌─────────────────────────────┐  ┌──────────────────────────────┐  ┃  ║
  ║   ┃  │ 🔵 DESIGNER        [R/O]   │  │ 🟢 PLANNER          [R/O]   │  ┃  ║
  ║   ┃  │                             │  │                              │  ┃  ║
  ║   ┃  │ Context: query → RPT → ctx │  │ Context: query → RPT → ctx │  ┃  ║
  ║   ┃  │ Skill: design-system        │  │ Skill: plan-template        │  ┃  ║
  ║   ┃  │                             │  │                              │  ┃  ║
  ║   ┃  │ User journeys & flows       │  │ Explore codebase structure   │  ┃  ║
  ║   ┃  │ Component specs + tokens    │  │ Phase breakdown by R{n}     │  ┃  ║
  ║   ┃  │ States, a11y, responsive    │  │ Task lists + test gates     │  ┃  ║
  ║   ┃  │ D-R{n} ←→ R{n} tracing     │  │ Parallel phase detection    │  ┃  ║
  ║   ┃  │                             │  │                              │  ┃  ║
  ║   ┃  │ ──▶ 📄 DESIGN.md           │  │ ──▶ 📄 PLAN.md              │  ┃  ║
  ║   ┃  │      D-R1, D-R2...          │  │      Phase 1..N              │  ┃  ║
  ║   ┃  │                             │  │                              │  ┃  ║
  ║   ┃  │ ──▶ 🔒 GATE D1-D5          │  │ ──▶ 🔒 GATE P1-P4          │  ┃  ║
  ║   ┃  │  D1 R→D coverage            │  │  P1 R→Phase coverage        │  ┃  ║
  ║   ┃  │  D2 token usage             │  │  P2 test gate per phase     │  ┃  ║
  ║   ┃  │  D3 component states        │  │  P3 task count (1-8)        │  ┃  ║
  ║   ┃  │  D4 accessibility           │  │  P4 phase ordering          │  ┃  ║
  ║   ┃  │  D5 no orphan D-R{n}        │  │                              │  ┃  ║
  ║   ┃  └─────────────────────────────┘  └──────────────────────────────┘  ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  (asyncio.Lock protects shared state during parallel writes)        ┃  ║
  ║   ┃  LITE MODE: runs Planner only, skips Designer entirely              ┃  ║
  ║   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  ║
  ║         │                                                                  ║
  ║         ▼                                                                  ║
  ║   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ║
  ║   ┃ 🟣 STEP 3 — ARCHITECT AGENT                      [read-only]      ┃  ║
  ║   ┃ (FULL MODE ONLY — skipped in lite)                                  ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  Context: /graphify query → GRAPH_REPORT.md → context.md            ┃  ║
  ║   ┃  Skill: technical-architecture                                      ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  API contracts (endpoints, req/res schemas)                         ┃  ║
  ║   ┃  Data models (fields, types, constraints, relations)                ┃  ║
  ║   ┃  ADRs (Architecture Decision Records)                               ┃  ║
  ║   ┃  Error taxonomy, security, performance                              ┃  ║
  ║   ┃  T-R{n} ←→ R{n} tracing                                            ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  ──▶ 📄 TECHNICAL.md                                               ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  ──▶ 🔒 GATE T1-T5                                                 ┃  ║
  ║   ┃       T1 R→T coverage  T2 API completeness  T3 data models         ┃  ║
  ║   ┃       T4 error codes   T5 no route conflicts                        ┃  ║
  ║   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  ║
  ║         │                                                                  ║
  ║         ▼                                                                  ║
  ║   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ║
  ║   ┃ 🟣 STEP 4 — IMPLEMENTER AGENT                    [read-write]     ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  Context: /graphify query → GRAPH_REPORT.md → context.md            ┃  ║
  ║   ┃  Skill: implementation-patterns (test-first, phased)                ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  ┌────────────────────────────────────────────────────────────┐     ┃  ║
  ║   ┃  │                    PHASE LOOP                              │     ┃  ║
  ║   ┃  │                                                            │     ┃  ║
  ║   ┃  │  PLAN.md ──▶ skip completed phases                        │     ┃  ║
  ║   ┃  │              group parallel phases into batches            │     ┃  ║
  ║   ┃  │                                                            │     ┃  ║
  ║   ┃  │  ┌──────────────────────────────────────────────────────┐  │     ┃  ║
  ║   ┃  │  │ 📦 Phase N                                          │  │     ┃  ║
  ║   ┃  │  │                                                      │  │     ┃  ║
  ║   ┃  │  │  Write code ──▶ Write tests ──▶ Run tests            │  │     ┃  ║
  ║   ┃  │  │                                                      │  │     ┃  ║
  ║   ┃  │  │  ──▶ 🔒 GATE I1-I4                                  │  │     ┃  ║
  ║   ┃  │  │       I1 tests pass (npm test / pytest / go test)    │  │     ┃  ║
  ║   ┃  │  │       I2 lint passes (eslint / ruff)                 │  │     ┃  ║
  ║   ┃  │  │       I3 types pass (tsc / mypy)                     │  │     ┃  ║
  ║   ┃  │  │       I4 test files exist                            │  │     ┃  ║
  ║   ┃  │  │                                                      │  │     ┃  ║
  ║   ┃  │  │  ✅ PASS ──▶ mark phase complete, next phase         │  │     ┃  ║
  ║   ┃  │  │  ❌ FAIL ──▶ retry (two-strike: 2 fails = STOP)     │  │     ┃  ║
  ║   ┃  │  └──────────────────────────────────────────────────────┘  │     ┃  ║
  ║   ┃  │                                                            │     ┃  ║
  ║   ┃  │  repeat for each phase...                                  │     ┃  ║
  ║   ┃  └────────────────────────────────────────────────────────────┘     ┃  ║
  ║   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  ║
  ║         │                                                                  ║
  ║         ▼                                                                  ║
  ║   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ║
  ║   ┃ 🟣 STEP 5 — REVIEWER AGENT                       [read-only]      ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  Reads: all artifacts + code changes + SPEC.md criteria             ┃  ║
  ║   ┃  Skill: review-checklist (50+ items)                                ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  Verify Given/When/Then for each R{n}                              ┃  ║
  ║   ┃  Cross-check: code vs DESIGN.md vs TECHNICAL.md                    ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  ──▶ Findings:                                                      ┃  ║
  ║   ┃       🔴 Critical  — must fix (blocks ship)                         ┃  ║
  ║   ┃       🟡 Warning   — should fix                                     ┃  ║
  ║   ┃       🔵 Suggestion — consider                                      ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  Fix criticals ──▶ re-test ──▶ two-strike applies                  ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  Acceptance: "R1: ✅ PASS — [evidence]"                            ┃  ║
  ║   ┃              "R2: ❌ FAIL — [gap]"   ──▶ fix                       ┃  ║
  ║   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  ║
  ║         │                                                                  ║
  ║         ▼                                                                  ║
  ║   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  ║
  ║   ┃ ⚙️  STEP 6 — WRAP-UP                                              ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  Update PRODUCT.md (features, endpoints, models, conventions)       ┃  ║
  ║   ┃  Archive: SPEC ──▶ docs/specs/{slug}.md                             ┃  ║
  ║   ┃           DESIGN ──▶ docs/designs/{slug}.md                         ┃  ║
  ║   ┃           PLAN ──▶ docs/plans/{slug}.md                             ┃  ║
  ║   ┃           TECHNICAL ──▶ docs/technical/{slug}.md                    ┃  ║
  ║   ┃  /graphify --update (absorb new code into knowledge graph)          ┃  ║
  ║   ┃  Clean .astra-cache/ (NOT graphify-out/ — persists across runs)     ┃  ║
  ║   ┃  Save agent memory ──▶ docs/.agent-memory/{agent}.md                ┃  ║
  ║   ┃  Collect feedback ──▶ docs/.agent-memory/forge-feedback.md          ┃  ║
  ║   ┃                                                                     ┃  ║
  ║   ┃  Next: /astra:ship (commit + PR) or /astra:retrospective           ┃  ║
  ║   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  ║
  ║                                                                            ║
  ╚══════════════════════════════════════════════════════════════════════════════╝
```

### Lite Mode (<=3 requirements, single type)

Skips Designer (Step 2) and Architect (Step 3):

```
⚙️ Scan ──▶ 🟣 PM ──▶ 🟢 Planner ──▶ 🟣 Implementer ──▶ 🟣 Reviewer ──▶ ⚙️ Wrap-up
             🔒 S1-S5   🔒 P1-P4       🔒 I1-I4/phase
```

---

## Traceability Chain

Every requirement is traced end-to-end. Stage gates enforce each link.

```
R{n}          D-R{n}          T-R{n}          Phase          Test
SPEC.md ────▶ DESIGN.md ────▶ TECHNICAL.md ──▶ PLAN.md ────▶ Code
  │              │                │               │             │
  PM             Designer         Architect       Planner       Implementer
  │              │                │               │             │
Gate S1        Gate D1           Gate T1         Gate P1       Gate I4
(relevance)    (R→D coverage)   (R→T coverage)  (R→Phase)     (tests exist)
```

---

## Stage Gate Reference

All gates are deterministic Python (regex, counting, cross-refs). No LLM judgment.

```
Gate logic:   PASS ──▶ proceed
              WARN ──▶ auto-fix once, re-eval, proceed
              FAIL ──▶ auto-fix once, re-eval, STOP if still FAIL
```

| ID | Validates | FAIL when |
|---|---|---|
| **S1** | Feature keywords in requirements | No matches |
| **S2** | No vague words in titles | Vague words without metrics |
| **S3** | Given/When/Then criteria coverage | <50% of requirements |
| **S4** | RICE scores present | Section missing |
| **S5** | Scope (<=10 requirements) | >15 requirements |
| **D1** | R{n} → D-R{n} coverage | >=2 unmapped |
| **D2** | Design tokens (not raw hex/px) | >5 raw values |
| **D3** | Component states documented | >=2 components <3 states |
| **D4** | Accessibility (contrast + ARIA) | Both missing |
| **D5** | No orphan D-R{n} | Orphan found |
| **P1** | R{n} → Phase coverage | >=2 unmapped |
| **P2** | Test gate per phase | >=2 phases missing |
| **P3** | Task count (1-8 per phase) | Any phase >12 tasks |
| **P4** | Phase ordering (data before UI) | — (warn only) |
| **T1** | R{n} → T-R{n} coverage | >=2 unmapped |
| **T2** | API request + response schemas | Both missing |
| **T3** | Data model types + constraints | Types missing |
| **T4** | Error code taxonomy | No error section |
| **T5** | No route conflicts with PRODUCT.md | Conflicts found |
| **I1** | Tests pass | Non-zero exit |
| **I2** | Lint passes | Errors |
| **I3** | Types pass | Non-zero exit |
| **I4** | Test files exist | No test files |

---

## Agent Permissions

```
          Read-only                          Read-write
┌─────────────────────────────┐    ┌──────────────────────┐
│  PM · Designer · Architect  │    │  Implementer         │
│  Planner · Reviewer         │    │  Debugger            │
│                             │    │                      │
│  Tools: Read, Grep, Glob,  │    │  Tools: + Write,     │
│         Bash (read cmds)    │    │         Edit         │
└─────────────────────────────┘    └──────────────────────┘

Agents never talk to each other.
All data flows through artifacts: SPEC → DESIGN → PLAN → TECHNICAL → Code
All agents query graphify first (/graphify query), read full GRAPH_REPORT.md only if needed.
Orchestrator carries summaries + gate results only. Agents read full files from disk.
```

---

## Two Invocation Paths

```
             ┌──────────────────────┐       ┌──────────────────────┐
             │  /astra:forge        │       │  astra-forge CLI     │
             │  (Markdown Path)     │       │  (SDK Path)          │
             ├──────────────────────┤       ├──────────────────────┤
  Runs in    │ Claude Code / Cursor │       │ Standalone (API)     │
  Driven by  │ LLM reads forge.md  │       │ Python pipeline.py   │
  Subagents  │ Editor-native        │       │ Agent SDK query()    │
  Hooks      │ Editor-native        │       │ orchestrator/hooks.py│
  Memory     │ Editor-native        │       │ orchestrator/memory.py│
  State      │ Artifact presence    │       │ pipeline-state.json  │
  Cost       │ Subscription         │       │ API billing          │
             └──────────┬───────────┘       └──────────┬───────────┘
                        │                              │
                        └──────────┬───────────────────┘
                                   │
                    Same agents, skills, artifacts, gates
```

---

## Cross-Editor Portability

```
┌─────────────────────────────────────────────────────┐
│              PORTABLE CORE (shared)                  │
│                                                      │
│  skills/       Pure methodology, no tool refs        │
│  agents/       Logic is editor-agnostic              │
│  commands/     Pipeline steps, same everywhere       │
│  checks/       Deterministic Python                  │
└────────────┬──────────────┬──────────────┬───────────┘
             │              │              │
     ┌───────▼──────┐ ┌────▼─────┐ ┌──────▼──────────┐
     │ Claude Code  │ │  Cursor  │ │    OpenClaw      │
     │              │ │          │ │                   │
     │ .claude-     │ │ .cursor- │ │ openclaw.plugin   │
     │  plugin/     │ │  plugin/ │ │ HEARTBEAT.md      │
     │ hooks.json   │ │ (no hks) │ │ AGENTS.md         │
     │ orchestrator │ │          │ │ Per-agent models   │
     │  (SDK CLI)   │ │          │ │ Aider for impl    │
     └──────────────┘ └──────────┘ └───────────────────┘
```

---

## Runtime Files

```
graphify-out/               (persists across forge runs, enriches over time, gitignored)
├── graph.json              Knowledge graph (nodes, edges, communities)
├── GRAPH_REPORT.md         Audit report (god nodes, clusters, surprising connections)
└── graph.html              Interactive visualization

.astra-cache/               (per forge run, not committed, cleaned in Step 6)
├── context.md              Flat codebase scan (fallback when graphify unavailable)
├── forge-state.json        Checkpoint/resume + artifact summaries + gate results (lean orchestrator state)
├── pipeline-state.json     Checkpoint/resume state (SDK path only)
└── audit.jsonl             Tool use audit trail

docs/.agent-memory/         (per developer, gitignored)
└── {agent}.md              Learnings that persist across sessions

PRODUCT.md                  (committed, never archived — accumulates across runs)
```
