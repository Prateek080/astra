# Astra on Cursor

Astra works on Cursor with the same commands, agents, and skills as Claude Code. This guide covers Cursor-specific setup and differences.

---

## Installation

```bash
git clone git@github.com:Prateek080/astra.git ~/astra
```

Then load it when starting Cursor:

```bash
cursor --plugin-dir ~/astra
```

**Verify:** Run `/help` inside Cursor — you should see all `/astra:*` commands.

---

## Setup

Run the same setup commands as Claude Code:

```
/astra:setup    # One-time global config
/astra:init     # Per-project setup
```

Both editors share `~/.claude/` for configuration (`settings.json`, `CLAUDE.md`). Setting up in one editor works for both.

---

## What's Different in Cursor

Most things work identically. Here are the few differences:

### Coordinator mode

Instead of the CLI flag, select the coordinator from Cursor's agent picker:

| Claude Code | Cursor |
|---|---|
| `claude --agent astra:coordinator` | Select `astra:coordinator` from the agent picker |

### Commands that are Claude Code-specific

These interactive commands from `/astra:setup` are Claude Code-specific. Cursor handles these differently through its own settings UI:

| Command | Claude Code | Cursor equivalent |
|---|---|---|
| `/permissions` | Pre-approves tool use | Managed in Cursor settings |
| `/sandbox` | File/network isolation | Managed in Cursor settings |
| `/statusline` | Context % in terminal | Cursor shows context usage in its UI |

### Agent behavior

Agents use dual frontmatter that both editors understand:

- `tools:`, `color:`, `memory:` — used by Claude Code, ignored by Cursor
- `readonly:` — used by Cursor, ignored by Claude Code

Read-only agents (planner, reviewer) have `readonly: true`. Write-capable agents (implementer, debugger, coordinator) have `readonly: false`.

---

## Everything Else

All commands, skills, MCP servers, hooks, and workflows work the same. See the [main README](../README.md) for the full reference.
