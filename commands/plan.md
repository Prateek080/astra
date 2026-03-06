---
description: Explore the codebase and create a phased implementation plan
argument-hint: "[feature name or path to SPEC.md]"
---

# Plan Phase

You are creating a detailed, phased implementation plan. You MUST delegate codebase exploration to the planner subagent to keep main context clean.

## Process

1. **Read the spec**: If $ARGUMENTS points to a file, read it. Otherwise, look for SPEC.md in the project root. If no spec exists, ask the user to describe what they want to build.

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

- Prefer delegating exploration to the planner subagent. If the Agent tool is unavailable, explore directly but keep reads minimal and targeted — summarize findings before continuing.
- Each phase must be completable in under 50% context window.
- Independent phases must be marked for potential parallel execution.
- Every task must have a verification step (test, lint, type-check, or manual check).
