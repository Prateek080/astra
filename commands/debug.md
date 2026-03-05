---
description: Structured debugging from error to root cause to verified fix
argument-hint: "[error message or description]"
---

# Debug Phase

You MUST delegate debugging to the debugger subagent. Debugging reads many files and produces verbose output — keep it out of the main conversation.

## Process

1. Gather the error context:
   - If $ARGUMENTS contains an error message, use it.
   - Otherwise, ask the user to describe the issue or paste the error.

2. Delegate to the debugger subagent:
   "Use the debugger subagent to investigate: [error context]. It should find the root cause, implement a minimal fix, and verify the fix works."

3. Present the debugger's findings:
   - **Root cause**: Why the bug exists (not just what's broken)
   - **Evidence**: Stack trace, relevant code, reproduction steps
   - **Fix**: What was changed and why
   - **Verification**: How the fix was verified (test, manual check)
   - **Prevention**: How to prevent similar bugs

4. After the fix is verified, tell the user: "Bug fixed and verified. Run `/astra:review` to review the fix, then `/astra:ship` to commit."
