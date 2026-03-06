---
description: Set up the current project for Astra — generates CLAUDE.md and path-specific rules
---

# Project Setup

You are configuring the current project for optimal Claude Code + Astra usage. This runs once per project.

## Step 1: Explore the project

Before asking anything, silently explore:
- Read `README.md`, `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, or similar to detect the tech stack.
- Check directory structure — identify `backend/`, `frontend/`, `src/`, `app/`, `server/`, `api/`, `lib/`, `test/`, `tests/` directories.
- Check for existing `CLAUDE.md`, `.claude/rules/`, `.cursorrules`, `.github/`, `tsconfig.json`, `eslint.config.*`, `.prettierrc`, `pytest.ini`, `vitest.config.*`, etc.
- Identify test runner, linter, formatter, build tool from config files.

## Step 2: Interview the user

Use AskUserQuestion for things you can't detect from the codebase:

1. "I detected [stack summary]. Is that correct, or is there anything I'm missing?"
2. "Any project-specific conventions not captured in config files?" (e.g., naming patterns, folder organization rules, API response format)
3. "What's the test command?" (if not detectable from package.json scripts or similar)
4. "Any areas of the codebase I should treat differently?" (e.g., legacy code that follows old patterns, auto-generated files to never touch)

Keep it to 2-4 questions. Skip anything you can answer from the codebase.

## Step 3: Generate project CLAUDE.md

Create `CLAUDE.md` in the project root (or update if one exists). Structure:

```markdown
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

Keep it under 30 lines. This gets loaded into every session for this project, so only include what Claude needs to know every time.

## Step 4: Generate path-specific rules

Create `.claude/rules/` directory and add rule files based on the project structure you detected:

**Only create rules for directories that actually exist.** Each rule file should:
- Have a `paths:` frontmatter matching the relevant directories
- Contain 3-5 conventions specific to that area of the codebase
- Reference existing patterns (e.g., "follow the pattern in src/api/users.ts for new API routes")

Example for a full-stack project:

`.claude/rules/backend.md`:
```markdown
---
paths: ["backend/**"]
---
- Follow existing route patterns in backend/app/api/ for new endpoints.
- Use [ORM] models from backend/app/models/ — never write raw SQL.
- All new endpoints need tests in backend/tests/.
```

`.claude/rules/frontend.md`:
```markdown
---
paths: ["frontend/**"]
---
- Use components from frontend/src/components/ui/ before creating new ones.
- Follow the data fetching pattern in existing page components.
- All new pages need to be responsive (mobile-first).
```

Adapt the rules to what the project actually uses. Don't create generic rules — reference real files and patterns from the codebase.

**For simpler single-directory projects**, a single rule file may suffice or none at all if CLAUDE.md covers everything.

## Step 5: Confirm

Show the user what was created:
1. `CLAUDE.md` — project context (show contents)
2. `.claude/rules/*.md` — path-specific rules (list them with a one-line summary each)

Tell the user: "Project setup complete. You're ready to start building. Use `/astra:spec` for new features or `/astra:plan` if you already know what to build."
