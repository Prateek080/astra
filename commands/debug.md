---
description: Structured debugging from error to root cause to verified fix
argument-hint: "[error message or description]"
---

> **Arguments**: Any text the user provides after the command name serves as input. In Claude Code, this is substituted into $ARGUMENTS automatically.

# Debug Phase

Prefer delegating debugging to the debugger subagent — debugging reads many files and produces verbose output. If subagent delegation is not available, debug directly but summarize findings frequently to manage context.

## Process

1. Gather the error context:
   - If $ARGUMENTS contains an error message, use it.
   - Otherwise, ask the user (use AskUserQuestion if available, otherwise ask directly in chat) to describe the issue or paste the error.

2. Delegate to the debugger subagent:
   "Use the debugger subagent to investigate: [error context]. It should find the root cause, implement a minimal fix, and verify the fix works."

3. Present the debugger's findings:
   - **Root cause**: Why the bug exists (not just what's broken)
   - **Evidence**: Stack trace, relevant code, reproduction steps
   - **Fix**: What was changed and why
   - **Verification**: How the fix was verified (test, manual check)
   - **Prevention**: How to prevent similar bugs

4. After the fix is verified, tell the user: "Bug fixed and verified. Run `/astra:review` to review the fix, then `/astra:ship` to commit. If the root cause was non-obvious, consider running `/astra:compound` to document this solution for future reference."
