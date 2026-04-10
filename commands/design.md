---
description: Create an implementable design document from a spec or feature description
argument-hint: "[feature name or path to SPEC.md]"
---

> **Arguments**: Any text the user provides after the command name serves as input. In Claude Code, this is substituted into $ARGUMENTS automatically.

# Design Phase

You are creating a detailed, implementable design document. You MUST delegate codebase exploration and design work to the designer subagent to keep main context clean.

## Process

0. **Check prerequisites.** If `~/.claude/CLAUDE.md` does not exist or does not contain `<!-- astra:managed -->`, run the `/astra:setup` flow inline (follow `commands/setup.md`). If the project root `CLAUDE.md` does not exist or does not contain `<!-- astra:managed -->`, run the `/astra:init` flow inline (follow `commands/init.md`).

1. **Read the spec**: If $ARGUMENTS points to a file, read it. Otherwise, look for SPEC.md in the project root. If no spec exists, ask the user (use AskUserQuestion if available, otherwise ask directly in chat) to describe the feature they want to design.

2. **Check for existing design**: If DESIGN.md already exists, read it and ask the user: "An existing design covers [feature name]. Do you want to update it or start fresh?"
   - If updating: pass the specific changes to the designer.
   - If starting fresh: extract the feature name from the first `# ` heading in DESIGN.md. Convert to lowercase kebab-case for the slug (e.g., "User Authentication" → `user-authentication`). Move DESIGN.md to `docs/designs/<feature-slug>.md`. If PLAN.md also exists, move it to `docs/plans/<feature-slug>.md`. Create the directories if they don't exist. If the archive destination already exists, append a date suffix (e.g., `user-authentication-20260408.md`).
   - If starting fresh and SPEC.md exists, ask: "SPEC.md also exists — is this spec still relevant for the new design, or should it be archived too?"

3. **Delegate design**: Tell the designer subagent to explore the codebase and create the design.

   Say: "Use the designer subagent to design the feature described in [SPEC.md / $ARGUMENTS]. The designer should read PRODUCT.md for existing context, explore the codebase for existing patterns (components, tokens, API structure, data models), and produce a DESIGN.md where every requirement R{n} from the spec maps to a design element D-R{n}."

4. **Write DESIGN.md**: Write the designer's output to DESIGN.md in the project root.

5. **Validate**: Check that the Traceability Matrix covers all requirements from SPEC.md (if SPEC.md exists). Report any gaps.

6. **Present to user**: Show the design summary — feature type, key design decisions, traceability matrix.

7. After the design is approved, tell the user: "Design complete. Run `/astra:plan` to create the implementation plan, or `/astra:forge` for the full automated pipeline."

## Key Rules

- Prefer delegating to the designer subagent. If subagent delegation is not available, design directly but keep reads minimal and targeted.
- Every design element must trace to a spec requirement (D-R{n} -> R{n}).
- Design must be directly implementable — concrete values, not vague descriptions.
- Reuse existing codebase patterns. The designer must explore before creating.
