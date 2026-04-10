---
description: Assess how the last feature went and suggest workflow improvements
argument-hint: "[feature name or git ref range]"
---

> **Arguments**: Any text the user provides after the command name serves as input. In Claude Code, this is substituted into $ARGUMENTS automatically.

# Retrospective

Review the recent development work and identify improvements. Delegates to a subagent to keep main context clean.

## Process

1. **Determine scope:**
   - If $ARGUMENTS names a feature, look for its archived spec in `docs/specs/` and plan in `docs/plans/`.
   - If $ARGUMENTS is a git ref range (e.g., `main..HEAD`), scope to those commits.
   - Otherwise, read SPEC.md, DESIGN.md, PLAN.md (if they exist), PRODUCT.md, and recent git history.

2. **Delegate the retrospective:**

   "Use a general-purpose subagent to run a retrospective on [scope]. The subagent should follow the retrospective skill methodology: compare spec and plan to what was actually built, assess quality (bugs found post-implementation, test adequacy, reverts), evaluate the process (was the spec detailed enough, was the plan well-structured), and check for reusability (new patterns worth documenting). Output as: What Went Well, What Didn't Go Well, and Suggested Improvements with copy-pasteable markdown for each target file."

3. **Present findings** to the user with actionable improvement suggestions.

4. After the retrospective, tell the user: "To apply these improvements, copy the suggested additions into the relevant files (review-checklist, plan-template, CLAUDE.md, rules). Or ask me to apply specific suggestions."
