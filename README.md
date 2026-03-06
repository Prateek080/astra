# Astra

> A Claude Code plugin that gives you a complete development workflow — from idea to production.
> Cross-project. Stack-agnostic. Works in any codebase.

---

## Getting Started

Astra adds 8 commands to Claude Code. Two for setup (run once), six for daily development. Here's how to get going.

### Step 1 — Install Astra

Clone the repo and load it with Claude Code:

```bash
git clone git@github.com:Prateek080/astra.git ~/astra
```

Then start any Claude Code session with:

```bash
claude --plugin-dir ~/astra
```

To avoid typing `--plugin-dir` every time, add an alias to your shell config (`~/.zshrc` or `~/.bashrc`):

```bash
alias claude='claude --plugin-dir ~/astra'
```

Reload your shell (`source ~/.zshrc`) and now every `claude` session includes Astra automatically.

**Verify:** Run `/help` inside Claude Code. You should see `/astra:setup`, `/astra:init`, `/astra:spec`, `/astra:plan`, `/astra:implement`, `/astra:review`, `/astra:ship`, `/astra:debug`.

### Step 2 — Configure your machine

Run this once. It sets up your global Claude Code environment.

```
/astra:setup
```

This command interviews you about your preferences (languages, frameworks, conventions, git workflow) and then:

- **Configures `~/.claude/settings.json`** — sets effort level to high (deeper thinking) and auto-compaction to 80% (prevents context from running out mid-session)
- **Generates `~/.claude/CLAUDE.md`** — your personal coding standards, loaded into every session across all projects
- **Guides you through** `/permissions`, `/sandbox`, and `/statusline` — these are interactive Claude Code commands that can't be automated, so it walks you through them

After this, your Claude Code is tuned for serious development work.

### Step 3 — Set up your project

Run this once per project. It teaches Claude about your specific codebase.

```
/astra:init
```

This command scans your project (README, package.json, directory structure, configs) and then:

- **Generates `CLAUDE.md`** in the project root — a concise summary of your stack, structure, dev commands, and conventions. Claude reads this at the start of every session so it knows how your project works.
- **Generates `.claude/rules/`** — path-specific rules that tell Claude to follow different conventions in different parts of the codebase. For example, a full-stack project might get:
  - `backend.md` — "follow the route pattern in `app/api/users.py`, use ORM models, add tests for new endpoints"
  - `frontend.md` — "reuse components from `components/ui/`, follow the data fetching pattern in existing pages, mobile-first"

These rules reference real files and patterns from *your* codebase, not generic advice.

**You're ready to build.**

---

## What Command Do I Use?

| Task | Example | What to run |
|---|---|---|
| **Tiny** | Fix a typo, rename a variable | Just ask Claude. No commands needed. |
| **Small** | Single-file bug fix, add a field | Just ask Claude. `/astra:review` after if you want. |
| **Medium** | Add a feature across 2-5 files | `plan` → `implement` → `review` → `ship` |
| **Large** | New feature, unclear scope | `spec` → *clear* → `plan` → `implement` → `review` → `ship` |
| **Cleanup** | Refactor, optimize, pay down debt | `debt-audit` → `plan` → `implement` → `review` → `ship` |

All commands are prefixed with `/astra:` (e.g., `/astra:plan`).

---

## Commands

### `/astra:spec` — Define what to build

```
/astra:spec "user auth with Google and GitHub OAuth"
/astra:spec
```

Interviews you about the feature — problem, users, scope, constraints, edge cases, non-requirements. Challenges your assumptions. Produces `SPEC.md`.

**Next:** `/clear` → `/astra:plan`

---

### `/astra:plan` — Break the work into phases

```
/astra:plan
/astra:plan "add pagination to the transactions API"
```

Explores the codebase via a subagent (keeps your context clean). Creates `PLAN.md` with numbered phases — each has scope, tasks, a test gate, and whether it can run in parallel with other phases.

**Next:** `/astra:implement`

---

### `/astra:implement` — Build phase by phase

```
/astra:implement
/astra:implement "phase 3"
```

Executes the plan one phase at a time. Searches for existing patterns before writing new code. Runs the test gate after each phase. Suggests `/clear` between phases. Stops and asks after 2 failed attempts.

**Next:** `/astra:review`

---

### `/astra:review` — Catch issues before shipping

```
/astra:review
/astra:review src/auth/
/astra:review main..HEAD
```

Reviews against a 40+ item checklist (security, performance, quality, reusability, tech debt). Runs in a subagent. Findings grouped by severity: **Critical** / **Warning** / **Suggestion**, each with file, line, issue, and fix.

**Next:** Fix criticals → `/astra:ship`

---

### `/astra:ship` — Commit and open a PR

```
/astra:ship
/astra:ship main
```

Runs pre-flight checks (tests, lint, secrets scan, debug artifact scan), stages files explicitly, commits with a clean message, pushes, and opens a PR via `gh`. Returns the PR URL.

---

### `/astra:debug` — Find and fix the root cause

```
/astra:debug "TypeError: cannot read property 'id' of undefined"
/astra:debug
```

Hypothesis-driven debugging in a subagent. Finds the root cause, implements a minimal fix, writes a regression test. Reports: root cause, evidence, fix, verification, prevention.

**Next:** `/astra:review` → `/astra:ship`

---

## Additional Skills

| Skill | What it does |
|---|---|
| `/astra:debt-audit` | Scans for dead code, orphaned TODOs, deprecated patterns, missing tests, duplication. Outputs a prioritized report. |
| `/astra:workflow-guide` | Explains which commands to use for new projects, new features, and optimizations. |
| `/astra:retrospective` | Compares spec and plan to what was actually built. Suggests improvements for your workflow. |

---

## Context Management

**Why this matters:** Claude Code has a finite context window. As the conversation grows, older instructions and code get compressed or lost. When context fills up, Claude forgets your conventions, misses details, and quality drops. Managing context is the single most important habit for getting good results.

**How to manage it:**

| Situation | Action | Why |
|---|---|---|
| Finished a task, starting something new | `/clear` | Old task's file reads, errors, and discussion are irrelevant. Fresh context = better results. |
| Between implementation phases | `/clear` | Phase 3 doesn't need phase 1's file contents. Each phase starts clean. |
| Claude keeps making the same mistake | `/clear` and rephrase | Earlier wrong attempts pollute context. A fresh start with clearer instructions works better. |
| Long session, can't clear yet | `/compact` | Manually compresses old messages. Do this around 50% context usage. |
| Want to monitor usage | `/statusline` | Shows context % in your terminal. Set up once during `/astra:setup`. |

**Built-in protections:** Astra commands delegate heavy exploration to subagents — their file reads and searches happen in a separate context, not yours. Auto-compaction is set to 80% during `/astra:setup` (default is 95%, which is too late).

---

## Under the Hood

### Agents

Commands delegate work to specialized agents, each running in its own context window so your main conversation stays clean.

| Agent | Role | Learns |
|---|---|---|
| **coordinator** | Orchestrates agents in parallel | No |
| **planner** | Explores codebase, creates plans | Yes |
| **implementer** | Writes code, runs tests | Yes |
| **reviewer** | 40+ item review checklist | Yes |
| **debugger** | Root cause analysis and fix | Yes |

Agents marked "Learns" accumulate knowledge across all your projects. The reviewer remembers recurring issues. The debugger remembers common root causes. This knowledge persists between sessions.

**Coordinator mode:** For large features, run `claude --agent astra:coordinator` to let the coordinator spawn multiple agents in parallel.

### MCP Servers (auto-loaded)

| Server | Purpose |
|---|---|
| **Context7** | Fetches up-to-date library docs. Prevents hallucinated APIs. |
| **Playwright** | Browser automation for testing UI. |
| **DeepWiki** | Documentation for any GitHub repo. |

### Hooks

Desktop notifications (macOS + Linux) when Claude needs your attention.

---

## Project Structure

```
astra/
├── .claude-plugin/
│   └── plugin.json              Plugin manifest
├── commands/
│   ├── setup.md                 /astra:setup  — one-time global config
│   ├── init.md                  /astra:init   — per-project setup
│   ├── spec.md                  /astra:spec   — feature discovery
│   ├── plan.md                  /astra:plan   — phased planning
│   ├── implement.md             /astra:implement — phase execution
│   ├── review.md                /astra:review — code review
│   ├── ship.md                  /astra:ship   — commit + PR
│   └── debug.md                 /astra:debug  — root cause analysis
├── agents/
│   ├── coordinator.md           Parallel orchestrator
│   ├── planner.md               Codebase exploration + planning
│   ├── implementer.md           Code execution + testing
│   ├── reviewer.md              Code review + checklist
│   └── debugger.md              Root cause analysis
├── skills/
│   ├── review-checklist/        40+ review checks (preloaded into reviewer)
│   ├── plan-template/           Plan structure (preloaded into planner)
│   ├── debt-audit/              Tech debt scanner
│   ├── workflow-guide/          Usage guide for all scenarios
│   └── retrospective/           Post-feature assessment
├── hooks/
│   └── hooks.json               Desktop notifications
├── .mcp.json                    Context7, Playwright, DeepWiki
└── settings.json                Default agent config
```
