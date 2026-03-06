<p align="center">
  <h1 align="center">Astra</h1>
  <p align="center">
    A Claude Code plugin for the complete development lifecycle.<br/>
    <strong>Idea → Spec → Plan → Implement → Review → Ship</strong>
  </p>
  <p align="center">
    Cross-project &bull; Stack-agnostic &bull; Works in any codebase
  </p>
</p>

<br/>

## Getting Started

Three steps. Two are one-time, one is per-project.

<br/>

<table>
<tr><td>

### `1` &nbsp; Install

```bash
git clone git@github.com:Prateek080/astra.git ~/astra
```

Add this alias to `~/.zshrc` (or `~/.bashrc`) so Astra loads automatically:

```bash
alias claude='claude --plugin-dir ~/astra'
```

Reload your shell: `source ~/.zshrc`

> **Verify** — run `/help` inside Claude Code. You should see all `/astra:*` commands.

</td></tr>
<tr><td>

### `2` &nbsp; Configure your machine &nbsp; *(one-time)*

```
/astra:setup
```

Interviews you about your stack, conventions, and preferences. Then:

| What it does | Why |
|---|---|
| Configures `~/.claude/settings.json` | Sets effort to high + auto-compact at 80% so context doesn't run out mid-session |
| Generates `~/.claude/CLAUDE.md` | Your personal coding standards, loaded into every session across all projects |
| Walks you through `/permissions`, `/sandbox`, `/statusline` | These are interactive — can't be automated, so Astra guides you step by step |

</td></tr>
<tr><td>

### `3` &nbsp; Set up your project &nbsp; *(once per codebase)*

```
/astra:init
```

Scans your project (README, configs, directory structure), asks 2-4 clarifying questions, then generates:

| File | Purpose |
|---|---|
| `CLAUDE.md` | Project summary — stack, structure, dev commands, conventions. Loaded every session. |
| `.claude/rules/backend.md` | Path-specific rules for backend code — references real files and patterns from your codebase. |
| `.claude/rules/frontend.md` | Path-specific rules for frontend code — component reuse, data fetching patterns, responsive rules. |

Rules are tailored to *your* project, not generic advice.

**You're ready to build.**

</td></tr>
</table>

<br/>

---

<br/>

## What Command Do I Use?

> Not every task needs the full workflow. Match the command to the task size.

```
Tiny  (typo, rename, one-line fix)           → Just ask Claude
Small (single-file fix, add a field)         → Just ask Claude. /astra:review after if you want.
Medium (2-5 files, clear approach)           → plan → implement → review → ship
Large (new feature, unclear scope)           → spec → /clear → plan → implement → review → ship
Cleanup (refactor, optimize, pay debt)       → debt-audit → plan → implement → review → ship
```

All commands are prefixed with `/astra:` — e.g. `/astra:plan`.

<br/>

---

<br/>

## Commands

<br/>

<table>
<tr>
<td width="160"><strong><code>/astra:spec</code></strong></td>
<td><strong>Define what to build</strong></td>
</tr>
<tr><td colspan="2">

```
/astra:spec "user auth with Google and GitHub OAuth"
/astra:spec
```

Interviews you about the feature — problem, users, scope, constraints, edge cases, non-requirements. Challenges your assumptions. Produces **`SPEC.md`**.

**Next →** `/clear` then `/astra:plan`

</td></tr>
</table>

<table>
<tr>
<td width="160"><strong><code>/astra:plan</code></strong></td>
<td><strong>Break the work into phases</strong></td>
</tr>
<tr><td colspan="2">

```
/astra:plan
/astra:plan "add pagination to the transactions API"
```

Explores the codebase via a subagent (keeps your context clean). Creates **`PLAN.md`** with numbered phases — each has scope, tasks, a test gate, and whether it can run in parallel.

**Next →** `/astra:implement`

</td></tr>
</table>

<table>
<tr>
<td width="160"><strong><code>/astra:implement</code></strong></td>
<td><strong>Build phase by phase</strong></td>
</tr>
<tr><td colspan="2">

```
/astra:implement
/astra:implement "phase 3"
```

Executes the plan one phase at a time. Searches for existing patterns before writing. Runs the test gate after each phase. Suggests `/clear` between phases. Stops and asks after 2 failed attempts.

**Next →** `/astra:review`

</td></tr>
</table>

<table>
<tr>
<td width="160"><strong><code>/astra:review</code></strong></td>
<td><strong>Catch issues before shipping</strong></td>
</tr>
<tr><td colspan="2">

```
/astra:review
/astra:review src/auth/
/astra:review main..HEAD
```

Reviews against a **40+ item checklist** (security, performance, quality, reusability, tech debt). Runs in a subagent. Findings grouped: **Critical** / **Warning** / **Suggestion** — each with file, line, issue, and fix.

**Next →** Fix criticals, then `/astra:ship`

</td></tr>
</table>

<table>
<tr>
<td width="160"><strong><code>/astra:ship</code></strong></td>
<td><strong>Commit and open a PR</strong></td>
</tr>
<tr><td colspan="2">

```
/astra:ship
/astra:ship main
```

Pre-flight checks (tests, lint, secrets scan, debug artifacts), stages files explicitly, commits with a clean message, pushes, and opens a PR via `gh`. Returns the **PR URL**.

</td></tr>
</table>

<table>
<tr>
<td width="160"><strong><code>/astra:debug</code></strong></td>
<td><strong>Find and fix the root cause</strong></td>
</tr>
<tr><td colspan="2">

```
/astra:debug "TypeError: cannot read property 'id' of undefined"
/astra:debug
```

Hypothesis-driven debugging in a subagent. Finds the root cause, implements a minimal fix, writes a regression test. Reports: root cause, evidence, fix, verification, prevention.

**Next →** `/astra:review` then `/astra:ship`

</td></tr>
</table>

<br/>

---

<br/>

## Additional Skills

| Skill | What it does |
|---|---|
| **`/astra:debt-audit`** | Scans for dead code, orphaned TODOs, deprecated patterns, missing tests, duplication. Outputs a prioritized report. |
| **`/astra:workflow-guide`** | Explains which commands to use for new projects, new features, and optimizations. |
| **`/astra:retrospective`** | Compares spec and plan to what was actually built. Suggests improvements for your workflow. |

<br/>

---

<br/>

## Context Management

> **Why this matters:** Claude Code has a finite context window. As the conversation grows, older instructions get compressed or lost. When context fills up, Claude forgets your conventions, misses details, and quality drops. Managing context is the **single most important habit** for getting good results.

<br/>

| Situation | What to do | Why |
|---|---|---|
| Finished a task, starting something new | **`/clear`** | Old task's file reads and discussion are irrelevant. Fresh context = better results. |
| Between implementation phases | **`/clear`** | Phase 3 doesn't need phase 1's file contents. Each phase starts clean. |
| Claude keeps making the same mistake | **`/clear`** and rephrase | Wrong attempts pollute context. Fresh start with clearer instructions works better. |
| Long session, can't clear yet | **`/compact`** | Manually compresses old messages. Do this around 50% context usage. |
| Want to monitor usage | **`/statusline`** | Shows context % in your terminal. Set up once during `/astra:setup`. |

<br/>

**Built-in protections:** Astra commands delegate heavy exploration to subagents — their file reads happen in a *separate* context, not yours. Auto-compaction is set to 80% during `/astra:setup` (default is 95%, which is too late).

<br/>

---

<br/>

## Under the Hood

<details>
<summary><strong>Agents</strong> — specialized workers, each in its own context window</summary>

<br/>

| Agent | Role | Learns across projects |
|---|---|---|
| **coordinator** | Orchestrates agents in parallel | No |
| **planner** | Explores codebase, creates plans | Yes |
| **implementer** | Writes code, runs tests | Yes |
| **reviewer** | 40+ item review checklist | Yes |
| **debugger** | Root cause analysis and fix | Yes |

Agents with learning accumulate knowledge across all your projects. The reviewer remembers recurring issues. The debugger remembers common root causes.

**Coordinator mode:** For large features with independent phases, run `claude --agent astra:coordinator` to orchestrate multiple agents in parallel.

</details>

<details>
<summary><strong>MCP Servers</strong> — auto-loaded with the plugin</summary>

<br/>

| Server | Purpose |
|---|---|
| **Context7** | Fetches up-to-date library docs. Prevents hallucinated APIs. |
| **Playwright** | Browser automation for testing UI. |
| **DeepWiki** | Documentation for any GitHub repo. |

</details>

<details>
<summary><strong>Hooks</strong></summary>

<br/>

Desktop notifications (macOS + Linux) when Claude needs your attention.

</details>

<br/>

---

<br/>

## Project Structure

```
astra/
├── .claude-plugin/
│   └── plugin.json              Plugin manifest
│
├── commands/                    User-facing commands
│   ├── setup.md                 /astra:setup     one-time global config
│   ├── init.md                  /astra:init      per-project setup
│   ├── spec.md                  /astra:spec      feature discovery
│   ├── plan.md                  /astra:plan      phased planning
│   ├── implement.md             /astra:implement  phase execution
│   ├── review.md                /astra:review     code review
│   ├── ship.md                  /astra:ship      commit + PR
│   └── debug.md                 /astra:debug     root cause analysis
│
├── agents/                      Specialized subagents
│   ├── coordinator.md           Parallel orchestrator
│   ├── planner.md               Codebase exploration + planning
│   ├── implementer.md           Code execution + testing
│   ├── reviewer.md              Code review + checklist
│   └── debugger.md              Root cause analysis
│
├── skills/                      Reusable knowledge
│   ├── review-checklist/        40+ review checks (preloaded into reviewer)
│   ├── plan-template/           Plan structure (preloaded into planner)
│   ├── debt-audit/              Tech debt scanner
│   ├── workflow-guide/          Usage guide for all scenarios
│   └── retrospective/           Post-feature assessment
│
├── hooks/
│   └── hooks.json               Desktop notifications
│
└── .mcp.json                    Context7, Playwright, DeepWiki
```
