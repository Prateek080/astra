# Astra on Cursor

Astra works on Cursor with the same commands, agents, and skills as Claude Code. This guide covers Cursor-specific installation, usage, and differences.

---

## Installation

### Prerequisites

- [Cursor](https://cursor.com) installed
- `git`, `python3`
- `node` / `npx` (for MCP servers)

### Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/Prateek080/astra/main/install.sh | bash -s -- --cursor
```

This clones Astra, copies the plugin to `~/.cursor/plugins/astra/`, registers it, and enables it. MCP servers (Context7, Playwright, DeepWiki) are configured automatically.

<details>
<summary><b>Manual install</b></summary>

```bash
git clone https://github.com/Prateek080/astra.git ~/astra
bash ~/astra/scripts/install-cursor.sh
```

</details>

3. **Enable third-party plugins in Cursor:**

   Settings → Features → enable **"Include third-party Plugins, Skills, and other configs"**

4. **Restart Cursor** (Cmd+Q and reopen, or Cmd+Shift+P → "Reload Window").

### Verify

Type `/` in chat — you should see all `astra:*` commands (setup, init, spec, plan, implement, review, ship, debug, compound).

---

## Setup

Run the same setup commands as Claude Code:

```
/astra:setup    # One-time global config
/astra:init     # Per-project setup (generates CLAUDE.md + rules for both editors)
```

`/astra:init` generates rules in both `.claude/rules/` and `.cursor/rules/` with the appropriate frontmatter format for each editor.

---

## Usage

All commands work the same way:

```
/astra:spec user auth with Google and GitHub OAuth
/astra:plan
/astra:implement
/astra:review
/astra:ship
```

Provide arguments after the command name — the AI receives them as part of the conversation context.

### Agents

Agents (planner, implementer, reviewer, debugger) are available as subagents. The AI delegates to them automatically when you use `/astra:*` commands (e.g., `/astra:plan` delegates to the planner, `/astra:review` delegates to the reviewer). You don't need to invoke agents directly for normal usage.

If you want to invoke an agent outside the standard workflow, refer to it by name in chat (e.g., "use the reviewer agent to review this file").

### Skills

Skills (workflow-guide, debt-audit, retrospective) are invocable the same way:

- `/astra:workflow-guide`
- `/astra:debt-audit`
- `/astra:retrospective`

---

## What's Different from Claude Code

Most things work identically. Here are the differences:

| Feature | Claude Code | Cursor | Impact |
|---|---|---|---|
| Command arguments | `$ARGUMENTS` auto-substituted into command text | Arguments visible in chat context, not substituted | None — AI sees your input either way |
| Subagent delegation | Explicit `Agent()` tool | AI uses Task tool + agent definitions | Works, may be slightly less deterministic |
| Agent memory | Built-in `memory: user` persists across sessions | No built-in persistence — see [Memory workaround](#agent-memory-on-cursor) below | Agents don't accumulate knowledge automatically; workaround available |
| Skills preloading | `skills:` frontmatter auto-injects | Agent reads skill file on demand (fallback built in) | Same content, one extra file read |
| Skill forking | `context: fork` runs skills in isolated context | Subagents provide equivalent isolation (each runs in its own context window) | Same outcome — context-heavy skills don't pollute your main chat |
| Parallel execution | `isolation: worktree` gives each subagent its own repo copy | Cursor natively supports worktrees for parallel agents — each subagent runs in its own worktree automatically | Same capability — parallel phases run concurrently in both editors |
| Context management | `/clear`, `/compact`, `/statusline` | Start a new chat when context feels heavy | Different mechanism, same outcome |
| Permissions | `/permissions` interactive command | Managed in Cursor Settings UI | Different path, same result |
| Safety | `/sandbox` for file/network isolation | Managed in Cursor Settings UI | Different path, same result |

The only functional difference is agent memory persistence. Everything else works equivalently in both editors.

### Agent Memory on Cursor

Claude Code agents have built-in memory that persists learnings across sessions. Cursor does not have this natively, but you can add it via an MCP-based memory server:

- **[SuperLocalMemory](https://superlocalmemory.com)** — local SQLite-based memory, works across Cursor, Claude Code, and other MCP-compatible tools. Install with `npx superlocalmemory@latest init`.
- **[cursor-mem](https://pypi.org/project/cursor-mem/)** — lightweight Python-based alternative, no API key needed. Install with `pip install cursor-mem`.

*(Recommendations as of March 2026. Verify these tools are actively maintained before installing.)*

Either option gives agents persistent memory so learnings carry across sessions.

**Built-in fallback:** Even without an MCP memory server, Astra agents automatically save and read learnings from `docs/.agent-memory/` in your project (e.g., `docs/.agent-memory/reviewer.md`). This is project-local and file-based — not as seamless as native memory, but ensures learnings persist. Add `docs/.agent-memory/` to your `.gitignore` since these are personal to each developer.

---

## Updating the Plugin

After pulling new changes from the repo:

```bash
cd ~/astra && git pull
bash ~/astra/scripts/install-cursor.sh
```

Then restart Cursor to pick up changes.

---

## Development Mode

If you're developing the plugin itself, use `--dev` to symlink instead of copy:

```bash
bash ~/astra/scripts/install-cursor.sh --dev
```

In dev mode, edits to the repo are reflected in the plugin immediately — just restart Cursor to pick them up. No need to re-run the script after each change.

---

## Troubleshooting

**Commands don't show up after install:**
- Check that "Include third-party Plugins" is enabled in Settings → Features.
- Try a full restart (Cmd+Q) instead of just reloading the window.
- Verify the files exist: `ls ~/.cursor/plugins/astra/commands/`

**Plugin loads but agents aren't available:**
- Verify: `ls ~/.cursor/plugins/astra/agents/`
- Agents are auto-delegated by `/astra:*` commands. You can also refer to them by name in chat (e.g., "use the reviewer agent").

**MCP servers not connecting:**
- Verify `node` and `npx` are installed: `which npx`
- Check `~/.cursor/plugins/astra/.mcp.json` exists.

---

## Everything Else

All commands, skills, workflows, and MCP servers work the same. See the [main README](../README.md) for the full reference.
