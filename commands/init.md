---
description: Set up the current project for Astra — generates CLAUDE.md and path-specific rules
---

# Project Setup

You are configuring the current project for optimal Astra usage. This command is idempotent — safe to run again when the project evolves.

## Step 1: Explore the project

Before asking anything, silently explore:
- Read `README.md`, `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, or similar to detect the tech stack.
- Check directory structure — identify `backend/`, `frontend/`, `src/`, `app/`, `server/`, `api/`, `lib/`, `test/`, `tests/` directories.
- Check for existing `CLAUDE.md`, `.claude/rules/`, `.cursorrules`, `.github/`, `tsconfig.json`, `eslint.config.*`, `.prettierrc`, `pytest.ini`, `vitest.config.*`, etc.
- Identify test runner, linter, formatter, build tool from config files.

**Detect re-run:** Check if `CLAUDE.md` exists and contains `<!-- astra:managed -->` on its first line. If yes, this is a re-run. Also check `.claude/rules/` for files containing `<!-- astra:managed -->`.

## Step 2: Interview the user

Ask the user (use AskUserQuestion if available, otherwise ask directly in chat) for things you can't detect from the codebase:

1. "I detected [stack summary]. Is that correct, or is there anything I'm missing?"
2. "Any areas of the codebase I should treat differently?" (e.g., legacy code that follows old patterns, auto-generated files to never touch, deprecated patterns being migrated)

Keep it to these 2 questions. Skip anything you can answer from the codebase.

**On re-run:** Instead of the full interview, ask: "Your project config exists. I can see [summary of what changed in the codebase since last run — new directories, changed deps, etc.]. Want me to update the config to reflect these changes, or do you have specific things to change?"

## Step 3: Generate project CLAUDE.md

**Marker rule:** Always include `<!-- astra:managed -->` as the very first line. This marks the file as Astra-generated so future re-runs can detect it.

**On re-run (marker exists):**
1. Generate the new version based on current codebase + interview updates.
2. Show the user a **summary of what changed** (new sections, updated commands, removed directories, etc.).
3. Ask: "Here's what I'd update. Apply these changes?" Only write the file after the user approves.
4. If the user has added custom content below the Astra-managed sections, preserve it exactly as-is.

**On fresh run (no existing file):**
Create the file directly. Structure:

```markdown
<!-- astra:managed -->
# [Project Name]

## Stack
[Detected tech stack, frameworks, key dependencies]

## Structure
[Key directories and what they contain — keep it to 5-8 lines max]

## Development
- Test: `[detected test command]`
- Lint: `[detected lint command]`
- Build: `[detected build command]`
- Dev: `[detected dev command]`

## Conventions
[Project-specific rules from the interview — naming, patterns, things to avoid]
```

Tailor to the project. Remove sections that don't apply. Keep it under 40 lines — this gets loaded into every session.

## Step 4: Generate path-specific rules

**Marker rule:** Every Astra-generated rule file must include `<!-- astra:managed -->` as the first line of the body (immediately after the closing `---` of the frontmatter). This ensures frontmatter parsing works correctly while still marking the file as Astra-generated.

**On re-run:**
1. Read all files in `.claude/rules/`.
2. Files **with** `<!-- astra:managed -->` — regenerate based on current codebase. Show the user what changed and ask for approval before overwriting.
3. Files **without** `<!-- astra:managed -->` — these are user-created. Never touch them.
4. If new directories exist that aren't covered by any rule file, propose new rule files.

**On fresh run:**
Create `.claude/rules/` and add rule files based on the project structure.

**Only create rules for directories that actually exist.** Each rule file should:
- Have a `paths:` frontmatter matching the relevant directories
- Include `<!-- astra:managed -->` as the first line of the body (after the closing `---`)
- Contain 3-5 conventions specific to that area of the codebase
- Reference existing patterns (e.g., "follow the pattern in src/api/users.ts for new API routes")

Example for a full-stack project:

`.claude/rules/backend.md`:
```markdown
---
paths: ["backend/**"]
---
<!-- astra:managed -->
- Follow existing route patterns in backend/app/api/ for new endpoints.
- Use the project's ORM models from backend/app/models/ — never write raw SQL.
- All new endpoints need tests in backend/tests/.
```

`.claude/rules/frontend.md`:
```markdown
---
paths: ["frontend/**"]
---
<!-- astra:managed -->
- Use components from frontend/src/components/ui/ before creating new ones.
- Follow the data fetching pattern in existing page components.
- All new pages need to be responsive (mobile-first).
```

Adapt the rules to what the project actually uses. Don't create generic rules — reference real files and patterns from the codebase.

**For simpler single-directory projects**, a single rule file may suffice or none at all if CLAUDE.md covers everything.

**Also generate Cursor rules** if the project uses Cursor (check for `.cursor/` directory or ask). Create matching rules in `.cursor/rules/` with `.mdc` extension. The rule body content is identical — only the frontmatter format differs:

| | Claude Code (`.claude/rules/backend.md`) | Cursor (`.cursor/rules/backend.mdc`) |
|---|---|---|
| Marker | `<!-- astra:managed -->` (first line of body, after frontmatter) | `<!-- astra:managed -->` (first line of body, after frontmatter) |
| Frontmatter | `paths: ["backend/**"]` | `description: Backend conventions` + `globs: backend/**` + `alwaysApply: false` |
| Body | Same conventions | Same conventions |

Apply the same re-run logic (detect marker, regenerate managed files, preserve user-created files) to `.cursor/rules/` as well.

## Step 5: Update .gitignore

Check the project's `.gitignore` file. If it doesn't already contain `docs/.agent-memory/`, append it:

```
# Astra agent memory (personal, not shared)
docs/.agent-memory/
```

If no `.gitignore` exists, create one with this entry. This prevents personal agent learnings from being committed to the team's repository.

## Step 6: Confirm

Show the user what was done:
- For each file, say **created** (new) or **updated** (changed) or **unchanged** (no diff).
1. `CLAUDE.md` — project context (show contents; on re-run, summarize what changed)
2. `.claude/rules/*.md` — Claude Code rules (list them with a one-line summary each)
3. `.cursor/rules/*.mdc` — Cursor rules (list them if generated)
4. `.gitignore` — updated with `docs/.agent-memory/` (if not already present)

Tell the user: "Project setup complete. You're ready to start building. Use `/astra:spec` for new features or `/astra:plan` if you already know what to build."
