---
description: Show which Astra commands to use for your task size and type
argument-hint: "[task description]"
---

> **Arguments**: Any text the user provides after the command name serves as input. In Claude Code, this is substituted into $ARGUMENTS automatically.

# Workflow Guide

Help the user pick the right workflow for their task. Load and present the workflow-guide skill.

## Process

1. **Load the workflow-guide skill** from `skills/workflow-guide/SKILL.md` if not already in context.

2. **If $ARGUMENTS is provided**, analyze the task description and recommend the specific workflow:
   - Assess task size (trivial / small / medium / large / end-to-end / cleanup).
   - Recommend the matching command sequence from the workflow guide.
   - Explain why this workflow fits.

3. **If no arguments**, present the full workflow guide — the "When to Use What" section and the scenario overviews.

4. Answer any follow-up questions about workflows, command ordering, or when to clear context.
