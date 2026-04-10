---
description: Scan codebase for technical debt — dead code, TODOs, deprecated patterns, missing tests
argument-hint: "[directory or file path to scope the audit]"
---

> **Arguments**: Any text the user provides after the command name serves as input. In Claude Code, this is substituted into $ARGUMENTS automatically.

# Tech Debt Audit

Run a comprehensive tech debt scan. This command delegates to a subagent to keep main context clean.

## Process

1. **Determine scope:**
   - If $ARGUMENTS is a file or directory path, scope the audit to that path.
   - Otherwise, audit the entire project.

2. **Delegate the audit:**

   "Use a general-purpose subagent to perform a tech debt audit on [scope]. The subagent should follow the debt-audit skill methodology: check for dead code, TODOs without linked issues, deprecated patterns, hardcoded values, missing tests, dependency health, and code duplication. Output findings organized by severity (Critical / Important / Minor) with file paths and line numbers."

3. **Present findings** to the user organized by severity, with a summary table at the top.

4. After the audit, tell the user: "Audit complete. To address these findings, run `/astra:plan` with the specific items you want to fix, then `/astra:implement`."
