# Astra → OpenClaw Port: Exhaustive Change List

**Status:** Planning only — not implemented
**Date:** 2026-04-14 (updated with Astra v2 SDK orchestrator mappings)
**Context:** Port Astra's development lifecycle agents from Claude Code to OpenClaw, enabling multi-model orchestration where each agent can use the best model for its role. Reference architecture: JobCopilot cron-driven 3-phase pipeline diagram.

**Update (v2):** Astra now has a Python SDK orchestrator (`orchestrator/`) with deterministic stage-gate checks, hooks, MCP integrations, Git/Slack tools, scheduled tasks, path-scoped rules, and agent memory. Most of this Python code ports directly to OpenClaw — see Section 18.

---

## Table of Contents

1. [Architecture Differences](#1-architecture-differences)
2. [Skills (Direct Port)](#2-skills-direct-port)
3. [Plugin Manifest](#3-plugin-manifest)
4. [Agent Definitions](#4-agent-definitions)
5. [Orchestration — Forge → Dexter/HEARTBEAT](#5-orchestration--forge--dexterheartbeat)
6. [Model Routing](#6-model-routing)
7. [Tool Mapping](#7-tool-mapping)
8. [Inter-Agent Data Passing (Python Mediators)](#8-inter-agent-data-passing-python-mediators)
9. [Coder Agent — Aider Integration](#9-coder-agent--aider-integration)
10. [Graphify Integration](#10-graphify-integration)
11. [Cron / Scheduling Layer](#11-cron--scheduling-layer)
12. [Reporting Layer](#12-reporting-layer)
13. [Stage-Gate Evals in OpenClaw](#13-stage-gate-evals-in-openclaw)
14. [Install / Setup](#14-install--setup)
15. [File Structure Comparison](#15-file-structure-comparison)
16. [Migration Order](#16-migration-order)
17. [Open Questions](#17-open-questions)

---

## 1. Architecture Differences

| Aspect | Claude Code v1 (markdown) | Claude Code v2 (SDK) | OpenClaw (target) |
|---|---|---|---|
| Orchestrator | forge.md (LLM-interpreted) | `orchestrator/pipeline.py` (Python async) | Dexter + HEARTBEAT.md (cron) |
| Agent isolation | Sub-agents share parent context | `query()` per stage (fresh session) | `sessions_spawn` (fully isolated) |
| Model | All Claude (inherit) | All Claude (inherit) | Per-agent model routing |
| Tool system | Read, Write, Edit, Bash, Grep, Glob | Same + SDK hooks for enforcement | exec, browser, node, custom |
| Plugin format | `.claude-plugin/plugin.json` | Same (SDK loads it) | `openclaw.plugin.json` |
| Skill format | `skills/*/SKILL.md` | Same (shared) | Same (shared) |
| Agent format | `agents/*.md` (YAML frontmatter) | Same (parsed by `config.py`) | AGENTS.md + sub-agent configs |
| Stage-gate checks | LLM-interpreted (stage-gate skill) | Python functions (checks/*.py) | Same Python functions |
| Hooks | None | SDK callbacks + hooks.json | OpenClaw hook system |
| Permissions | Manual approval popups | `permissions.py` profiles + hooks | Per-agent workspace config |
| Context passing | Shared filesystem | Same + `PipelineState` JSON | Python mediator scripts |
| Scheduling | User-triggered | `scheduler.py` + crontab | HEARTBEAT.md + cron engine |
| Reporting | None | Slack webhook (tools/slack_tools.py) | Telegram/Discord |
| Git automation | Manual | Git tools (auto-branch, commit, PR) | Same Python tools |
| Agent memory | `memory: user` (agent frontmatter) | `memory.py` (file-based) | File-based (same) |
| Codebase context | `.astra-cache/context.md` | Same | Graphify GRAPH_REPORT.md |

---

## 2. Skills (Direct Port)

**No changes needed.** OpenClaw uses the same `SKILL.md` format with YAML frontmatter.

Copy these 11 skills as-is to OpenClaw's skills directory:

| Skill | Path | Notes |
|---|---|---|
| pm-framework | `skills/pm-framework/SKILL.md` | RICE, Given/When/Then, spec methodology |
| design-system | `skills/design-system/SKILL.md` | UI/UX methodology, tokens, components |
| technical-architecture | `skills/technical-architecture/SKILL.md` | API contracts, data models, ADRs |
| plan-template | `skills/plan-template/SKILL.md` | Phased plan structure |
| implementation-patterns | `skills/implementation-patterns/SKILL.md` | Test-first, phased execution |
| review-checklist | `skills/review-checklist/SKILL.md` | Security, perf, quality gates |
| stage-gate | `skills/stage-gate/SKILL.md` | Automated eval between stages |
| debugging-methodology | `skills/debugging-methodology/SKILL.md` | Root cause analysis |
| debt-audit | `skills/debt-audit/SKILL.md` | Tech debt assessment |
| workflow-guide | `skills/workflow-guide/SKILL.md` | Usage patterns and scenarios |
| retrospective | `skills/retrospective/SKILL.md` | Process assessment |

**One consideration:** Skills reference Claude Code tool names (Read, Write, Edit, Bash, Grep, Glob) in agent files. The skills themselves are methodology-only and don't reference specific tools — they're model-agnostic. Confirmed safe to port without changes.

---

## 3. Plugin Manifest

**Change required:** Create `openclaw.plugin.json` replacing `.claude-plugin/plugin.json`.

### Current (Claude Code)
```json
{
  "name": "astra",
  "description": "Complete development lifecycle workflow...",
  "version": "1.0.0",
  "commands": "./commands/",
  "agents": ["./agents/pm.md", ...],
  "skills": "./skills/"
}
```

### Target (OpenClaw)
```json
{
  "id": "astra",
  "configSchema": {
    "type": "object",
    "properties": {
      "models": {
        "type": "object",
        "description": "Model assignment per agent role",
        "properties": {
          "pm": { "type": "string", "default": "claude-sonnet-4-20250514" },
          "designer": { "type": "string", "default": "claude-sonnet-4-20250514" },
          "planner": { "type": "string", "default": "claude-sonnet-4-20250514" },
          "architect": { "type": "string", "default": "claude-sonnet-4-20250514" },
          "coder": { "type": "string", "default": "kimi-k2.5:cloud" },
          "reviewer": { "type": "string", "default": "claude-sonnet-4-20250514" }
        }
      },
      "reporting": {
        "type": "object",
        "properties": {
          "channel": { "type": "string", "enum": ["telegram", "discord", "none"] },
          "chatId": { "type": "string" }
        }
      },
      "mode": {
        "type": "string",
        "enum": ["full", "lite"],
        "default": "full"
      }
    }
  },
  "skills": ["./skills/"],
  "kind": "workflow"
}
```

### Fields to add
- `configSchema.properties.models` — per-agent model routing (the key differentiator)
- `configSchema.properties.reporting` — Telegram/Discord config
- `configSchema.properties.mode` — full/lite mode selection

---

## 4. Agent Definitions

**Major change.** Claude Code uses individual `agents/*.md` files with specific YAML frontmatter (`tools`, `model`, `color`, `memory`, `readonly`). OpenClaw uses workspace configs + sub-agent sessions.

### 4a. Create AGENTS.md

Define all agents in a single `AGENTS.md` file (OpenClaw workspace format):

| Agent ID | Role | Isolation | Model (configurable) | Skills |
|---|---|---|---|---|
| `product-manager` | PM — spec writing | Isolated session | configurable | pm-framework |
| `ux-designer` | UI/UX design | Isolated session | configurable | design-system |
| `planner` | Implementation planning | Isolated session | configurable | plan-template |
| `architect` | Technical design | Isolated session | configurable | technical-architecture |
| `coder` | Implementation | Isolated session | configurable (default: Aider + kimi-k2.5) | implementation-patterns |
| `reviewer` | Code review | Isolated session | configurable | review-checklist, stage-gate |
| `debugger` | Bug fixing | Isolated session | configurable | debugging-methodology |

### 4b. Per-agent workspace configs

Each agent needs a workspace config defining:
- Which model to use (from plugin config)
- Which skills to load
- Which tracked files to read/write
- Which Python mediator scripts it can call
- Whether it's read-only or read-write

### 4c. Agent instruction migration

Map each Claude Code agent `.md` content to OpenClaw sub-agent instructions:

| Claude Code file | OpenClaw equivalent | Content changes |
|---|---|---|
| `agents/pm.md` | Sub-agent `product-manager` instructions | Remove: `tools:`, `model: inherit`, `color:`, `memory:`, `readonly:`. Keep: system prompt, "Before Starting", methodology reference. Add: Python script references (`add_requirement.py`). |
| `agents/designer.md` | Sub-agent `ux-designer` instructions | Same pattern. Add: `add_design_spec.py`, `update_design_status.py` references. |
| `agents/planner.md` | Sub-agent `planner` instructions | Same pattern. Remove: read-only bash restriction (OpenClaw handles isolation differently). |
| `agents/architect.md` | Sub-agent `architect` instructions | Same pattern. |
| `agents/implementer.md` | Sub-agent `coder` instructions | Major change: replace direct Write/Edit tool usage with Aider invocation pattern. Add: `claim_requirement.py`, `get_design_spec.py`, `complete_requirement.py`. |
| `agents/reviewer.md` | Sub-agent `reviewer` instructions | Same pattern. Add: stage-gate eval execution. |
| `agents/debugger.md` | Sub-agent `debugger` instructions | Same pattern. |

### 4d. Key differences per agent

**PM agent:**
- Claude Code: Returns spec as response, forge writes SPEC.md
- OpenClaw: Writes REQUIREMENTS.md directly via `add_requirement.py` + generates PRD.md
- Change: Agent writes its own output files via mediator scripts

**Designer agent:**
- Claude Code: Returns design as response, forge writes DESIGN.md
- OpenClaw: Writes DESIGN_SPECS.md via `add_design_spec.py`
- Change: Same as PM — agent writes directly

**Coder agent:**
- Claude Code: Uses Read/Write/Edit/Bash directly
- OpenClaw: Invokes Aider as external tool, reads GRAPH_REPORT.md for context
- Change: Complete rewrite of execution — from inline coding to Aider delegation

**All agents:**
- Claude Code: `memory: user` for cross-session learning
- OpenClaw: Need equivalent — check if OpenClaw has agent memory or use `docs/.agent-memory/*.md` files

---

## 5. Orchestration — Forge → Dexter/HEARTBEAT

**Major rewrite.** Forge.md is a single synchronous orchestrator that runs in one session. In OpenClaw, this becomes Dexter (main agent) with HEARTBEAT.md for cron-driven execution.

### 5a. HEARTBEAT.md

Replaces forge.md's step-by-step flow. Runs on cron, checks state, spawns the next phase:

```
On heartbeat:
1. Read .astra-state/progress.json (which phase is current, status)
2. If no active build → check for pending feature requests → start Phase 1
3. If Phase N is "in_progress" → check if sub-agent session is done
   - Done + eval passed → advance to Phase N+1
   - Done + eval failed → retry once, then report blocker
   - Still running → do nothing (wait for next heartbeat)
   - Stalled (no progress in 2 heartbeats) → kill and respawn
4. If all phases complete → run final review → report completion
```

### 5b. State file: `.astra-state/progress.json`

New file to track pipeline state across cron invocations (forge.md doesn't need this because it runs synchronously):

```json
{
  "feature": "add notifications system",
  "mode": "full",
  "startedAt": "2026-04-13T10:00:00Z",
  "currentPhase": 2,
  "phases": [
    { "name": "pm", "status": "complete", "agentSessionId": "sess_abc", "evalResult": "pass" },
    { "name": "designer", "status": "in_progress", "agentSessionId": "sess_def", "evalResult": null },
    { "name": "planner", "status": "in_progress", "agentSessionId": "sess_ghi", "evalResult": null },
    { "name": "architect", "status": "pending", "agentSessionId": null, "evalResult": null },
    { "name": "coder", "status": "pending", "agentSessionId": null, "evalResult": null },
    { "name": "reviewer", "status": "pending", "agentSessionId": null, "evalResult": null }
  ],
  "artifacts": {
    "spec": "REQUIREMENTS.md",
    "design": "DESIGN_SPECS.md",
    "plan": "PLAN.md",
    "technical": "TECHNICAL.md"
  }
}
```

### 5c. Forge.md feature mapping

| Forge step | OpenClaw equivalent |
|---|---|
| Step 0a-0c: Prerequisites | BOOTSTRAP.md — run once on workspace init |
| Step 0d: Codebase scan → context.md | Graphify build/update → GRAPH_REPORT.md (persistent) |
| Step 0e: Resume detection | HEARTBEAT reads progress.json |
| Step 0f: Get feature description | Manual trigger or queue file |
| Step 1: PM → SPEC.md | `sessions_spawn agentId="product-manager"` → wait → eval |
| Step 2: Designer + Planner (parallel) | Spawn both: `sessions_spawn agentId="ux-designer"` + `sessions_spawn agentId="planner"` |
| Step 2 eval: DESIGN + PLAN eval | Run stage-gate S1-S5, D1-D5, P1-P4 checks via Python |
| Step 3: Architect → TECHNICAL.md | `sessions_spawn agentId="architect"` → wait → eval |
| Step 4: Implementation | `sessions_spawn agentId="coder"` (invokes Aider) → per-phase eval |
| Step 5: Final review | `sessions_spawn agentId="reviewer"` |
| Step 6: Wrap-up | Git push + Telegram report + archive artifacts |

### 5d. Parallel stage handling

Claude Code: forge.md launches Designer + Planner as parallel subagents in the same session.
OpenClaw: Spawn two separate sessions, track both in progress.json, wait for both to complete before advancing.

### 5e. Feature queue

New concept not in Astra: a queue of features to build. HEARTBEAT picks the next one when idle.

File: `.astra-state/queue.json`
```json
[
  { "feature": "add notifications", "priority": 1, "requestedAt": "..." },
  { "feature": "user settings page", "priority": 2, "requestedAt": "..." }
]
```

---

## 6. Model Routing

**New capability.** Claude Code forces all agents to use Claude (`model: inherit`). OpenClaw allows per-agent model selection.

### Recommended model assignments

| Agent | Recommended Model | Rationale |
|---|---|---|
| PM | claude-sonnet-4 or gpt-4o | Strong at structured analysis, requirement writing |
| Designer | claude-sonnet-4 | Best at detailed component specs with tokens |
| Planner | claude-sonnet-4 or gemini-2.5-pro | Good at codebase analysis and phased planning |
| Architect | claude-sonnet-4 or claude-opus-4 | Needs deep technical reasoning for ADRs, API design |
| Coder | kimi-k2.5 via Aider (or any Aider-supported model) | Cost-effective for code generation, Aider handles the interaction |
| Reviewer | claude-sonnet-4 | Good at spotting security/correctness issues |
| Debugger | claude-opus-4 | Deep reasoning needed for root cause analysis |

### Implementation

- Models configured in `openclaw.plugin.json` configSchema
- Dexter reads config, passes model to `sessions_spawn`
- Each sub-agent session uses its assigned model
- User can override per-agent in workspace config

---

## 7. Tool Mapping

Map Claude Code tools to OpenClaw equivalents:

| Claude Code Tool | OpenClaw Equivalent | Notes |
|---|---|---|
| `Read` | `exec` (cat/head) or native file read | OpenClaw's exec tool runs shell commands |
| `Write` | `exec` (tee/cat >) or native file write | |
| `Edit` | `exec` (sed/patch) or Aider | For coder agent, Aider handles edits |
| `Bash` | `exec` | Direct mapping |
| `Grep` | `exec` (grep/rg) | |
| `Glob` | `exec` (find/fd) | |

### Tool changes needed in agent instructions

- Replace `Read file.md` → `exec "cat file.md"`
- Replace `Write file.md content` → `exec "cat > file.md << 'EOF'\ncontent\nEOF"`
- Replace `Grep pattern` → `exec "rg 'pattern'"`
- Or: define custom OpenClaw tools that wrap these (cleaner approach)

### Custom tools to create

Consider creating thin OpenClaw tool wrappers:

| Tool Name | Wraps | Purpose |
|---|---|---|
| `read_artifact` | cat + parse | Read and validate an Astra artifact (SPEC.md, DESIGN.md, etc.) |
| `write_artifact` | write + validate | Write an artifact with structural validation |
| `run_eval` | Python script | Execute stage-gate eval checks |
| `check_progress` | read progress.json | Query pipeline state |

---

## 8. Inter-Agent Data Passing (Python Mediators)

**New layer.** In Claude Code, agents share filesystem context (forge writes SPEC.md, designer reads it). In OpenClaw with isolated agents, Python scripts mediate data flow.

### Scripts to create

Based on the reference architecture diagram + Astra's artifact flow:

| Script | Purpose | Called by | Reads | Writes |
|---|---|---|---|---|
| `init_requirements.py` | Initialize REQUIREMENTS.md from feature description | Dexter | queue.json | REQUIREMENTS.md (skeleton) |
| `add_requirement.py` | Add/update a requirement in REQUIREMENTS.md | PM agent | REQUIREMENTS.md | REQUIREMENTS.md |
| `generate_summary.py` | Generate PRD.md from requirements | PM agent | REQUIREMENTS.md | PRD.md |
| `add_design_spec.py` | Add UI spec for a requirement | Designer agent | REQUIREMENTS.md | DESIGN_SPECS.md |
| `update_design_status.py` | Mark design complete for a requirement | Designer agent | DESIGN_SPECS.md | DESIGN_SPECS.md |
| `list_available_work.py` | List requirements ready for implementation | Coder agent | REQUIREMENTS.md, DESIGN_SPECS.md | stdout |
| `claim_requirement.py` | Mark a requirement as "in progress" | Coder agent | REQUIREMENTS.md | REQUIREMENTS.md |
| `get_design_spec.py` | Get design spec for a specific requirement | Coder agent | DESIGN_SPECS.md | stdout |
| `complete_requirement.py` | Mark requirement as "implemented" | Coder agent | REQUIREMENTS.md | REQUIREMENTS.md |
| `run_stage_eval.py` | Run stage-gate eval (S/D/P/T/I checks) | Dexter | Artifacts | eval_result.json |
| `update_progress.py` | Update pipeline state | Dexter | progress.json | progress.json |

### Artifact file mapping

| Astra artifact | OpenClaw equivalent | Format change? |
|---|---|---|
| SPEC.md | REQUIREMENTS.md + PRD.md | Yes — split into structured tracker + narrative |
| DESIGN.md | DESIGN_SPECS.md | Minor — add status tracking per requirement |
| PLAN.md | PLAN.md | No change |
| TECHNICAL.md | TECHNICAL.md | No change |
| PRODUCT.md | COMPLETION_CHECKLIST.md + PRD.md | Split into checklist + narrative |
| `.astra-cache/context.md` | `graphify-out/GRAPH_REPORT.md` | Replace flat cache with Graphify output |

### Key difference: structured tracking

Astra's SPEC.md is a free-form markdown document. The OpenClaw version (REQUIREMENTS.md) is a **structured tracker** with per-requirement status:

```markdown
### R1: Push notifications
- **Status:** implemented | in_progress | designed | specced | pending
- **Priority:** P1
- **RICE:** 8.0
- **Assigned to:** coder (session_xyz)
- **Design:** complete (DESIGN_SPECS.md#R1)
- **Technical:** complete (TECHNICAL.md#T-R1)
```

This enables the mediator scripts to query/update individual requirements programmatically — essential for isolated agents that can't read the full pipeline state.

---

## 9. Coder Agent — Aider Integration

**Major change.** Astra's implementer agent writes code directly using Claude's Write/Edit tools. In OpenClaw, the coder agent delegates to Aider.

### How it works

1. Coder agent reads GRAPH_REPORT.md (Graphify context)
2. Calls `claim_requirement.py` to pick next requirement
3. Calls `get_design_spec.py` for UI specs
4. Reads TECHNICAL.md for API contracts, data models
5. Invokes Aider with the task:
   ```bash
   aider --model kimi-k2.5:cloud \
         --message "Implement T-R1: POST /api/notifications endpoint. 
                    Follow spec in TECHNICAL.md. Use existing patterns from GRAPH_REPORT.md." \
         --file src/api/notifications.ts \
         --file src/models/notification.ts
   ```
6. Aider makes the edits
7. Coder agent runs tests: `exec "npm test -- --grep notification"`
8. If pass → `complete_requirement.py`
9. If fail → Aider fix cycle (max 2 attempts)

### Aider configuration

- Model: configurable (default `kimi-k2.5:cloud` per reference architecture)
- Pointed at project root
- Receives specific file list per requirement (not whole project)
- Uses `--message` mode (non-interactive)

### implementation-patterns skill adaptation

The skill is methodology-only and doesn't reference tools. However, sections that assume direct file editing need notes:

| Skill section | Adaptation |
|---|---|
| "Pattern Discovery" | Coder reads GRAPH_REPORT.md instead of scanning files |
| "Test-First" | Coder writes test via Aider first, then implementation |
| "Code Quality Gates" | Coder runs tests/lint/types via exec after Aider edits |
| "Phased Execution" | Same — claim one requirement at a time, complete before next |

---

## 10. Graphify Integration

**Replaces `.astra-cache/context.md`** with a persistent, queryable knowledge graph. Same role across all three editor targets — Claude Code uses the `/graphify` skill, Cursor uses the same skill, OpenClaw uses the CLI directly.

### Installation in OpenClaw

Add to BOOTSTRAP.md workspace setup (runs once):
```bash
pip install graphifyy --quiet
```

OpenClaw agents invoke graphify via CLI commands (`graphify query "..."`, `graphify . --update`), not via `/graphify` skill syntax (which is Claude Code/Cursor specific). The Python package provides both the CLI and the library.

### Pipeline integration

| Pipeline step | Graphify action | Fallback |
|---|---|---|
| **HEARTBEAT init** (before first agent) | `graphify-out/graph.json` exists? → `graphify . --update` : `graphify . --no-viz` | Skip graph, agents scan manually (degraded) |
| **After coder completes** | `graphify . --update` (code-only → AST only, no LLM, fast) | Skip — graph stays stale until next heartbeat |
| **Stale graph (>24h)** | HEARTBEAT triggers `graphify . --update` | — |
| **After git pull** | `graphify . --update` (detect changed files via manifest) | — |

### Usage per agent

Agents use **query-first** pattern: CLI query for targeted context first, read full `GRAPH_REPORT.md` only if query returns insufficient results:

| Agent | CLI query (first) | Full GRAPH_REPORT.md | Budget |
|---|---|---|---|
| **PM** | `graphify query "existing features and user flows"` | Only if query insufficient | `--budget 600` |
| **Designer** | `graphify query "UI components, design tokens, CSS patterns"` | Only if query insufficient | `--budget 800` |
| **Planner** | `graphify query "project structure, dependencies, test patterns"` | Only if query insufficient | `--budget 500` |
| **Architect** | `graphify query "API routes, data models, auth, error handling"` | Only if query insufficient | `--budget 800` |
| **Coder** | `graphify query "TargetModule" --dfs` for call chains | Only if query insufficient | — |
| **Reviewer** | `graphify query "recent changes and affected modules"` | Only if query insufficient | `--budget 600` |
| **Debugger** | `graphify query "ErrorModule" --dfs` for call paths | Only if query insufficient | `--budget 600` |

### Graph rebuild triggers

| Trigger | When | What runs | LLM cost |
|---|---|---|---|
| Coder completes a requirement | After implementation phase | `graphify . --update` | None (code-only = AST) |
| External changes | After `git pull` | `graphify . --update` | Only if docs/images changed |
| Stale timer | HEARTBEAT detects >24h since last update | `graphify . --update` | Depends on changes |
| `astra-graph-update` cron | Every 8h (see Section 11) | `graphify . --update` | Depends on changes |

### Error handling

- **graphify not installed:** Skip graph, log warning. Agents fall back to manual codebase scanning (slower, no cross-file relationships).
- **graphify fails mid-build:** Use stale `graph.json` from previous run if available. Log error, don't block pipeline.
- **Empty graph (new project, no code yet):** GRAPH_REPORT.md will be minimal. Agents supplement with targeted file reads.
- **Large codebase (>200 files):** graphify auto-warns and suggests running on a subdirectory. HEARTBEAT should scope to `src/` or primary source directory.

### Key differences from Claude Code / Cursor

| Aspect | Claude Code / Cursor | OpenClaw |
|---|---|---|
| Invocation | `/graphify` skill (LLM-interpreted) | `graphify` CLI (direct subprocess) |
| Agent context | Agents read GRAPH_REPORT.md from filesystem | Agents read GRAPH_REPORT.md as tracked file |
| Queries | `/graphify query "..."` (skill call) | `graphify query "..."` (CLI) |
| Rebuild trigger | forge.md Step 0 and Step 6 | HEARTBEAT.md + cron job |
| Install | Skill auto-installs `pip install graphifyy` | BOOTSTRAP.md runs `pip install graphifyy` |

---

## 11. Cron / Scheduling Layer

**New layer.** Astra is user-triggered. OpenClaw version is cron-driven.

### Cron schedules

| Job | Schedule | Purpose |
|---|---|---|
| `astra-build-marathon` | Every hour 5AM-11PM UTC | Main build pipeline — check progress, advance phases |
| `astra-continuous-build` | Every 2 hours | Lighter check — just verify nothing is stalled |
| `astra-graph-update` | Every 8 hours | Rebuild Graphify graph for fresh context |

### HEARTBEAT.md logic

```
Priority 1: Active build
  - Check progress.json for active feature
  - If phase agent stalled (no progress in 2 heartbeats) → kill + respawn
  - If phase agent done → run eval → advance or retry

Priority 2: Queue processing
  - If no active build → check queue.json
  - If queue non-empty → start next feature

Priority 3: Health check
  - Git status (uncommitted changes?)
  - Test suite pass?
  - Graph staleness?
```

### Manual trigger

Besides cron, support manual trigger:
- User sends message to Dexter: "build: add notifications system"
- Dexter adds to queue, starts immediately if idle

---

## 12. Reporting Layer

**UPDATE (v2):** Astra now has `orchestrator/tools/slack_tools.py` with `notify_pipeline_event()`. For OpenClaw, swap Slack webhook for Telegram Bot API — same function signature, different HTTP endpoint.

### Report types

| Report | When | Content |
|---|---|---|
| Phase start | When a new phase begins | "Phase 2/6: UX Designer started for 'notifications'" |
| Phase complete | When eval passes | "Phase 2/6: Design complete. 5/5 eval checks passed." |
| Phase failure | When eval fails after retry | "Phase 3 BLOCKED: T-R2 missing API schema. Needs input." |
| Build complete | All phases done | Full summary: requirements implemented, test results, completion % |
| Stall alert | Agent stalled 2+ heartbeats | "Coder agent stalled on R3. Respawning." |
| Daily digest | Once per day | Progress across all active features |

### Implementation

- Create `scripts/report.py` that sends messages via Telegram Bot API or Discord webhook
- Dexter calls `report.py` at each transition point
- Channel config comes from `openclaw.plugin.json`

---

## 13. Stage-Gate Checks in OpenClaw

**UPDATE (v2): All checks are now implemented as Python functions in `orchestrator/checks/`.** These port directly to OpenClaw with zero changes — they're pure Python with no SDK dependency.

### Current (Astra v2)

Python check functions in `orchestrator/checks/`:
- `spec_checks.py` — S1-S5 (regex, counting, keyword match)
- `design_checks.py` — D1-D5 (cross-reference, raw value scan, state count)
- `plan_checks.py` — P1-P4 (coverage, test gates, task count, dependency order)
- `tech_checks.py` — T1-T5 (coverage, API completeness, models, error codes)
- `phase_checks.py` — I1-I4 (subprocess: tests, lint, types)

### Target (OpenClaw)

Copy `orchestrator/checks/` as-is. Call from HEARTBEAT.md or Dexter via `exec` tool:
```bash
python3 -m orchestrator.checks.spec_checks --spec SPEC.md --feature "notifications"
```

These are the same checks listed below (kept for reference):

| Eval | Can be scripted? | Approach |
|---|---|---|
| S1: Relevance (keyword match) | Yes | Python: extract keywords from feature desc, check requirement titles |
| S2: Specificity (banned words) | Yes | Python: regex scan for banned vague words |
| S3: Criteria (Given/When/Then) | Yes | Python: regex for Given/When/Then blocks per R{n} |
| S4: RICE scores | Yes | Python: check RICE fields exist per requirement |
| S5: Scope (requirement count) | Yes | Python: count R{n} entries |
| D1: R→D coverage | Yes | Python: cross-reference R{n} and D-R{n} IDs |
| D2: Token usage | Partial | Python: regex for raw hex/px values |
| D3: States count | Partial | Python: count state keywords per component |
| D4: Accessibility | Partial | Python: check for contrast/keyboard/ARIA sections |
| D5: Orphans | Yes | Python: D-R{n} IDs not in SPEC requirements |
| P1-P4 | Mostly yes | Python: cross-reference, count tasks, check test gates |
| T1-T5 | Mostly yes | Python: cross-reference, check schemas, validate formats |
| I1: Tests pass | Yes | `exec "npm test"` |
| I2: Lint | Yes | `exec "npm run lint"` |
| I3: Types | Yes | `exec "tsc --noEmit"` |
| I4: Criteria spot-check | No | Needs LLM to verify test matches criterion |

### Script: `scripts/run_stage_eval.py`

```
Usage: python scripts/run_stage_eval.py --stage spec|design|plan|technical|phase
Reads: relevant artifact files
Outputs: eval_result.json with pass/warn/fail per check
```

**Key benefit:** Most evals become deterministic Python checks instead of LLM calls. Saves tokens, runs faster, more reliable.

---

## 14. Install / Setup

### New installer

Create `install-openclaw.sh` alongside existing `install.sh`:

| Step | Action |
|---|---|
| 1 | Check OpenClaw is installed (`which openclaw`) |
| 2 | Clone/update Astra repo to `~/astra` |
| 3 | Copy skills to `~/.openclaw/workspace/skills/astra/` |
| 4 | Copy `openclaw.plugin.json` to workspace |
| 5 | Copy `AGENTS.md` to workspace |
| 6 | Copy `HEARTBEAT.md` to workspace |
| 7 | Copy `scripts/*.py` to workspace |
| 8 | Install Python dependencies (`pip install graphifyy`) |
| 9 | Configure cron jobs (or let OpenClaw cron engine handle it) |
| 10 | Prompt user for Telegram/Discord config (optional) |
| 11 | Prompt user for model preferences per agent |

### Dual installer

Update main `install.sh` to detect environment:
```bash
if command -v claude &>/dev/null; then
  install_claude_code
fi
if command -v openclaw &>/dev/null; then
  install_openclaw
fi
```

---

## 15. File Structure Comparison

### Current (Claude Code)

```
astra/
├── .claude-plugin/plugin.json
├── .cursor-plugin/plugin.json
├── commands/
│   ├── forge.md          (orchestrator)
│   ├── spec.md, design.md, plan.md, architect.md
│   ├── implement.md, review.md, ship.md
│   ├── debug.md, compound.md, debt-audit.md
│   ├── setup.md, init.md
│   ├── workflow-guide.md, retrospective.md
├── agents/
│   ├── pm.md, designer.md, planner.md
│   ├── architect.md, implementer.md
│   ├── reviewer.md, debugger.md
├── skills/
│   ├── pm-framework/SKILL.md
│   ├── design-system/SKILL.md
│   ├── ... (11 total)
├── install.sh
└── README.md
```

### Target (OpenClaw)

```
astra/
├── openclaw.plugin.json
├── AGENTS.md                    (all agent definitions)
├── HEARTBEAT.md                 (cron-driven orchestration)
├── BOOTSTRAP.md                 (first-run setup)
├── SOUL.md                      (Dexter personality/instructions)
├── skills/                      (direct port — no changes)
│   ├── pm-framework/SKILL.md
│   ├── design-system/SKILL.md
│   ├── ... (11 total)
├── scripts/                     (new — Python mediators)
│   ├── init_requirements.py
│   ├── add_requirement.py
│   ├── generate_summary.py
│   ├── add_design_spec.py
│   ├── update_design_status.py
│   ├── list_available_work.py
│   ├── claim_requirement.py
│   ├── get_design_spec.py
│   ├── complete_requirement.py
│   ├── run_stage_eval.py
│   ├── update_progress.py
│   ├── report.py
├── templates/                   (artifact templates)
│   ├── REQUIREMENTS.template.md
│   ├── DESIGN_SPECS.template.md
│   ├── PLAN.template.md
│   ├── TECHNICAL.template.md
├── .claude-plugin/plugin.json   (keep — Claude Code support)
├── .cursor-plugin/plugin.json   (keep — Cursor support)
├── commands/                    (keep — Claude Code support)
├── agents/                      (keep — Claude Code support)
├── install.sh                   (update — detect both platforms)
└── README.md                    (update — document both platforms)
```

---

## 16. Migration Order

Suggested phased implementation:

### Phase 1: Skills + Manifest (low risk)
1. Create `openclaw.plugin.json`
2. Copy skills to OpenClaw workspace
3. Create `BOOTSTRAP.md` for first-run setup
4. Verify skills load correctly in OpenClaw

### Phase 2: Single-agent test (PM only)
5. Create PM sub-agent config in AGENTS.md
6. Create `init_requirements.py` and `add_requirement.py`
7. Test: spawn PM agent, produce REQUIREMENTS.md
8. Create `run_stage_eval.py` with SPEC eval (S1-S5)
9. Verify eval runs correctly

### Phase 3: Full pipeline (sequential)
10. Add Designer, Planner, Architect sub-agent configs
11. Create remaining mediator scripts
12. Create HEARTBEAT.md with sequential phase execution
13. Test full pipeline: PM → Designer → Planner → Architect → manual coding
14. Verify stage-gate evals at each transition

### Phase 4: Coder + Aider
15. Configure Aider integration
16. Create coder sub-agent that invokes Aider
17. Test: coder receives specs, produces code via Aider
18. Integrate Graphify for codebase context

### Phase 5: Automation
19. Set up cron schedules
20. Add Telegram/Discord reporting
21. Implement feature queue
22. Test full autonomous loop

### Phase 6: Polish
23. Update install.sh for dual-platform detection
24. Update README with OpenClaw documentation
25. Test on a real project end-to-end
26. Performance benchmarking: tokens used, time per phase, success rate

---

## 17. Open Questions

1. **OpenClaw agent memory** — Does OpenClaw have cross-session agent memory like Claude Code's `memory: user`? If not, use `docs/.agent-memory/*.md` file-based approach.

2. **Sub-agent session management** — How long do OpenClaw sessions persist? Can Dexter check if a session is still running? What happens if a session crashes?

3. **Model availability** — Which models are available in OpenClaw? Is kimi-k2.5 accessible? What about Gemini, GPT-4o, local Ollama models?

4. **Aider compatibility** — Does Aider work well with all the models? Some models may not follow Aider's edit format correctly. Need to test.

5. **Graphify in OpenClaw** — Is graphify already a ClawHub skill, or does it need separate installation? The reference architecture shows it integrated — confirm the exact integration path.

6. **Parallel sub-agents** — Can OpenClaw spawn multiple sub-agents simultaneously? Critical for Designer + Planner parallel execution.

7. **Cost tracking** — Can we track token usage per agent per model? Important for optimizing model assignments.

8. **Artifact format** — Should we keep Astra's free-form markdown artifacts (SPEC.md, DESIGN.md) or switch to the structured tracker format (REQUIREMENTS.md with per-requirement status)? The structured format enables scripted evals but is less flexible.

9. **Backward compatibility** — Should the OpenClaw version maintain the same artifact format as Claude Code version so you can switch between them on the same project?

10. **ClawHub publishing** — Should Astra be published as a ClawHub skill/plugin for the community?

11. **Parallel feature runs (known limitation — revisit during OpenClaw port)** — Astra's current design assumes one active forge run at a time. All runs share a single `.astra-cache/` directory (no namespacing) and a single `graphify-out/graph.json`. Running two forge runs in parallel on the same project will cause:
    - `.astra-cache/` file overwrites (context.md, spec.md, design.md stomped by second run)
    - `graph.json` race condition if both runs call `/graphify --update` simultaneously
    - Stage gates checking wrong artifacts (Feature B's content evaluated against Feature A's gates)
    - No cross-run conflict detection (both features may touch the same files with no warning until git merge)
    
    **When to fix:** When OpenClaw port begins, scope `.astra-cache/` by branch or run ID (e.g., `.astra-cache/feature-auth/`). Add a planner step that runs `git diff main` against other active branches to surface conflict surface area before implementation. The cron/HEARTBEAT model in OpenClaw naturally serialises runs, so this may be less urgent there — but worth designing for explicitly. Until then, the safe workflow is sequential forge runs on separate git branches, merging between each.

---

## 18. Astra v2 SDK → OpenClaw Mapping (NEW)

Astra v2 introduced a Python SDK orchestrator (`orchestrator/`) with hooks, checks, tools, scheduled tasks, and agent memory. This section maps every v2 component to its OpenClaw equivalent.

### What Ports Directly (zero changes)

| Astra v2 Component | File(s) | OpenClaw Usage |
|---|---|---|
| All 11 skills | `skills/*/SKILL.md` | Copy to OpenClaw skills directory |
| Spec checks (S1-S5) | `orchestrator/checks/spec_checks.py` | Call via `exec` or import |
| Design checks (D1-D5) | `orchestrator/checks/design_checks.py` | Call via `exec` or import |
| Plan checks (P1-P4) | `orchestrator/checks/plan_checks.py` | Call via `exec` or import |
| Tech checks (T1-T5) | `orchestrator/checks/tech_checks.py` | Call via `exec` or import |
| Phase checks (I1-I4) | `orchestrator/checks/phase_checks.py` | Call via `exec` or import |
| Check base classes | `orchestrator/checks/base.py` | Import directly |
| Git tools | `orchestrator/tools/git_tools.py` | Call directly (pure asyncio+subprocess) |
| Agent memory | `orchestrator/memory.py` | Import directly (pure file I/O) |
| Pipeline state | `orchestrator/state.py` | Import directly (Pydantic model) |
| Config loader | `orchestrator/config.py` | Adapt: change ASTRA_PLUGIN_DIR to OpenClaw paths |
| Path-scoped rules | `rules/*.md` | Copy to OpenClaw workspace rules |

### What Needs Adaptation

| Astra v2 Component | File(s) | OpenClaw Adaptation |
|---|---|---|
| Pipeline orchestrator | `orchestrator/pipeline.py` | Replace `query()` calls with `sessions_spawn`. Replace `asyncio.gather()` with parallel session tracking. Replace `ClaudeAgentOptions` with OpenClaw workspace config. |
| Stage base class | `orchestrator/stages/base.py` | Replace `query()` + `ClaudeAgentOptions` with OpenClaw sub-agent spawning pattern. Keep `build_prompt()` logic. |
| Stage definitions | `orchestrator/stages/*.py` | Keep `build_prompt()` methods. Replace `run()` with OpenClaw `sessions_spawn` + output capture. |
| SDK hooks | `orchestrator/hooks.py` | Replace SDK callback pattern with OpenClaw hook system. `enforce_readonly` → OpenClaw tool restrictions per agent. `audit_trail` → OpenClaw PostToolUse hook. |
| Permissions | `orchestrator/permissions.py` | Map `PermissionProfile` to OpenClaw per-agent workspace tool configs. |
| Plugin hooks | `hooks/hooks.json` | Replace with OpenClaw hook format (check OpenClaw docs for exact schema). |
| Slack tools | `orchestrator/tools/slack_tools.py` | Swap webhook URL for Telegram Bot API. Function signature stays the same. |
| MCP config | `orchestrator/mcp.py` | Replace `ClaudeAgentOptions.mcp_servers` with OpenClaw tool registration. |
| Scheduler | `orchestrator/scheduler.py` | Replace crontab management with OpenClaw cron engine (HEARTBEAT.md). |
| CLI | `orchestrator/__main__.py` | Replace with OpenClaw command/trigger (Dexter message or cron). |

### Key Insight: Effort Reduction from v2

Before v2, porting to OpenClaw required writing all check logic, git tools, state management, and reporting from scratch. Now:

| Component | Before v2 (estimated) | After v2 (port effort) |
|---|---|---|
| Stage-gate checks | Write from scratch (~5 days) | Copy as-is (0 days) |
| Git automation | Write from scratch (~2 days) | Copy as-is (0 days) |
| Agent memory | Write from scratch (~1 day) | Copy as-is (0 days) |
| Pipeline state | Write from scratch (~2 days) | Copy, adapt spawn calls (~1 day) |
| Reporting | Write from scratch (~2 days) | Swap Slack→Telegram (~0.5 days) |
| Orchestration | Write HEARTBEAT.md (~3 days) | Adapt pipeline.py → HEARTBEAT (~2 days) |
| **Total** | **~15 days** | **~3.5 days** |

The v2 Python code is the shared foundation. Only the SDK-specific integration layer (how agents are spawned, how permissions are enforced) needs to be rewritten for OpenClaw.

### Updated Migration Order (accounting for v2)

#### Phase 1: Copy shared code (0.5 days)
1. Copy `skills/` → OpenClaw skills directory
2. Copy `orchestrator/checks/` → OpenClaw scripts
3. Copy `orchestrator/tools/git_tools.py` → OpenClaw scripts
4. Copy `orchestrator/memory.py` → OpenClaw scripts
5. Copy `orchestrator/state.py` → OpenClaw scripts
6. Copy `rules/` → OpenClaw workspace rules
7. Verify imports work outside the SDK

#### Phase 2: Adapt orchestration (2 days)
8. Create AGENTS.md from `agents/*.md` (convert YAML frontmatter to OpenClaw format)
9. Create HEARTBEAT.md adapting `pipeline.py` logic to OpenClaw's cron pattern
10. Adapt `stages/*.py` — keep prompts, replace `query()` with `sessions_spawn`
11. Wire checks into HEARTBEAT between-phase transitions

#### Phase 3: Wire tools + reporting (1 day)
12. Swap `slack_tools.py` webhook → Telegram Bot API
13. Wire `git_tools.py` into HEARTBEAT wrap-up phase
14. Configure Aider for coder agent

#### Phase 4: Test + polish (1-2 days)
15. Test full pipeline on a real project
16. Performance benchmark
17. Update README

### Updated Open Questions (v2 resolves several)

| # | Original Question | Status |
|---|---|---|
| 1 | Agent memory approach | **Resolved** — `memory.py` uses file-based approach, works on any platform |
| 6 | Parallel sub-agents | **Partially resolved** — `pipeline.py` uses `asyncio.gather()`, OpenClaw needs equivalent |
| 7 | Cost tracking | **Partially resolved** — `audit.jsonl` logs all tool calls, needs token counting added |
| 8 | Artifact format | **Resolved** — Keep Astra's free-form markdown artifacts (used by v2 checks) |
| 9 | Backward compatibility | **Resolved** — Both Claude Code paths (markdown + SDK) share artifacts with OpenClaw |

Remaining open: questions 2 (session management), 3 (model availability), 4 (Aider compatibility), 5 (Graphify integration), 10 (ClawHub publishing).
