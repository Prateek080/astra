# Astra → OpenClaw Port: Implementation Plan

**Source:** `docs/openclaw-port-plan.md` (design doc, April 14 2026)
**Updated:** 2026-06-03 — incorporates all v2 SDK enhancements (graphify, lean orchestrator, audit trail, permissions, MCP, agent memory, nightly forge, resume/checkpoint)

**Isolation:** All OpenClaw files live under `openclaw/` subdirectory to avoid side effects on Claude Code Astra. Shared code (`orchestrator/checks/`, `skills/`) stays in place and is referenced by path. Existing Claude Code files (`commands/`, `agents/`, `install.sh`, `README.md`) are **never modified**.

---

## Phase 1: Plugin Manifest + Artifact Templates — **Status: complete**

**Parallel: no**

### What
- Create `openclaw/plugin.json` with `configSchema` for per-agent model routing, reporting channel, mode selection
- Create `openclaw/templates/` directory with structured artifact templates (REQUIREMENTS, DESIGN_SPECS, PLAN, TECHNICAL)

### Files to create
- `openclaw/plugin.json`
- `openclaw/templates/REQUIREMENTS.template.md`
- `openclaw/templates/DESIGN_SPECS.template.md`
- `openclaw/templates/PLAN.template.md`
- `openclaw/templates/TECHNICAL.template.md`

### Key decisions
- Model defaults: PM/Designer/Planner/Architect/Reviewer → claude-sonnet-4, Coder → kimi-k2.5:cloud, Debugger → claude-opus-4
- REQUIREMENTS.template.md uses structured per-requirement status tracking (Status, Priority, RICE, Assigned, Design link, Technical link)
- Templates enable Python mediator scripts to parse/update requirements programmatically

### Test gate
- [ ] `python -c "import json; json.load(open('openclaw/plugin.json'))"` passes
- [ ] All 4 template files exist in `openclaw/templates/` and contain placeholder markers
- [ ] configSchema has models, reporting, mode fields

---

## Phase 2: Agent Definitions — **Status: complete**

**Parallel: no**

### What
- Create `AGENTS.md` — all 7 agents ported from `agents/*.md` to OpenClaw workspace format
- Create `SOUL.md` — Dexter (main orchestrator agent) personality and instructions
- Create `BOOTSTRAP.md` — first-run workspace setup (graphify, deps, git config)

### Files to create
- `openclaw/AGENTS.md`
- `openclaw/SOUL.md`
- `openclaw/BOOTSTRAP.md`

### Port mapping (from Claude Code agents)
| Source | Target | Key changes |
|--------|--------|-------------|
| `agents/pm.md` | `product-manager` in AGENTS.md | Remove YAML frontmatter (tools/model/color/readonly). Keep system prompt. Add mediator script refs. |
| `agents/designer.md` | `ux-designer` in AGENTS.md | Same pattern. Add `add_design_spec.py` refs. |
| `agents/planner.md` | `planner` in AGENTS.md | Same. Remove read-only bash restriction. |
| `agents/architect.md` | `architect` in AGENTS.md | Same. |
| `agents/implementer.md` | `coder` in AGENTS.md | Major: replace Write/Edit with Aider invocation. Add `claim_requirement.py`, `complete_requirement.py`. |
| `agents/reviewer.md` | `reviewer` in AGENTS.md | Same. Add stage-gate eval execution via `run_stage_eval.py`. |
| `agents/debugger.md` | `debugger` in AGENTS.md | Same. |

### Enhancements from v2
- Agent memory: `docs/.agent-memory/{agent}.md` — port `memory.py` pattern
- Graphify: query-first pattern in agent instructions (`graphify query "topic"` before full report)
- Permission profiles: map `permissions.py` AGENT_PROFILES to OpenClaw per-agent workspace configs
- Audit trail: OpenClaw PostToolUse hook for write logging

### Test gate
- [ ] AGENTS.md contains all 7 agent definitions
- [ ] SOUL.md references HEARTBEAT.md state machine and mediator scripts
- [ ] BOOTSTRAP.md includes graphify install, git config, dependency check

---

## Phase 3: HEARTBEAT.md Orchestration — **Status: complete**

**Parallel: no**

### What
Port `commands/forge.md` + `orchestrator/pipeline.py` logic to OpenClaw's cron-driven HEARTBEAT.md format.

### Files to create
- `openclaw/HEARTBEAT.md`

### State machine (from pipeline.py)
```
idle → scan → spec → [design+plan parallel] → architect → implement → review → wrapup → idle
```

### Features to port from v2
| v2 Feature | HEARTBEAT equivalent |
|------------|---------------------|
| `PipelineState` (state.py) | `.astra-state/progress.json` — read/write via `update_progress.py` |
| `_run_codebase_scan()` | Graphify update step: `graphify . --update` |
| `_detect_mode()` | Mode detection after spec: req count + frontend/backend heuristic |
| `_run_stage_with_retry()` | Two-strike retry: run agent, if fail retry once, then report blocker |
| `asyncio.gather()` parallel | Spawn Designer + Planner sessions simultaneously, track both |
| `_run_gate()` | Call `run_stage_eval.py --stage {name}` between phases |
| `_mark_stage_done()` | Call `update_progress.py --stage {name} --status complete` |
| `_archive_artifacts()` | Copy artifacts to `docs/{type}/` with timestamp |
| `create_feature_branch()` | Git branch creation via exec |
| `create_pr()` | PR creation via exec + gh CLI |
| Lean orchestrator | Save 2-3 line summaries per stage, not full artifacts |
| Consolidated run summary | Print structured report reading progress.json at completion |
| Nightly forge / backlog.md | Feature queue: `.astra-state/queue.json` + backlog.md support |
| Agent memory | Call `save_agent_memory()` after each stage |
| Slack notifications | Call `report.py` for Telegram/Discord |

### Cron schedules
| Job | Schedule | Purpose |
|-----|----------|---------|
| `astra-build-marathon` | Every hour 5AM-11PM UTC | Main pipeline — check progress, advance phases |
| `astra-continuous-build` | Every 2 hours | Lighter check — verify nothing is stalled |
| `astra-graph-update` | Every 8 hours | Rebuild graphify graph |

### Test gate
- [ ] HEARTBEAT.md covers all 8 stages (scan, spec, design, plan, architect, implement, review, wrapup)
- [ ] References all mediator scripts from Phase 4
- [ ] Includes resume logic (read progress.json, skip completed stages)
- [ ] Includes parallel design+plan handling
- [ ] Includes two-strike retry logic

---

## Phase 4: Python Mediator Scripts — **Status: complete**

**Parallel: yes** (with Phase 5 — no file overlap)

### What
Build all inter-agent data passing scripts. These are OpenClaw-specific — Claude Code agents share filesystem directly, but OpenClaw isolated agents need mediators.

### Files to create
- `openclaw/scripts/__init__.py`
- `openclaw/scripts/init_requirements.py`
- `openclaw/scripts/add_requirement.py`
- `openclaw/scripts/generate_summary.py`
- `openclaw/scripts/add_design_spec.py`
- `openclaw/scripts/update_design_status.py`
- `openclaw/scripts/list_available_work.py`
- `openclaw/scripts/claim_requirement.py`
- `openclaw/scripts/get_design_spec.py`
- `openclaw/scripts/complete_requirement.py`
- `openclaw/scripts/run_stage_eval.py`
- `openclaw/scripts/update_progress.py`

### Script details (I/O from port plan §8 + v2 enhancements)

| Script | Purpose | Reads | Writes | v2 source |
|--------|---------|-------|--------|-----------|
| `init_requirements.py` | Initialize REQUIREMENTS.md from feature | queue.json | REQUIREMENTS.md (skeleton) | New |
| `add_requirement.py` | Add/update a requirement | REQUIREMENTS.md | REQUIREMENTS.md | New |
| `generate_summary.py` | Generate PRD.md from requirements | REQUIREMENTS.md | PRD.md | New |
| `add_design_spec.py` | Add UI spec for a requirement | REQUIREMENTS.md | DESIGN_SPECS.md | New |
| `update_design_status.py` | Mark design complete | DESIGN_SPECS.md | DESIGN_SPECS.md | New |
| `list_available_work.py` | List requirements ready for impl | REQUIREMENTS.md, DESIGN_SPECS.md | stdout | New |
| `claim_requirement.py` | Mark requirement in progress | REQUIREMENTS.md | REQUIREMENTS.md | New |
| `get_design_spec.py` | Get design spec for requirement | DESIGN_SPECS.md | stdout | New |
| `complete_requirement.py` | Mark requirement implemented | REQUIREMENTS.md | REQUIREMENTS.md | New |
| `run_stage_eval.py` | Run stage-gate checks | Artifacts | eval_result.json | Wraps `orchestrator/checks/*.py` |
| `update_progress.py` | Update pipeline state | progress.json | progress.json | Adapts `orchestrator/state.py` |

### Key: run_stage_eval.py wraps existing checks
```
python scripts/openclaw/run_stage_eval.py --stage spec --feature "notifications" --project-dir .
```
This calls `orchestrator/checks/spec_checks.py` (S1-S5), `design_checks.py` (D1-D5), etc. — the same 24 deterministic checks, zero LLM cost.

### Test gate
- [ ] `python -c "from openclaw.scripts import init_requirements"` succeeds
- [ ] `python openclaw/scripts/run_stage_eval.py --help` prints usage
- [ ] `python openclaw/scripts/update_progress.py --help` prints usage
- [ ] All scripts have `if __name__ == "__main__"` CLI entry points

---

## Phase 5: Reporting Layer — **Status: complete**

**Parallel: yes** (with Phase 4 — no file overlap)

### What
Create `scripts/openclaw/report.py` with Telegram Bot API + Discord webhook support. Same interface as `orchestrator/tools/slack_tools.py` but multi-channel.

### Files to create
- `openclaw/scripts/report.py`

### Channels
| Channel | Method | Config |
|---------|--------|--------|
| Telegram | Bot API: `POST https://api.telegram.org/bot{token}/sendMessage` | `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` |
| Discord | Webhook: `POST {webhook_url}` with JSON body | `DISCORD_WEBHOOK_URL` |
| None | Skip silently | Default |

### Report types (from v2 slack_tools.py + port plan §12)
| Event | When | Content |
|-------|------|---------|
| start | Phase begins | "Phase 2/6: UX Designer started for 'notifications'" |
| pass | Gate passes | "Phase 2/6: Design complete. 5/5 eval checks passed." |
| warn | Gate has warnings | "Phase 3: Plan gate passed with warnings." |
| fail | Gate fails after retry | "Phase 3 BLOCKED: T-R2 missing API schema." |
| complete | All phases done | Full summary with requirements, test results, completion % |
| stall | Agent stalled 2+ heartbeats | "Coder agent stalled on R3. Respawning." |

### Test gate
- [ ] `python openclaw/scripts/report.py --help` prints usage
- [ ] `python openclaw/scripts/report.py --dry-run --channel telegram --event start --stage spec --details "test"` prints formatted message without sending

---

## Phase 6: Installer + Documentation — **Status: complete**

**Parallel: no**

### What
- Create `install-openclaw.sh` for OpenClaw-specific installation
- Update `install.sh` to detect and install for both Claude Code + OpenClaw
- Update `docs/openclaw-port-plan.md` with all v2 enhancements
- Update `README.md` with OpenClaw section

### Files to create
- `openclaw/install.sh`

### Files to modify
- `docs/openclaw-port-plan.md` (add §19: v2 Enhancements Update)
- `openclaw/README.md` (standalone OpenClaw docs — does NOT touch root README.md)

### openclaw/install.sh steps
1. Check `which openclaw`
2. Clone/update Astra repo to `~/astra`
3. Copy skills to `~/.openclaw/workspace/skills/astra/`
4. Copy `openclaw.plugin.json` to workspace
5. Copy `AGENTS.md`, `HEARTBEAT.md`, `SOUL.md`, `BOOTSTRAP.md` to workspace
6. Copy `scripts/openclaw/*.py` to workspace
7. Copy `orchestrator/checks/` to workspace (reused directly)
8. Install Python deps: `pip install graphifyy pydantic rich pyyaml`
9. Configure cron jobs (prompt user)
10. Prompt for Telegram/Discord config (optional)
11. Prompt for model preferences per agent

### Test gate
- [ ] `bash -n openclaw/install.sh` passes (syntax check)
- [ ] docs/openclaw-port-plan.md includes §19 (v2 Enhancements Update)
- [ ] `openclaw/README.md` exists with installation and usage docs

---

## Phase 7: Final Verification — **Status: complete**

**Parallel: no**

### What
End-to-end verification of all created files.

### Test gate
- [ ] All Python scripts parse without errors: `python -m py_compile openclaw/scripts/*.py`
- [ ] JSON files are valid: `python -c "import json; json.load(open('openclaw/plugin.json'))"`
- [ ] Shell scripts pass syntax check: `bash -n openclaw/install.sh`
- [ ] File structure matches port plan §15 (Target)
- [ ] No orphan references (HEARTBEAT mentions scripts that exist, AGENTS references skills that exist)
- [ ] `orchestrator/checks/` still works after no modifications (imports unchanged)
