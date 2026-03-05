# Astra

Development lifecycle plugin for Claude Code.
**Spec. Plan. Implement. Review. Ship. Debug.**

Cross-project. Stack-agnostic. Works in any codebase.

---

## Installation

### Option A: Load per session

```bash
claude --plugin-dir /path/to/astra
```

### Option B: Install permanently

```bash
# From inside any Claude Code session
/plugin install /path/to/astra
```

### Option C: Coordinator mode (parallel orchestration)

```bash
claude --agent astra:coordinator --plugin-dir /path/to/astra
```

Use this when a feature has independent phases that can run simultaneously. The coordinator spawns planner, implementer, reviewer, and debugger agents in parallel.

---

## First-Time Setup

Do this once. Takes 5 minutes.

**1. Effort level** — Add to `~/.claude/settings.json`:
```json
{
  "env": {
    "CLAUDE_CODE_EFFORT_LEVEL": "high",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "80"
  }
}
```

**2. Permissions** — Run `/permissions` and allow:
```
Read, Glob, Grep, Edit
Bash(npm test *), Bash(npx *), Bash(git *)
Bash(bun *), Bash(python *), Bash(pip *)
```

**3. Sandbox** — Run `/sandbox` to enable file and network isolation.

**4. Status line** — Run `/statusline` to monitor context usage and cost. This is the #1 tool for managing context — the primary constraint in Claude Code.

**5. LSP plugin** — Run `/plugin` and install the code intelligence plugin for your language (TypeScript, Python, Rust, etc.).

**6. Global CLAUDE.md** — Create `~/.claude/CLAUDE.md`:
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

---

## Per-Project Setup

Each time you start working on a new project:

1. Run `/init` to generate a project-level CLAUDE.md.
2. Create `.claude/rules/` with path-specific rules for your stack:
   - `backend.md` — `paths: ["backend/**", "server/**", "api/**"]`
   - `frontend.md` — `paths: ["frontend/**", "src/**", "app/**"]`
3. For unfamiliar codebases, run `/config` and set output style to **Explanatory**.

---

## Choosing the Right Command

Not every task needs the full workflow. Match commands to task size:

```
Trivial (typo, rename, one-line fix)
  → Just ask Claude directly. No commands needed.

Small (single file, clear scope)
  → Just ask Claude. Optionally /astra:review after.

Medium (2-5 files, clear approach)
  → /astra:plan → /astra:implement → /astra:review → /astra:ship

Large (new feature, unclear scope, multi-module)
  → /astra:spec → /clear → /astra:plan → /astra:implement → /astra:review → /astra:ship

Optimization / Refactor
  → /astra:debt-audit → /astra:plan → /astra:implement → /astra:review → /astra:ship
```

---

## Commands

### `/astra:spec` — Define what to build

Interviews you about the feature before any code is written. Asks about the problem, users, scope, constraints, edge cases, and non-requirements. Produces `SPEC.md`.

**When to use:** Starting a new feature with unclear scope. Starting a new project.

**Use cases:**
```bash
/astra:spec "user authentication with Google and GitHub OAuth"
/astra:spec "real-time notifications system"
/astra:spec   # no args — Claude asks what you want to build
```

**What it does:**
1. Reads existing project context (CLAUDE.md, README).
2. Interviews you with 5-10 focused questions via AskUserQuestion.
3. Challenges assumptions — digs into the hard parts you haven't considered.
4. Writes SPEC.md with requirements, non-requirements, constraints, and edge cases.

**Next step:** `/clear` then `/astra:plan`

---

### `/astra:plan` — Break the work into phases

Explores the codebase and creates a phased implementation plan with test gates. Delegates exploration to the planner subagent to keep your main context clean.

**When to use:** Before implementing anything that touches 2+ files.

**Use cases:**
```bash
/astra:plan                    # reads SPEC.md from project root
/astra:plan SPEC.md            # explicit spec file
/astra:plan "add pagination to the transactions API"  # inline description
```

**What it does:**
1. Delegates codebase exploration to the planner agent (read-only, preserves your context).
2. Identifies existing patterns, test infrastructure, and files to modify vs create.
3. Creates PLAN.md with numbered phases — each has scope, tasks, and a test gate.
4. Marks independent phases for parallel execution.

**Output:** `PLAN.md` following the plan-template structure.

**Next step:** `/astra:implement`

---

### `/astra:implement` — Build phase by phase

Executes the plan one phase at a time. Each phase must pass its test gate before the next begins. Suggests `/clear` between phases to keep context clean.

**When to use:** After a plan exists. This is where code gets written.

**Use cases:**
```bash
/astra:implement               # reads PLAN.md from project root
/astra:implement PLAN.md       # explicit plan file
/astra:implement "phase 3"     # resume from a specific phase
```

**What it does:**
1. Reads the plan. Executes one phase at a time.
2. Before writing code, searches for existing patterns to reuse.
3. Runs the test gate after each phase (tests, lint, type-check).
4. If verification fails, fixes issues before proceeding.
5. After each phase: summarizes changes, suggests `/clear`.
6. For independent phases, spawns parallel subagents with worktree isolation.
7. After the final phase, spawns the reviewer agent.

**Key rules:**
- Never skips a test gate. If tests don't exist, writes them first.
- Stops and asks after 2 failed attempts instead of guessing.

**Next step:** `/astra:review`

---

### `/astra:review` — Catch issues before shipping

Delegates a comprehensive code review to the reviewer agent. Covers security, performance, quality, reusability, and tech debt using a 40+ item checklist.

**When to use:** After implementing changes. Before shipping. On PRs from others.

**Use cases:**
```bash
/astra:review                  # reviews all uncommitted changes
/astra:review src/auth/        # reviews a specific directory
/astra:review main..HEAD       # reviews changes vs main branch
```

**What it does:**
1. Delegates to the reviewer agent (separate context, doesn't pollute yours).
2. Reviewer applies the full review-checklist: security, performance, quality, reusability, tech debt, testing.
3. Organizes findings by severity: Critical (must fix), Warning (should fix), Suggestion (consider).
4. Each finding includes: file, line, what's wrong, how to fix it.

**Next step:** Fix critical/warning items, then `/astra:ship`

---

### `/astra:ship` — Commit and create a PR

Runs pre-flight checks, creates a descriptive commit, pushes, and opens a pull request.

**When to use:** After implementation and review. When changes are ready to merge.

**Use cases:**
```bash
/astra:ship                    # ships to default branch
/astra:ship main               # explicit base branch
/astra:ship develop            # ship to develop branch
```

**What it does:**
1. **Pre-flight checks:**
   - Runs the project's test suite. Stops if tests fail.
   - Runs linter/formatter if configured.
   - Scans for secrets, credentials, .env files in staged changes.
   - Checks for debug artifacts (console.log, debugger, print statements).
   - Reviews the full diff.
2. **Commit:** Stages files explicitly (never `git add .`). Writes imperative commit message explaining why.
3. **PR:** Pushes and creates PR via `gh pr create` with summary and test plan.

**Output:** PR URL.

---

### `/astra:debug` — Find and fix the root cause

Delegates structured debugging to the debugger agent. Finds the root cause, implements a minimal fix, and verifies it works.

**When to use:** When you hit an error, a failing test, or unexpected behavior.

**Use cases:**
```bash
/astra:debug "TypeError: cannot read property 'id' of undefined"
/astra:debug "test suite fails on CI but passes locally"
/astra:debug "API returns 500 on large payloads"
/astra:debug   # no args — Claude asks you to describe the issue
```

**What it does:**
1. Delegates to the debugger agent (keeps verbose investigation out of your context).
2. Debugger forms hypotheses, tests them systematically (no guess-and-check).
3. Implements the smallest fix that addresses the root cause.
4. Writes a regression test.
5. Reports: root cause, evidence, fix, verification, and prevention strategy.

**Next step:** `/astra:review` then `/astra:ship`

---

## Additional Skills

These aren't part of the main workflow but are available on demand.

### `/astra:debt-audit` — Scan for tech debt

Full codebase audit. Runs in a forked subagent (won't pollute your context). Checks for: dead code, orphaned TODOs, deprecated patterns, hardcoded values, missing tests, dependency issues, code duplication.

```bash
/astra:debt-audit
```

**Output:** Prioritized report (critical / important / minor) with specific file references.

### `/astra:workflow-guide` — How to use Astra

Explains which commands to use for different scenarios: new project, new feature, optimization. Includes task-size guidance.

```bash
/astra:workflow-guide
```

### `/astra:retrospective` — Improve the workflow

Assesses how the last feature went. Compares SPEC.md and PLAN.md against what was actually built. Outputs copy-pasteable improvements for the review checklist, plan template, and project CLAUDE.md.

```bash
/astra:retrospective
```

---

## How It Works Under the Hood

### Agents

Commands delegate work to specialized agents. Each runs in its own context window so your main conversation stays clean.

| Agent | Role | Color | Learns across projects |
|---|---|---|---|
| **coordinator** | Orchestrates other agents in parallel | blue | No |
| **planner** | Explores codebase, creates plans | cyan | Yes |
| **implementer** | Writes code, runs tests | green | Yes |
| **reviewer** | Reviews against 40+ item checklist | yellow | Yes |
| **debugger** | Root cause analysis and fix | red | Yes |

Agents with learning enabled (`memory: user`) accumulate knowledge across every project you work on. The reviewer remembers recurring issues. The debugger remembers common root causes. The planner remembers what plan structures work best.

### MCP Servers (auto-loaded)

| Server | What it does |
|---|---|
| **Context7** | Fetches up-to-date library documentation. Prevents hallucinated APIs. |
| **Playwright** | Browser automation for testing and debugging UI. |
| **DeepWiki** | Structured documentation for any GitHub repository. |

### Hooks

| Event | Action |
|---|---|
| **Notification** | Desktop notification when Claude needs attention (macOS + Linux). |

---

## Context Management Tips

Context is the #1 constraint. These habits keep Astra effective:

- **`/clear` between unrelated tasks.** Don't let a bug fix pollute a feature session.
- **`/clear` between implementation phases.** Phase 3 doesn't need phase 1's file reads.
- **Let agents do the reading.** Commands delegate to subagents so exploration stays out of your context.
- **After 2 corrections on the same issue,** `/clear` and rephrase with what you learned.
- **Watch your status line.** Manual `/compact` at ~50% if you need to continue without clearing.

---

## Advanced

### Agent Teams (Experimental)

For maximum parallelism, enable agent teams:

```json
// ~/.claude/settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Ask Claude to create a team for your feature. Each teammate gets their own context window and can communicate with others.

### Environment Variables

Add to `"env"` in `~/.claude/settings.json`:

| Variable | Value | Effect |
|---|---|---|
| `CLAUDE_CODE_EFFORT_LEVEL` | `high` | Maximum reasoning depth |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `1` | Enable agent teams |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | `80` | Auto-compact at 80% instead of 95% |

---

## Project Structure

```
astra/
├── .claude-plugin/plugin.json     Plugin identity
├── commands/
│   ├── spec.md                    /astra:spec
│   ├── plan.md                    /astra:plan
│   ├── implement.md               /astra:implement
│   ├── review.md                  /astra:review
│   ├── ship.md                    /astra:ship
│   └── debug.md                   /astra:debug
├── agents/
│   ├── coordinator.md             Parallel orchestrator
│   ├── planner.md                 Codebase exploration + planning
│   ├── implementer.md             Code execution + testing
│   ├── reviewer.md                Code review + checklist
│   └── debugger.md                Root cause analysis
├── skills/
│   ├── review-checklist/SKILL.md  40+ review checks (preloaded into reviewer)
│   ├── plan-template/SKILL.md     Plan structure (preloaded into planner)
│   ├── debt-audit/SKILL.md        Tech debt scanner
│   ├── workflow-guide/SKILL.md    Usage guide for all scenarios
│   └── retrospective/SKILL.md     Post-feature assessment
├── hooks/hooks.json               Desktop notifications
├── .mcp.json                      Context7, Playwright, DeepWiki
├── settings.json                  Coordinator as default agent
└── README.md                      This file
```
