---
description: Interview the user about a feature and produce a SPEC.md
argument-hint: "[brief feature description]"
---

> **Arguments**: Any text the user provides after the command name serves as input. In Claude Code, this is substituted into $ARGUMENTS automatically.

# Spec Phase

You are creating a product specification. You MUST delegate the product discovery interview to the pm subagent to keep main context clean and leverage the pm-framework skill.

## Process

0. **Check prerequisites.** If `~/.claude/CLAUDE.md` does not exist or does not contain `<!-- astra:managed -->`, tell the user: "Global setup needed first." Then run the `/astra:setup` flow inline (follow `commands/setup.md`). If the project root `CLAUDE.md` does not exist or does not contain `<!-- astra:managed -->`, tell the user: "Project not initialized yet." Then run the `/astra:init` flow inline (follow `commands/init.md`).

1. **Check for existing spec.** Read the project's CLAUDE.md and README for context. Then check if SPEC.md already exists in the project root.

   **If SPEC.md exists:**
   - Read it and present a summary: "Your existing spec covers [feature name] with [N] requirements. Sections: [list sections]."
   - Ask: "Do you want to update this spec or start fresh for a different feature?"
   - If updating: ask what changed — new requirements, scope changes, resolved open questions. Pass the changes to the pm subagent for revision. Preserve sections the user doesn't mention.
   - If starting fresh: **archive first.** Extract the feature name from the existing SPEC.md heading (e.g., `# Feature: User Auth` → `user-auth`). Move `SPEC.md` to `docs/specs/<feature-name>.md`. If `PLAN.md` also exists, move it to `docs/plans/<feature-name>.md`. If `DESIGN.md` also exists, move it to `docs/designs/<feature-name>.md`. Create the directories if they don't exist. Then proceed with the full interview below.

   **If no SPEC.md exists:** Proceed with the full interview.

2. **Delegate to the pm subagent:**

   "Use the pm subagent to conduct a product discovery interview for: [$ARGUMENTS or the user's description]. The pm agent has the pm-framework skill loaded. It should read PRODUCT.md for context on existing features and produce a SPEC.md with numbered requirements (R1, R2...), RICE prioritization, and Given/When/Then acceptance criteria."

3. **Write** the pm agent's output to SPEC.md in the project root.

4. **Present the spec** to the user: show the feature name, executive summary, and list all R{n} requirements with their titles.

5. After writing SPEC.md, tell the user: "Spec complete. Start a fresh session (`/clear` in Claude Code, new chat in Cursor) and run `/astra:design` to create the design document, or `/astra:plan` to go straight to planning."

## If $ARGUMENTS is provided
Pass "$ARGUMENTS" to the pm subagent as the starting point for the interview. The pm agent will explore it deeper — it won't just accept the description at face value.

## Key Rules

- Prefer delegating to the pm subagent. If subagent delegation is not available, conduct the interview directly but follow the pm-framework methodology: pre-draft questioning, numbered requirements with R{n} IDs, Given/When/Then acceptance criteria, RICE prioritization.
- Requirements must be agent-consumable: numbered, testable, concrete. No vague language.
