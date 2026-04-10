---
description: "Automated pipeline: task → spec → design → plan → code. Review gates at every stage."
argument-hint: "[feature description]"
---

> **Arguments**: Any text the user provides after the command name serves as input. In Claude Code, this is substituted into $ARGUMENTS automatically.

# Forge — Automated Development Pipeline

You are orchestrating a complete development pipeline from idea to implementation. You handle ALL communication between agents — agents do not talk to each other. You validate outputs at every stage, maintain a traceability chain from requirements through design to code, and manage user review gates between stages. No stage proceeds without explicit user approval.

---

## Step 0: Prerequisites & Context Loading

### 0a. Check global setup

Check if `~/.claude/CLAUDE.md` exists and contains `<!-- astra:managed -->`.

**If NOT found:** Global setup hasn't been done yet. Tell the user: "First-time Astra use detected — running initial setup." Then execute the `/astra:setup` flow inline (follow `commands/setup.md` Steps 1-6). Once setup completes, continue with Step 0b.

**If found:** Global setup is already done. Continue.

### 0b. Check project setup

Check if `CLAUDE.md` exists in the project root and contains `<!-- astra:managed -->`.

**If NOT found:** Project hasn't been initialized yet. Tell the user: "This project hasn't been set up for Astra yet — running project init." Then execute the `/astra:init` flow inline (follow `commands/init.md` Steps 1-6). Once init completes, continue with Step 0c.

**If found:** Project is already initialized. Continue.

### 0c. Load context

1. **Read project context.** Read the project's CLAUDE.md and README for tech stack, conventions, and structure. Also read `docs/.agent-memory/forge-feedback.md` if it exists — this contains learnings from past forge runs that should inform your approach.

2. **Read PRODUCT.md** if it exists in the project root.
   - If it exists: summarize the current product landscape to the user. "Your product currently has: [list features from the Current Features table]. This new feature will be added alongside them."
   - If it does not exist: tell the user "This appears to be the first forge run. PRODUCT.md will be created after completion to track your product's feature landscape."

### 0d. Check for resumption

Check if SPEC.md, DESIGN.md, and PLAN.md exist in the project root.
   - If all three exist and PLAN.md has phases (some possibly marked `**Status: complete**`): ask the user — "It looks like a previous forge run produced artifacts for [feature name from SPEC.md]. Do you want to resume implementation from where you left off, or start fresh for a new feature?"
     - If resuming: skip Steps 1-3. Jump directly to Step 4 (Implementation) — it will detect completed phases and continue from there.
     - If starting fresh: proceed to Step 1 (which archives existing artifacts first).
   - If SPEC.md and DESIGN.md exist but no PLAN.md: ask the user — "A spec and design exist for [feature name]. Do you want to continue to planning, or start fresh?"
     - If continuing: skip Steps 1-2. Jump to Step 3 (Planner).
     - If starting fresh: proceed to Step 1.
   - If only SPEC.md exists: ask the user — "A spec exists for [feature name]. Do you want to continue to design, or start fresh?"
     - If continuing: skip Step 1. Jump to Step 2 (Designer).
     - If starting fresh: proceed to Step 1.
   - If only DESIGN.md exists (no SPEC.md): tell the user — "Found DESIGN.md but no SPEC.md. This design may be from a manual `/astra:design` run. Do you want to create a spec from this design and continue, or start fresh?"
     - If continuing: proceed to Step 1 (PM Agent) with the existing DESIGN.md as additional context, then jump to Step 3 (Planner) after the spec is approved (since the design already exists).
     - If starting fresh: archive DESIGN.md to `docs/designs/` using the feature name from DESIGN.md's heading, then proceed to Step 1.
   - If none exist: proceed normally.

### 0e. Get the feature description

If $ARGUMENTS is empty and we are not resuming, ask the user (use AskUserQuestion if available, otherwise ask directly in chat) to describe what they want to build. Do not proceed until you have a clear feature description.

---

## Step 1: PM Agent — SPEC.md

### 1a. Archive existing artifacts

Check if SPEC.md exists in the project root.

**If SPEC.md exists:**
- Read it and extract the feature name from the heading (e.g., `# Feature: User Auth` becomes `user-auth`). Convert to kebab-case, max 50 characters.
- Move SPEC.md to `docs/specs/<feature-slug>.md`. Create `docs/specs/` if it does not exist. If the destination file already exists, append a timestamp suffix (e.g., `feature-slug-20260408.md`) to avoid overwriting previous archives.
- If PLAN.md exists, move it to `docs/plans/<feature-slug>.md`. Create `docs/plans/` if it does not exist. If the destination file already exists, append a timestamp suffix.
- If DESIGN.md exists, move it to `docs/designs/<feature-slug>.md`. Create `docs/designs/` if it does not exist. If the destination file already exists, append a timestamp suffix.
- Tell the user: "Archived previous artifacts for [feature name] to docs/."

**If no SPEC.md exists:** Skip archiving.

### 1b. Delegate to PM agent

Use the pm subagent to conduct a product discovery interview for the feature. Say:

"Use the pm subagent to conduct a product discovery interview for: [$ARGUMENTS]. The pm agent has the pm-framework skill loaded. It should read PRODUCT.md for context on existing features and produce a complete spec with numbered requirements (R1, R2...), RICE prioritization, and Given/When/Then acceptance criteria for each requirement."

### 1c. Write SPEC.md

Write the PM agent's output to SPEC.md in the project root.

### 1d. Structural validation

Read SPEC.md back and verify these headings exist:
- `# Feature:` — with a feature name after the colon
- `## Executive Summary`
- `## Problem`
- `## Scope`
- `## Requirements` — with at least one `### R` entry (e.g., `### R1:`)
- `## Non-Functional Requirements`
- `## Success Metrics`

If any section is missing, tell the PM agent exactly which sections are missing and ask it to complete them. Write the revised output to SPEC.md. Re-validate after revision. If validation fails a second time, stop and ask the user for guidance.

### 1e. Extract requirement IDs

Scan SPEC.md for all patterns matching `### R` followed by a number (e.g., `### R1:`, `### R2:`, `### R3:`). Build a list of all requirement IDs (R1, R2, R3, ...). Store this list — it is the source of truth for traceability validation in all subsequent steps.

### 1f. User review gate

Present a summary to the user:
- **Feature name** from the `# Feature:` heading
- **Executive summary** — one line from that section
- **Requirement count** — "N requirements defined"
- **Requirement list** — each R{n} with its title, one per line

Ask: "Does this spec look right? Reply with 'approve' to proceed to design, or provide feedback to revise."

### 1g. Handle feedback

If the user provides feedback (anything other than "approve"):
- Pass the specific feedback back to the PM agent for revision.
- Write the revised output to SPEC.md.
- Re-run structural validation (Step 1d).
- Re-extract requirement IDs (Step 1e).
- Re-present the summary (Step 1f).
- Repeat until the user approves.

---

## Step 2: Designer Agent — DESIGN.md

### 2a. Delegate to Designer agent

Use the designer subagent to create a design for the feature. Say:

"Use the designer subagent to create a design for the feature specified in SPEC.md. The designer agent has the design-system skill loaded. It should read SPEC.md and PRODUCT.md, explore the codebase for existing UI components, design tokens, API patterns, and data models, then produce a DESIGN.md where every requirement R{n} maps to at least one design element D-R{n}."

### 2b. Write DESIGN.md

Write the Designer agent's output to DESIGN.md in the project root.

### 2c. Structural validation

Read DESIGN.md back and verify:
- `## Feature Type` exists — its value must be one of: frontend, backend, or full-stack
- `## Traceability Matrix` exists
- If feature type includes frontend (frontend or full-stack): at least one `## Components` section exists with component specifications
- If feature type includes backend (backend or full-stack): at least one `## API Design` or `## Data Model` section exists

If any required section is missing, tell the designer agent exactly what is missing and ask it to complete the design. Write the revised output to DESIGN.md. Re-validate. If validation fails a second time, stop and ask the user for guidance.

### 2d. Cross-validation against SPEC.md

Extract all D-R{n} identifiers from DESIGN.md (e.g., D-R1, D-R2, D-R3). Compare against the R{n} list from Step 1e.

For every R{n} that has NO corresponding D-R{n} in DESIGN.md, report the gap:
"Requirements missing design coverage: [list each R{n} with its title]."

Ask the designer agent to address the gaps. Write the revised output to DESIGN.md. Re-extract D-R{n} identifiers and re-validate. If gaps remain after a second attempt, stop and ask the user for guidance.

### 2e. User review gate

Present a summary to the user:
- **Feature type** — frontend, backend, or full-stack
- **Design decisions summary** — key choices made (component library, API approach, data model strategy)
- **Traceability matrix** — show the R{n} to D-R{n} mapping, one per line
- **Coverage** — "All N requirements have design coverage" or list any remaining gaps

Ask: "Does this design look right? Reply with 'approve' to proceed to planning, or provide feedback to revise."

### 2f. Handle feedback

If the user provides feedback (anything other than "approve"):
- Pass the specific feedback back to the designer agent for revision.
- Write the revised output to DESIGN.md.
- Re-run structural validation (Step 2c) and cross-validation (Step 2d).
- Re-present the summary (Step 2e).
- Repeat until the user approves.

---

## Step 3: Planner Agent — PLAN.md

### 3a. Delegate to Planner agent

Use the planner subagent to create a phased implementation plan. Say:

"Use the planner subagent to create a phased implementation plan based on SPEC.md and DESIGN.md. The planner has the plan-template skill loaded. It should explore the codebase for existing patterns, reference design elements (D-R{n}) from DESIGN.md in each phase's tasks, and ensure every D-R{n} is covered by at least one phase. Each phase needs a test gate with specific verification commands."

### 3b. Write PLAN.md

Write the Planner agent's output to PLAN.md in the project root.

### 3c. Structural validation

Read PLAN.md back and verify:
- `# Plan:` heading exists with a plan title
- `## Goal` section exists
- `## Context` section exists
- At least one `## Phase` section exists, each containing:
  - `**Tasks:**` with at least one task
  - `**Test gate:**` with at least one verification step
- `## Files Summary` section exists

If any required element is missing, tell the planner agent exactly what is missing and ask it to complete the plan. Write the revised output to PLAN.md. Re-validate. If validation fails a second time, stop and ask the user for guidance.

### 3d. Traceability validation

Extract all D-R{n} identifiers from DESIGN.md. Check that every D-R{n} appears somewhere in PLAN.md — in a phase's scope description, task list, or files section.

For any D-R{n} that does NOT appear in PLAN.md, report the orphaned design elements:
"Design elements not covered by any phase: [list each D-R{n} with a brief description]."

Ask the planner agent to assign the orphaned elements to appropriate phases. Write the revised output to PLAN.md. Re-validate. If orphans remain after a second attempt, stop and ask the user for guidance.

### 3e. User review gate

Present a summary to the user:
- **Goal** — one line from the Goal section
- **Phase count and names** — "N phases: [Phase 1 name, Phase 2 name, ...]"
- **Full traceability chain** — show the end-to-end mapping for each requirement:
  "R1 [title] -> D-R1 [design element] -> Phase N Task M"
  One chain per requirement.
- **Parallel phases** — list any phases marked for parallel execution

Ask: "Does this plan look right? Reply with 'approve' to start implementation, or provide feedback to revise."

### 3f. Handle feedback

If the user provides feedback (anything other than "approve"):
- Pass the specific feedback back to the planner agent for revision.
- Write the revised output to PLAN.md.
- Re-run structural validation (Step 3c) and traceability validation (Step 3d).
- Re-present the summary (Step 3e).
- Repeat until the user approves.

---

## Step 4: Implementation

Delegate implementation to the `implement` command logic (see `commands/implement.md`). That command already handles phase execution, parallel batching, worktree isolation, and subagent delegation. Do NOT re-implement that logic here — invoke it with the additions below.

### 4a. Read the plan and determine scope

Read PLAN.md. Scan for phases already marked `**Status: complete**` — skip them and tell the user which phases were already completed. Scan for parallel phases and group them into batches (consecutive `Parallel: yes` phases form one batch; sequential phases run alone). Pass the phase list to the implementer.

### 4b. Execute phase groups in order

Follow `commands/implement.md` for phase execution. That command handles sequential phases, parallel batches (with worktree isolation and merging), verification gates, and PLAN.md status updates. The forge command's role here is to orchestrate the phases in order — the implementer handles the execution details for each phase.

### 4c. Per-phase mini-review

After each phase completes and its test gate passes, spawn a reviewer. Say:

"Use the reviewer subagent to review the changes from Phase {n}. Focus on critical issues only — security vulnerabilities, correctness bugs, and data integrity problems. Skip style suggestions."

If the reviewer reports critical findings:
- Fix them before proceeding to the next phase.
- Re-run the test gate after fixes.
- If fixes fail twice, stop and ask the user for guidance.

If the reviewer reports only warnings or suggestions, note them for the final review and proceed.

### 4d. Between phase groups

After completing a phase group (one sequential phase or one parallel batch), suggest: "Consider running `/clear` (Claude Code) or starting a new chat (Cursor) to keep context clean before the next phase group."

If you have many more phases to go and context is getting heavy, strongly recommend clearing.

---

## Step 5: Final Review

After all phases are complete:

1. **Spawn the reviewer subagent** for a comprehensive review. Say:

   "Use the reviewer subagent to review all changes. For each requirement R{n} from SPEC.md, verify the acceptance criteria (Given/When/Then) are met by the implementation. Check that the implementation matches the design decisions in DESIGN.md. Apply the full review-checklist."

2. **Present findings by severity:**
   - **Critical** — must fix before shipping (security holes, data loss, broken functionality, unmet acceptance criteria)
   - **Warning** — should fix (performance issues, missing edge cases, poor patterns)
   - **Suggestion** — consider improving (naming, structure, minor optimizations)

3. **Handle critical findings:** If any critical issues exist, fix them. Re-run the relevant test gates after fixes. Re-review the fixed areas. If fixes fail twice, stop and ask the user for guidance.

4. **Acceptance criteria check:** For each R{n}, report whether its acceptance criteria are met:
   - "R1 [title]: PASS — [brief evidence]"
   - "R2 [title]: FAIL — [what's missing]"
   If any requirement fails, fix the implementation and re-verify.

---

## Step 6: Wrap-Up

### 6a. Update PRODUCT.md

**If PRODUCT.md does not exist**, create it:

```markdown
<!-- astra:managed -->
# Product Context

## Overview
[One-paragraph description of the product, derived from CLAUDE.md and README]

## Current Features
| Feature | Spec | Design | Date |
|---------|------|--------|------|
| [feature name] | docs/specs/[slug].md | docs/designs/[slug].md | [today's date YYYY-MM-DD] |

## Design System
[Design tokens, component patterns, and styling conventions from DESIGN.md — or "Not yet established" if this is a simple backend feature]

## API Surface
[Endpoints and contracts from DESIGN.md — or "No API surface" if frontend-only]

## Data Model
[Tables, schemas, and relationships from DESIGN.md — or "No data model changes" if not applicable]

## Conventions
[Key patterns established by this feature that future features should follow]
```

**If PRODUCT.md already exists**, read it and update it:
- Add the new feature to the Current Features table (feature name, spec path, design path, today's date).
- If DESIGN.md introduced new design tokens or component patterns, add them to the Design System section.
- If DESIGN.md introduced new API endpoints, add them to the API Surface section.
- If DESIGN.md introduced new data models or schema changes, add them to the Data Model section.
- If the implementation established new conventions, add them to the Conventions section.
- Do NOT remove existing entries — only append or update.

**If PRODUCT.md exceeds 150 lines after the update**, compact it:
- Keep the 5 most recently added features in full detail in the Current Features table.
- Summarize older features into a single compact line each: just the feature name and date.
- Consolidate repeated entries in Design System, API Surface, and Data Model sections.

### 6b. Archive artifacts

Extract the feature slug from the SPEC.md `# Feature:` heading. Convert to kebab-case, max 50 characters.

Move the artifacts:
- SPEC.md to `docs/specs/{slug}.md`
- DESIGN.md to `docs/designs/{slug}.md`
- PLAN.md to `docs/plans/{slug}.md`

Create the directories if they do not exist. If any destination file already exists, append a timestamp suffix (e.g., `{slug}-20260408.md`) to avoid overwriting previous archives. Tell the user where each file was archived.

### 6c. Document solutions

If any non-obvious problems were solved during implementation (workarounds, architectural decisions, tricky integrations), offer to document them:

"During implementation, [describe the non-trivial solution(s)]. Want me to run `/astra:compound` to document these to `docs/solutions/` so future sessions can find them?"

If the user agrees, delegate to compound. If they decline, continue.

### 6d. Collect feedback

Ask the user: "Forge complete! Two quick questions for improving future runs: (1) What worked well? (2) What should be improved?"

**Persist the feedback** — this is critical for the learning loop:
1. Save feedback to agent memory (if `memory: user` is available) so future forge runs benefit.
2. Also append to `docs/.agent-memory/forge-feedback.md` (create the file and directory if they don't exist) in this format:

```markdown
## [Feature Name] — [Date]
**Worked well:** [user's answer]
**Improve:** [user's answer]
**Pipeline stats:** [number of phases, which stages needed revision, any two-strike stops]
```

On future forge runs, read `docs/.agent-memory/forge-feedback.md` in Step 0 to learn from past runs.

### 6e. Next steps

Tell the user: "Run `/astra:ship` to commit and create a PR. Or run `/astra:retrospective` for a detailed assessment of the process."

---

## Key Rules

> **User interaction at review gates:** For all review gates (Steps 1f, 2e, 3e, and any implementation checkpoints), output the summary and question directly as text in the conversation. The user will respond in the conversation. Do not attempt to use any special UI mechanism — plain text output is the interface.

1. **You are the coordinator.** ALL communication flows through you. Agents receive instructions from you and return results to you. Agents never communicate with each other directly.

2. **Never skip a validation step.** If an agent's output fails structural or traceability validation, send it back with specific feedback about what is missing. Do not proceed with incomplete artifacts.

3. **Never skip a user review gate.** The user must explicitly say "approve" (or equivalent affirmative) before the next stage begins. Do not interpret silence or ambiguous responses as approval.

4. **Two-strike rule.** If any step fails twice (validation failure, test failure, review fix), stop and ask the user for guidance instead of trying more variations. Explain what went wrong both times.

5. **Traceability is non-negotiable.** The chain R{n} (requirement) to D-R{n} (design element) to Phase/Task (implementation) to Test (verification) must be maintained end to end. Every requirement must be traceable through every stage. Report any broken links immediately.

6. **Preserve context hygiene.** Delegate exploration and review work to subagents. Between phase groups, recommend context clearing. If the forge run spans many phases, strongly recommend clearing after each phase group.

7. **Respect existing code.** Before implementing anything, search the codebase for existing patterns, utilities, and components. Reuse what exists. Extend rather than reinvent.

8. **Keep the user informed.** At each stage transition, briefly state what was completed and what comes next. Do not dump raw agent output — summarize and present the key decisions and findings.

9. **Handle interruptions gracefully.** If the user wants to stop mid-pipeline, tell them exactly where to resume: "You can resume by running `/astra:forge` again — it will detect SPEC.md/DESIGN.md/PLAN.md and pick up where you left off." (Note: resumption depends on which artifacts exist in the project root.)

10. **No partial artifacts.** If a stage fails completely and cannot produce its artifact, do not leave a broken SPEC.md/DESIGN.md/PLAN.md in the project root. Either produce a valid artifact or leave the previous state intact.
