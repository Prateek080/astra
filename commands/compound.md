---
description: Document a solved problem for future reference — builds a searchable project knowledge base
argument-hint: "[problem description]"
---

# Knowledge Compounding

After solving a non-trivial problem (bug fix, architectural decision, tricky integration, performance optimization), document the solution so the team never has to solve it again.

## Process

1. **Identify what was solved.** If $ARGUMENTS describes it, use that. Otherwise, look at recent changes (`git diff`, `git log -3`) and ask the user what they just solved.

2. **Determine the category.** Pick the best fit:
   - `bugs` — Root cause was non-obvious
   - `architecture` — Design decision with trade-offs
   - `integration` — Connecting systems, APIs, libraries
   - `performance` — Optimization with measurable impact
   - `tooling` — Dev environment, CI/CD, build config
   - `patterns` — Reusable approach discovered

3. **Create the solution file** at `docs/solutions/[category]/[slug].md`:

   ```markdown
   ---
   title: [Clear, searchable title]
   category: [category]
   date: [YYYY-MM-DD]
   tags: [relevant tech, libraries, concepts]
   ---

   ## Problem
   [What went wrong or what needed to be decided. Include error messages if applicable.]

   ## Root Cause
   [Why this happened — the underlying reason, not just symptoms.]

   ## Solution
   [What was done to fix it. Include code snippets or file references.]

   ## Prevention
   [How to avoid this in the future — tests, linting rules, conventions.]
   ```

4. **Keep it concise.** Each solution should be scannable in under 30 seconds. No essays — just the facts someone needs to solve this problem next time.

5. After saving, tell the user: "Solution documented at `docs/solutions/[category]/[slug].md`. This will be searchable in future sessions."

## Rules

- Create `docs/solutions/` and the category subdirectory if they don't exist.
- Slugs should be kebab-case, max 50 characters.
- Don't document trivial fixes (typos, missing imports). Only document problems where the solution wasn't obvious.
- If a similar solution already exists in `docs/solutions/`, update it instead of creating a duplicate.
