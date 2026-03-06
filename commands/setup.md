---
description: One-time global setup — configures settings, permissions, and coding standards for optimal Astra usage
---

# Global Setup

You are configuring the user's global environment for optimal use with Astra. This command is idempotent — safe to run again to update preferences.

> **Note:** This command configures `~/.claude/` paths (settings, CLAUDE.md). Both Claude Code and Cursor read from this directory for plugin compatibility.

## Step 0: Detect re-run

Read `~/.claude/settings.json` and `~/.claude/CLAUDE.md` if they exist.

**If `~/.claude/CLAUDE.md` exists and contains `<!-- astra:managed -->`:**
This is a re-run. Tell the user: "I found your existing global config. I'll interview you for any changes, generate an updated version, and show you the diff before writing anything."

**If the files don't exist:**
This is a fresh setup. Proceed normally.

## Step 1: Interview the user

Ask the user (use AskUserQuestion if available, otherwise ask directly in chat) to learn their preferences:

1. **Anything else** — "Any other rules you always want Claude to follow across all projects?"

> **Note:** Don't ask about languages, frameworks, test runners, code style, or git workflow here. Stack-specific conventions are handled by `/astra:init`. Git best practices are baked into the template.

Keep it conversational. On re-runs, show the user their current answers from the existing file and ask what they want to change — don't re-ask everything. Don't ask more than necessary.

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

> **Claude Code only**: The following step uses `/permissions`, which is a Claude Code interactive command. In Cursor, tool permissions are managed through Cursor's Settings UI — skip this step.

Tell the user to run `/permissions` and suggest these universal allowlists:

```
Read, Glob, Grep, Edit
Bash(git *)
```

Tell the user they can add stack-specific permissions per project (e.g., `Bash(npm *)`, `Bash(python *)`, `Bash(cargo *)`) — those are best configured in each project's `.claude/settings.local.json` or via `/permissions` when working in that project.

Explain: pre-approving these means Claude won't pause for confirmation on routine operations like checking git status.

## Step 4: Enable safety features

> **Claude Code only**: `/sandbox` and `/statusline` are Claude Code interactive commands. In Cursor, file isolation and context usage are managed through Cursor's built-in UI.

Tell the user:
- Run `/sandbox` to enable file and network isolation — prevents accidental writes outside the project
- Run `/statusline` to show context usage in the terminal — this is essential because **context is the #1 constraint** in Claude Code. When context fills up, Claude loses earlier instructions and quality drops. The status line helps you know when to `/clear` or `/compact`.

## Step 5: Generate global CLAUDE.md

Generate the full CLAUDE.md content based on interview answers.

**Marker rule:** Always include `<!-- astra:managed -->` as the very first line. This marks the file as Astra-generated so future re-runs can detect it.

**On re-run (marker exists):**
1. Generate the new version based on updated interview answers.
2. Show the user a **side-by-side summary** of what changed (sections added, removed, or modified).
3. Ask: "Here's what I'd change. Apply these updates?" Only write the file after the user approves.
4. If the user has added custom sections (anything not in the template below), preserve them exactly as-is at the end of the file.

**On fresh run (no existing file):**
Create the file directly.

The following sections are mandatory — include them in every generated CLAUDE.md. These are stack-agnostic principles that apply to all projects. Use them exactly as written — no customization needed.

```markdown
<!-- astra:managed -->
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
- Use conventional commits (feat:, fix:, chore:, refactor:, docs:, test:).
- Keep commits atomic — one logical change per commit.

## Testing
- Run the specific test for what changed after each meaningful change, not the full suite.
- Never modify tests to make them pass — unless the test itself was wrong.
- Never mark a task complete without proving it works.

## Communication
- Lead with the action, not the reasoning.
- After 2 failed attempts, stop and ask.
```

Do not add any language-specific or stack-specific rules — those belong in the project-level CLAUDE.md generated by `/astra:init`. Keep the final file under 50 lines — this gets loaded into every session, so brevity matters.

## Step 6: Confirm

Show the user what was done:
1. `~/.claude/settings.json` — created / updated (specify which)
2. `~/.claude/CLAUDE.md` — created / updated (specify which, summarize changes on re-run)
3. **Claude Code only:** Remind them to run `/permissions`, `/sandbox`, and `/statusline` manually (these are interactive commands that can't be automated). **Cursor:** Skip this — permissions and safety are managed in Cursor's Settings UI.

Tell the user: "Global setup complete. For each new project, run `/astra:init` to configure project-specific settings."
