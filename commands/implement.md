---
description: Execute a plan phase-by-phase with verification gates
argument-hint: "[path to PLAN.md or phase number]"
---

# Implement Phase

You are executing an implementation plan phase by phase. Each phase must pass its verification gate before moving to the next.

## Process

1. **Read the plan**: Look for PLAN.md in the project root, or read the file at $ARGUMENTS. If no plan exists, tell the user to run `/astra:plan` first.

2. **Execute one phase at a time**:
   a. Announce which phase you're starting and what it involves.
   b. Before writing new code, search the codebase for existing similar patterns or utilities. Reuse what exists.
   c. Implement the tasks for this phase.
   d. Run the verification gate (tests, lint, type-check) defined in the plan.
   e. If verification fails, fix issues before moving on. Do not skip failing tests.

3. **After each phase completes**:
   a. Summarize what was done: files created, files modified, tests added.
   b. Suggest the user run `/clear` before starting the next phase to keep context clean.
   c. If the next phase is independent, mention it can be run in parallel using a subagent with worktree isolation.

4. **For independent phases**: Spawn separate subagents with `isolation: worktree` to work in parallel. Each subagent gets its own copy of the repo.

5. **After the final phase**: Spawn the reviewer subagent to review all changes. Say: "Use the reviewer subagent to review the implementation."

## Key Rules

- Never skip a verification gate. If tests don't exist for the change, write them first.
- If you've read many files and context feels heavy, summarize findings before continuing.
- If something fails twice, stop and ask the user rather than trying more variations.
- Don't introduce TODOs without a linked issue. Don't leave commented-out code.
- After completing all phases, tell the user: "Implementation complete. Run `/astra:review` for a full review, then `/astra:ship` to commit and create a PR."
