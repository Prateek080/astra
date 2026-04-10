---
description: Create a technical design document with API contracts, data models, and architecture decisions
argument-hint: "[feature name or path to SPEC.md]"
---

> **Arguments**: Any text the user provides after the command name serves as input. In Claude Code, this is substituted into $ARGUMENTS automatically.

# Architect Phase

You are creating a detailed, implementable technical design document. You MUST delegate codebase exploration and technical design work to the architect subagent to keep main context clean.

## Process

0. **Check prerequisites.** If `~/.claude/CLAUDE.md` does not exist or does not contain `<!-- astra:managed -->`, run the `/astra:setup` flow inline (follow `commands/setup.md`). If the project root `CLAUDE.md` does not exist or does not contain `<!-- astra:managed -->`, run the `/astra:init` flow inline (follow `commands/init.md`).

1. **Read inputs**: Read SPEC.md — this is required. If $ARGUMENTS points to a file, read it as the spec instead. If no spec exists, ask the user to run `/astra:spec` first.

   Also read DESIGN.md if it exists (UI/UX design informs technical decisions). Also read PLAN.md if it exists (implementation phases inform architecture).

2. **Check for existing technical design**: If TECHNICAL.md already exists, read it and ask the user: "An existing technical design covers [feature name]. Do you want to update it or start fresh?"
   - If updating: pass the specific changes to the architect.
   - If starting fresh: extract the feature name from the first `# ` heading in TECHNICAL.md. Convert to lowercase kebab-case for the slug. Move TECHNICAL.md to `docs/technical/<feature-slug>.md`. Create the directory if it doesn't exist. If the archive destination already exists, append a date suffix (e.g., `feature-slug-20260408.md`).

3. **Delegate technical design**: Tell the architect subagent to explore the codebase and create the technical design.

   Say: "Use the architect subagent to create a technical design for the feature specified in SPEC.md. The architect should read PRODUCT.md for existing context, read DESIGN.md for UI/UX decisions to support, read PLAN.md for implementation phases, explore the codebase for existing API patterns, data models, and service architecture, and produce a TECHNICAL.md where every backend requirement R{n} maps to a technical element T-R{n}."

4. **Write TECHNICAL.md**: Write the architect's output to TECHNICAL.md in the project root.

5. **Validate**: Check that the Traceability Matrix covers all requirements from SPEC.md that have backend implications. Report any gaps. Verify ADRs exist for non-trivial decisions.

6. **Present to user**: Show the technical design summary — ADR list, API endpoint summary, data model entities, traceability matrix.

7. After the design is approved, tell the user: "Technical design complete. Run `/astra:implement` to start building phase by phase, or `/astra:forge` for the full automated pipeline."

## Key Rules

- Prefer delegating to the architect subagent. If subagent delegation is not available, design directly but keep reads minimal and targeted.
- Every technical element must trace to a spec requirement (T-R{n} -> R{n}).
- Technical design must be directly implementable — exact schemas, exact types, exact error contracts.
- ADRs are required for non-trivial decisions (new tables, new dependencies, auth changes).
- Reuse existing codebase patterns. The architect must explore before creating.
