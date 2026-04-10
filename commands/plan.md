---
description: Explore the codebase and create a phased implementation plan
argument-hint: "[feature name or path to SPEC.md]"
---

> **Arguments**: Any text the user provides after the command name serves as input. In Claude Code, this is substituted into $ARGUMENTS automatically.

# Plan Phase

You are creating a detailed, phased implementation plan. You MUST delegate codebase exploration to the planner subagent to keep main context clean.

## Process

0. **Check prerequisites.** If `~/.claude/CLAUDE.md` does not exist or does not contain `<!-- astra:managed -->`, run the `/astra:setup` flow inline (follow `commands/setup.md`). If the project root `CLAUDE.md` does not exist or does not contain `<!-- astra:managed -->`, run the `/astra:init` flow inline (follow `commands/init.md`).

1. **Read the spec**: If $ARGUMENTS points to a file, read it. Otherwise, look for SPEC.md in the project root. If no spec exists, ask the user (use AskUserQuestion if available, otherwise ask directly in chat) to describe what they want to build.

2. **Delegate exploration**: Tell the planner subagent to explore the codebase and identify:
   - Existing patterns and conventions to follow
   - Files that need to be modified vs created
   - Dependencies and integration points
   - Test infrastructure and how to run tests

   Say: "Use the planner subagent to explore the codebase for [feature]."

3. **Create the plan**: Based on the planner's findings, write PLAN.md with the structure defined in the plan-template skill.

4. **Validate with user**: Present the plan summary and ask if the phasing makes sense before proceeding.

5. After the plan is approved, tell the user: "Plan complete. Run `/astra:implement` to start building phase by phase."

## Key Rules

- Prefer delegating exploration to the planner subagent. If subagent delegation is not available, explore directly but keep reads minimal and targeted — summarize findings before continuing.
- Each phase must be completable in under 50% context window.
- Independent phases must be marked for potential parallel execution.
- Every task must have a verification step (test, lint, type-check, or manual check).
