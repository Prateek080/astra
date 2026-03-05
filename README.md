# Astra

Development lifecycle plugin for Claude Code.
**Spec. Plan. Implement. Review. Ship. Debug.**

Cross-project. Stack-agnostic. Works in any codebase.

---

## Getting Started

### 1. Install the plugin

Open any Claude Code session and run these two commands:

```
/plugin marketplace add Prateek080/astra
/plugin install astra
```

That's it. Astra is now available in every Claude Code session — every project, every directory. You'll never need to run these again.

> **Per-project only?** Use `/plugin install astra --scope project` instead. This saves it to the project's `.claude/plugins/` so teammates get it too.
>
> **Contributing to Astra?** Clone the repo and load it directly:
> ```bash
> git clone git@github.com:Prateek080/astra.git ~/astra
> claude --plugin-dir ~/astra
> ```

Verify it worked by running `/help` — you should see `/astra:spec`, `/astra:plan`, `/astra:implement`, `/astra:review`, `/astra:ship`, `/astra:debug`.

### 2. Configure Claude Code (once)

These settings make Claude Code work best with Astra. Do this once on your machine.

**Set effort and auto-compaction** — add to `~/.claude/settings.json`:
```json
{
  "env": {
    "CLAUDE_CODE_EFFORT_LEVEL": "high",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "80"
  }
}
```

**Pre-approve common tools** — run `/permissions` and allow:
```
Read, Glob, Grep, Edit
Bash(npm test *), Bash(npx *), Bash(git *)
Bash(bun *), Bash(python *), Bash(pip *)
```

**Enable safety and monitoring:**
- `/sandbox` — isolates file and network access
- `/statusline` — shows context usage and cost (context is the #1 constraint, this helps you manage it)

**Optional but recommended:**
- `/plugin` — install an LSP plugin for your language (TypeScript, Python, Rust, etc.) for better code intelligence

**Set up your global CLAUDE.md** — create `~/.claude/CLAUDE.md` with your coding standards. This gets loaded into every session. Here's a good starting point:

```markdown
## Workflow
- Before implementing anything non-trivial, create a plan with phased tasks and test gates.
- Each phase must have a verification step (test, lint, type-check, or screenshot).
- Never skip verification. If tests don't exist, write them first.
- When context feels heavy or you've been correcting course, suggest a /clear.

## Context Discipline
- Delegate codebase research to subagents — don't pollute main context.
- Scope exploration narrowly. Summarize what changed after completing a task.

## Code Quality
- No floating point for money. Use Decimal or integer cents.
- No any types in TypeScript. No # type: ignore without explanation.
- Validate at system boundaries. Trust internal code.
- Three similar lines > premature abstraction.

## Code Reuse
- Search the codebase for existing patterns before writing new code.
- Extract shared logic only after the same pattern appears 3+ times.

## Debt Prevention
- No TODOs without a linked issue. No commented-out code.

## Git
- Imperative mood commit messages. Explain why, not what.
- One logical change per commit. Never force push without approval.

## Testing
- Run the specific test for what changed, not the full suite.
- Tests verify behavior, not implementation details.

## Communication
- Lead with the action, not the reasoning.
- After 2 failed attempts, stop and ask.
```

### 3. Set up your project

Each time you start working on a new codebase, do this once:

1. **Run `/init`** — generates a project-level `CLAUDE.md` with the project's conventions, stack, and structure.

2. **Create path-specific rules** — add files to `.claude/rules/` so Claude follows different conventions for different parts of the codebase:
   - `backend.md` — `paths: ["backend/**", "server/**", "api/**"]`
   - `frontend.md` — `paths: ["frontend/**", "src/**", "app/**"]`

3. **New to the codebase?** Run `/config` and set output style to **Explanatory** so Claude explains patterns as it works.

You're ready. Start building.

---

## Choosing the Right Command

Not every task needs the full workflow. Match commands to task size:

| Task size | Example | Workflow |
|---|---|---|
| **Trivial** | Typo, rename, config change | Just ask Claude directly |
| **Small** | Single-file bug fix | Ask Claude, optionally `/astra:review` after |
| **Medium** | 2-5 files, clear approach | `/astra:plan` → `/astra:implement` → `/astra:review` → `/astra:ship` |
| **Large** | New feature, unclear scope | `/astra:spec` → `/clear` → `/astra:plan` → `/astra:implement` → `/astra:review` → `/astra:ship` |
| **Refactor** | Optimization, cleanup | `/astra:debt-audit` → `/astra:plan` → `/astra:implement` → `/astra:review` → `/astra:ship` |

---

## Commands

### `/astra:spec` — Define what to build

Interviews you about the feature before any code is written. Produces `SPEC.md`.

```
/astra:spec "user auth with Google and GitHub OAuth"
/astra:spec                   # no args — Claude asks what to build
```

Reads project context, asks 5-10 focused questions, challenges your assumptions, then writes a spec with requirements, non-requirements, constraints, and edge cases.

**Next:** `/clear` then `/astra:plan`

### `/astra:plan` — Break the work into phases

Explores the codebase and creates a phased plan with test gates. Produces `PLAN.md`.

```
/astra:plan                   # reads SPEC.md
/astra:plan "add pagination to the transactions API"
```

Delegates exploration to a subagent (keeps your context clean). Identifies existing patterns, files to modify vs create, and marks independent phases for parallel execution.

**Next:** `/astra:implement`

### `/astra:implement` — Build phase by phase

Executes the plan one phase at a time. Each phase must pass its test gate before the next begins.

```
/astra:implement              # reads PLAN.md
/astra:implement "phase 3"   # resume from a specific phase
```

Searches for existing patterns before writing new code. Runs tests after each phase. Suggests `/clear` between phases. Spawns parallel subagents for independent phases. Stops and asks after 2 failed attempts.

**Next:** `/astra:review`

### `/astra:review` — Catch issues before shipping

Reviews code against a 40+ item checklist covering security, performance, quality, reusability, and tech debt.

```
/astra:review                 # reviews uncommitted changes
/astra:review src/auth/       # specific directory
/astra:review main..HEAD      # changes vs main branch
```

Runs in a separate subagent. Findings organized by severity: Critical (must fix), Warning (should fix), Suggestion (consider). Each finding includes file, line, issue, and fix.

**Next:** Fix critical/warning items, then `/astra:ship`

### `/astra:ship` — Commit and create a PR

Runs pre-flight checks, commits, pushes, and opens a pull request.

```
/astra:ship                   # ships to default branch
/astra:ship main              # explicit base branch
```

Pre-flight: runs tests, linter, scans for secrets and debug artifacts, reviews the diff. Stages files explicitly (never `git add .`). Creates PR with summary and test plan.

**Output:** PR URL.

### `/astra:debug` — Find and fix the root cause

Structured debugging: hypothesis, root cause, minimal fix, regression test.

```
/astra:debug "TypeError: cannot read property 'id' of undefined"
/astra:debug                  # no args — Claude asks you to describe it
```

Runs in a separate subagent. Forms hypotheses, tests them systematically. Reports: root cause, evidence, fix, verification, and prevention strategy.

**Next:** `/astra:review` then `/astra:ship`

---

## Additional Skills

| Skill | What it does |
|---|---|
| `/astra:debt-audit` | Full codebase scan for dead code, TODOs, deprecated patterns, missing tests, duplication. Prioritized report. |
| `/astra:workflow-guide` | Which commands to use for new projects, new features, and optimizations. |
| `/astra:retrospective` | Post-feature assessment. Compares spec/plan to what was built. Outputs improvements for your workflow. |

---

## Under the Hood

### Agents

Commands delegate to specialized agents, each in its own context window.

| Agent | Role | Learns across projects |
|---|---|---|
| **coordinator** | Orchestrates agents in parallel (use via `claude --agent astra:coordinator`) | No |
| **planner** | Explores codebase, creates plans | Yes |
| **implementer** | Writes code, runs tests | Yes |
| **reviewer** | 40+ item review checklist | Yes |
| **debugger** | Root cause analysis and fix | Yes |

Agents with learning accumulate knowledge across projects — the reviewer remembers recurring issues, the debugger remembers common root causes.

### MCP Servers (auto-loaded)

| Server | Purpose |
|---|---|
| **Context7** | Up-to-date library docs. Prevents hallucinated APIs. |
| **Playwright** | Browser automation for testing UI. |
| **DeepWiki** | Documentation for any GitHub repo. |

### Hooks

Desktop notifications (macOS + Linux) when Claude needs your attention.

---

## Context Management

Context is the #1 constraint. These habits keep Astra effective:

- `/clear` between unrelated tasks and between implementation phases.
- Let agents do the reading — commands delegate to subagents so exploration stays out of your context.
- After 2 corrections on the same issue, `/clear` and rephrase.
- Manual `/compact` at ~50% if you need to continue without clearing.

---

## Project Structure

```
astra/
├── .claude-plugin/plugin.json     Plugin manifest
├── marketplace.json               Marketplace registry
├── commands/                      /astra:* commands
│   ├── spec.md, plan.md, implement.md, review.md, ship.md, debug.md
├── agents/                        Specialized subagents
│   ├── coordinator.md, planner.md, implementer.md, reviewer.md, debugger.md
├── skills/                        Reusable skills
│   ├── review-checklist/          40+ review checks (preloaded into reviewer)
│   ├── plan-template/             Plan structure (preloaded into planner)
│   ├── debt-audit/                Tech debt scanner
│   ├── workflow-guide/            Usage guide
│   └── retrospective/             Post-feature assessment
├── hooks/hooks.json               Desktop notifications
├── .mcp.json                      Context7, Playwright, DeepWiki
└── settings.json                  Default agent config
```
