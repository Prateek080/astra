# Astra for OpenClaw

Multi-model development lifecycle pipeline for OpenClaw — the same Astra workflow (spec → design → plan → architect → implement → review) running with per-agent model routing and cron-driven orchestration.

## What's Different from Claude Code

| Aspect | Claude Code (Astra) | OpenClaw (Astra) |
|--------|-------------------|-----------------|
| **Orchestrator** | `commands/forge.md` (LLM) / `orchestrator/pipeline.py` (SDK) | `HEARTBEAT.md` (cron-driven) |
| **Models** | All Claude (inherit) | Per-agent: PM → Sonnet, Coder → Kimi, Debugger → Opus |
| **Agent isolation** | Sub-agents share parent | Fully isolated sessions |
| **Code implementation** | Direct Write/Edit tools | Aider integration (configurable) |
| **Codebase context** | `.astra-cache/context.md` | Graphify knowledge graph (query-first) |
| **Scheduling** | User-triggered | Cron heartbeat + feature queue |
| **Reporting** | Slack (webhook) | Telegram / Discord |
| **Data passing** | Shared filesystem | Python mediator scripts |

## Installation

```bash
cd ~/astra
bash openclaw/install.sh
```

Options:
```bash
bash openclaw/install.sh --workspace ~/my-workspace   # Custom workspace
bash openclaw/install.sh --uninstall                   # Remove
```

### Prerequisites

- OpenClaw CLI
- Python 3.10+
- Git
- Optional: `gh` (GitHub CLI), `aider` (code agent)

## Architecture

```
openclaw/
├── plugin.json          Plugin manifest with model routing + configSchema
├── AGENTS.md            7 agent definitions (PM, Designer, Planner, Architect, Coder, Reviewer, Debugger)
├── SOUL.md              Dexter — main orchestrator agent personality
├── HEARTBEAT.md         Cron-driven state machine (replaces forge.md)
├── BOOTSTRAP.md         First-run workspace setup
├── scripts/             Python mediator scripts for inter-agent data passing
│   ├── init_requirements.py      Initialize REQUIREMENTS.md from feature
│   ├── add_requirement.py        Add/update requirements
│   ├── generate_summary.py       Generate PRD.md from requirements
│   ├── add_design_spec.py        Add UI design spec (D-R{n})
│   ├── update_design_status.py   Mark design complete
│   ├── list_available_work.py    List work ready for implementation
│   ├── claim_requirement.py      Claim a requirement (in_progress)
│   ├── get_design_spec.py        Get design spec for a requirement
│   ├── complete_requirement.py   Mark requirement as implemented
│   ├── run_stage_eval.py         Run stage-gate checks (wraps orchestrator/checks/)
│   ├── update_progress.py        Manage pipeline state (progress.json)
│   └── report.py                 Send Telegram/Discord notifications
├── templates/           Artifact templates
│   ├── REQUIREMENTS.template.md
│   ├── DESIGN_SPECS.template.md
│   ├── PLAN.template.md
│   └── TECHNICAL.template.md
└── install.sh           Installer
```

### Shared Code (from Claude Code Astra)

These files live in the parent repo and are copied by the installer:
- `orchestrator/checks/` — 24 deterministic stage-gate checks (S1-S5, D1-D5, P1-P4, T1-T5, I1-I4)
- `skills/` — 12 methodology skills (model-agnostic, shared across all editors)
- `rules/` — Path-scoped conventions (API, frontend, tests)

## Usage

### Start a build

Send to Dexter:
```
build: add notifications system
```

Or add to queue:
```json
// .astra-state/queue.json
[{"feature": "add notifications", "priority": 1}]
```

### Pipeline stages

```
idle → scan → spec → [design + plan] → architect → implement → review → wrapup → idle
```

Lite mode (auto-detected for small features):
```
idle → scan → spec → plan → implement → review → wrapup → idle
```

### Stage-gate checks

Run manually:
```bash
python scripts/run_stage_eval.py --stage spec --feature "notifications" --project-dir .
python scripts/run_stage_eval.py --stage design --project-dir .
python scripts/run_stage_eval.py --stage plan --project-dir .
python scripts/run_stage_eval.py --stage technical --project-dir .
python scripts/run_stage_eval.py --stage phase --project-dir .
```

### Pipeline state

```bash
python scripts/update_progress.py --action status --project-dir .
python scripts/update_progress.py --action init --feature "notifications" --mode full
python scripts/update_progress.py --stage spec --status complete --artifact REQUIREMENTS.md
```

### Notifications

```bash
python scripts/report.py --channel telegram --event start --stage spec --details "Starting notifications"
python scripts/report.py --channel discord --event complete --stage pipeline --details "All done"
python scripts/report.py --dry-run --event fail --stage design --details "D-R2 missing"
```

## Model Configuration

Edit `plugin.json` → `configSchema.properties.models`:

```json
{
  "models": {
    "pm": "claude-sonnet-4-20250514",
    "designer": "claude-sonnet-4-20250514",
    "planner": "gemini-2.5-pro",
    "architect": "claude-opus-4-20250515",
    "coder": "kimi-k2.5:cloud",
    "reviewer": "claude-sonnet-4-20250514",
    "debugger": "claude-opus-4-20250515"
  }
}
```

## Cron Schedules

Default schedules (configurable in `plugin.json`):

| Job | Schedule | Purpose |
|-----|----------|---------|
| Build marathon | Hourly, 5AM-11PM UTC | Main pipeline heartbeat |
| Continuous build | Every 2 hours | Stall detection |
| Graph update | Every 8 hours | Refresh graphify knowledge graph |

## Updating

```bash
cd ~/astra
git pull
bash openclaw/install.sh
```
