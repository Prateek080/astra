---
description: One-time global Claude Code setup — configures settings, permissions, and coding standards for optimal Astra usage
---

# Global Setup

You are configuring the user's global Claude Code environment for optimal use with Astra. This only needs to run once per machine.

## Step 1: Interview the user

Use AskUserQuestion to learn their preferences:

1. **Primary languages/frameworks** — "What languages and frameworks do you mainly work with?" (e.g., TypeScript + React, Python + FastAPI, Rust, Go)
2. **Code style preferences** — "Any strong conventions? Tabs vs spaces, semicolons, naming conventions, etc."
3. **Git workflow** — "Do you use conventional commits? Do you prefer squash merges? Any commit message format?"
4. **Testing approach** — "What test runners do you use? Any coverage requirements?"
5. **Financial or precision math?** — "Do any of your projects deal with money or precise decimal math?"
6. **Anything else** — "Any other rules you always want Claude to follow across all projects?"

Keep it conversational. Skip questions if the user has already answered them. Don't ask more than necessary.

## Step 2: Configure settings.json

Read `~/.claude/settings.json` (create if it doesn't exist). Merge the following into it, preserving any existing keys:

```json
{
  "env": {
    "CLAUDE_CODE_EFFORT_LEVEL": "high",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "80"
  }
}
```

Explain to the user:
- **effort: high** — Claude thinks deeper before responding, catches more issues
- **auto-compact at 80%** — compresses old context before it runs out, so sessions don't hit a wall

## Step 3: Pre-approve common permissions

Tell the user to run `/permissions` and suggest these allowlists based on their tech stack:

**Always:**
```
Read, Glob, Grep, Edit
Bash(git *)
```

**If JavaScript/TypeScript:**
```
Bash(npm *), Bash(npx *), Bash(bun *), Bash(node *)
```

**If Python:**
```
Bash(python *), Bash(pip *), Bash(uv *), Bash(pytest *)
```

**If Rust:**
```
Bash(cargo *)
```

Explain: pre-approving these means Claude won't pause for confirmation on routine operations like running tests or checking git status.

## Step 4: Enable safety features

Tell the user:
- Run `/sandbox` to enable file and network isolation — prevents accidental writes outside the project
- Run `/statusline` to show context usage in the terminal — this is essential because **context is the #1 constraint** in Claude Code. When context fills up, Claude loses earlier instructions and quality drops. The status line helps you know when to `/clear` or `/compact`.

## Step 5: Generate global CLAUDE.md

Create `~/.claude/CLAUDE.md` based on the user's interview answers. This file gets loaded into every Claude Code session across all projects.

The following sections are mandatory — include them in every generated CLAUDE.md. Tailor the wording based on interview answers but keep the principles intact.

```markdown
## Workflow
- Before implementing anything non-trivial, create a plan with phased tasks and test gates.
- Each phase must have a verification step (test, lint, type-check, or screenshot).
- Never skip verification. If tests don't exist, write them first.
- If something goes sideways after 2 attempts, STOP. Don't keep pushing. Re-plan with what you've learned.
- When context feels heavy or you've been correcting course, suggest a /clear.

## Self-Improvement
- When the user corrects you, immediately note what went wrong and the rule to prevent it.
- Check if the same mistake exists elsewhere in the current session's work.
- After completing a task, reflect: what patterns worked, what didn't, what to remember next time.

## Quality
- [rules based on their language/framework preferences]
- [precision math rules if applicable]
- For non-trivial changes, pause and ask: "Is there a simpler way?" If the fix feels hacky, rethink it.
- Find root causes. No temporary fixes. No suppressing errors to make symptoms go away.
- Minimal impact — changes should only touch what's necessary.

## Code Reuse
- Search the codebase for existing patterns before writing new code.
- Match the project's naming conventions, file structure, and error handling. Don't introduce new patterns unless asked.
- Extract shared logic only after the same pattern appears 3+ times.

## Debt Prevention
- No TODOs without a linked issue. No commented-out code.

## Context Discipline
- Delegate codebase research to subagents — don't pollute main context.
- Scope exploration narrowly. Summarize what changed after completing a task.

## Git
- [rules based on their git workflow preferences]

## Testing
- [rules based on their testing approach]
- Run the specific test for what changed after each meaningful change, not the full suite.
- Never modify tests to make them pass — unless the test itself was wrong.
- Never mark a task complete without proving it works.

## Communication
- Lead with the action, not the reasoning.
- After 2 failed attempts, stop and ask.
```

Tailor the bracketed sections to their actual answers. Remove brackets and replace with real rules. Keep it under 50 lines — this gets loaded into every session, so brevity matters.

## Step 6: Confirm

Show the user what was created/modified:
1. `~/.claude/settings.json` — settings applied
2. `~/.claude/CLAUDE.md` — coding standards saved
3. Remind them to run `/permissions`, `/sandbox`, and `/statusline` manually (these are interactive commands that can't be automated)

Tell the user: "Global setup complete. For each new project, run `/astra:init` to configure project-specific settings."
