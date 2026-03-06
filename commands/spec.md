---
description: Interview the user about a feature and produce a SPEC.md
argument-hint: "[brief feature description]"
---

> **Arguments**: Any text the user provides after the command name serves as input. In Claude Code, this is substituted into $ARGUMENTS automatically.

# Spec Phase

You are conducting a product discovery interview. Your goal is to deeply understand what the user wants to build before any code is written.

## Process

1. **Check for existing spec.** Read the project's CLAUDE.md and README for context. Then check if SPEC.md already exists in the project root.

   **If SPEC.md exists (update mode):**
   - Read it and present a summary: "Your existing spec covers [feature name] with [N] requirements. Sections: [list sections]."
   - Ask: "Do you want to update this spec or start fresh for a different feature?"
   - If updating: ask what changed — new requirements, scope changes, resolved open questions. Only re-interview for the parts that need updating. Preserve sections the user doesn't mention.
   - If starting fresh: proceed with the full interview below.

   **If no SPEC.md exists:** Proceed with the full interview.

2. Interview the user (use AskUserQuestion if available, otherwise ask directly in chat). Ask about:
   - What problem does this solve? Who is the user?
   - What does "done" look like? What's the minimal viable version?
   - Technical constraints — must it integrate with existing systems?
   - Edge cases — what happens when things go wrong?
   - What are you NOT building? (scope boundaries)
   - Performance requirements, security concerns, data model implications

3. Do NOT ask obvious questions. Dig into the hard parts the user might not have considered. Challenge assumptions.

4. Keep interviewing until you've covered all dimensions. Aim for 5-10 focused questions, not 20 shallow ones.

5. Write the complete spec to SPEC.md in the project root with this structure:

```markdown
# Feature: [Name]

## Problem
What problem this solves and for whom.

## Requirements
Numbered list of functional requirements.

## Non-Requirements
What is explicitly out of scope.

## Technical Constraints
Integration points, performance targets, security needs.

## Edge Cases
Known edge cases and how to handle them.

## Open Questions
Anything that needs further clarification.
```

6. After writing SPEC.md, tell the user: "Spec complete. Start a fresh session (`/clear` in Claude Code, new chat in Cursor) and run `/astra:plan` to create the implementation plan."

## If $ARGUMENTS is provided
Use "$ARGUMENTS" as the starting point for the interview. Explore it deeper — don't just accept the description at face value.
