---
description: Execute a plan phase-by-phase with verification gates
argument-hint: "[path to PLAN.md or phase number]"
---

> **Arguments**: Any text the user provides after the command name serves as input. In Claude Code, this is substituted into $ARGUMENTS automatically.

# Implement Phase

You are executing an implementation plan phase by phase. Each phase must pass its verification gate before moving to the next.

## Process

1. **Read the plan and determine scope**:
   - Look for PLAN.md in the project root.
   - If $ARGUMENTS is a file path, read that file as the plan instead.
   - If $ARGUMENTS is a phase reference (e.g., "phase 3", "3", "Phase 3: Auth"), read PLAN.md and execute **only that phase** — skip straight to it, run its tasks and verification gate, then stop. Do not execute other phases.
   - If no plan exists, tell the user to run `/astra:plan` first.
   - Scan for phases already marked `**Status: complete**`. Skip them and tell the user which phases were already completed.

2. **Scan for parallel phases** (skip this step if running a single phase): After reading the plan, identify all phases marked `Parallel: yes`. Group them into batches — consecutive parallel phases form one batch. Sequential phases (`Parallel: no` or unmarked) run alone.

3. **Execute phase groups in order**:

   **For a sequential phase:**
   a. Announce which phase you're starting and what it involves.
   b. Before writing new code, search the codebase for existing similar patterns or utilities. Reuse what exists.
   c. Implement the tasks for this phase.
   d. Run the verification gate (tests, lint, type-check) defined in the plan.
   e. If verification fails, fix issues before moving on. Do not skip failing tests.
   f. Summarize what was done: files created, files modified, tests added.
   g. Update PLAN.md — check off this phase's test gate items (`- [x]`) and append `**Status: complete**` to the phase heading (e.g., `## Phase 2: Auth — **Status: complete**`).

   **For a parallel batch:**
   a. Announce which phases are running in parallel.
   b. Verify the parallel phases have no overlapping files (check "files to create" and "files to modify" across phases). If they share files, run them sequentially instead and warn the user.
   c. Spawn one implementer subagent per phase. Both editors support worktree-based parallel execution — each subagent gets its own copy of the repo. In Claude Code, use `isolation: worktree`. In Cursor, subagents automatically run in worktrees when launched in parallel.
   d. Wait for all subagents to complete.
   e. Merge each worktree's changes back to the main branch via `git merge`. Resolve any conflicts before proceeding.
   f. Run verification gates for all phases in the batch. If any fail, fix before proceeding.
   g. Summarize what each parallel phase accomplished.
   h. Update PLAN.md — mark all phases in this batch as complete (same format as sequential phases).

4. **Between phase groups**: Suggest the user run `/clear` (Claude Code) or start a new chat (Cursor) to keep context clean before the next group.

5. **After the final phase**: Spawn the reviewer subagent to review all changes. Say: "Use the reviewer subagent to review the implementation."

## Key Rules

- Never skip a verification gate. If tests don't exist for the change, write them first.
- If you've read many files and context feels heavy, summarize findings before continuing.
- If something fails twice, stop and ask the user rather than trying more variations.
- After completing all phases, tell the user: "Implementation complete. Run `/astra:review` for a full review, then `/astra:ship` to commit and create a PR."
