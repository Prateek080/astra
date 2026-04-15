#!/usr/bin/env bash
set -euo pipefail

# ─── Astra Installer ────────────────────────────────────────────────
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/Prateek080/astra/main/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/Prateek080/astra/main/install.sh | bash -s -- --cursor
#   curl -fsSL https://raw.githubusercontent.com/Prateek080/astra/main/install.sh | bash -s -- --claude
#   curl -fsSL https://raw.githubusercontent.com/Prateek080/astra/main/install.sh | bash -s -- --uninstall
# ─────────────────────────────────────────────────────────────────────

ASTRA_DIR="${ASTRA_DIR:-$HOME/astra}"
REPO_URL="https://github.com/Prateek080/astra.git"

if [ -t 1 ]; then
  BOLD="\033[1m" DIM="\033[2m" GREEN="\033[32m" YELLOW="\033[33m" RED="\033[31m" CYAN="\033[36m" RESET="\033[0m"
else
  BOLD="" DIM="" GREEN="" YELLOW="" RED="" CYAN="" RESET=""
fi

info()  { echo -e "${BOLD}${CYAN}▸${RESET} $1"; }
ok()    { echo -e "${BOLD}${GREEN}✓${RESET} $1"; }
warn()  { echo -e "${BOLD}${YELLOW}!${RESET} $1"; }
err()   { echo -e "${BOLD}${RED}✗${RESET} $1"; }

# ─── Parse arguments ────────────────────────────────────────────────

FORCE_CLAUDE=false
FORCE_CURSOR=false
UNINSTALL=false
PURGE=false

for arg in "$@"; do
  case "$arg" in
    --claude)    FORCE_CLAUDE=true ;;
    --cursor)    FORCE_CURSOR=true ;;
    --uninstall) UNINSTALL=true ;;
    --purge)     UNINSTALL=true; PURGE=true ;;
    --help|-h)
      echo "Astra Installer"
      echo ""
      echo "Usage:"
      echo "  install.sh               Auto-detect editors and install"
      echo "  install.sh --claude      Install for Claude Code only"
      echo "  install.sh --cursor      Install for Cursor only"
      echo "  install.sh --uninstall   Remove Astra from all editors"
      echo "  install.sh --purge       Uninstall + delete ~/astra entirely"
      echo ""
      echo "Environment:"
      echo "  ASTRA_DIR   Install location (default: ~/astra)"
      exit 0
      ;;
    *) err "Unknown option: $arg"; exit 1 ;;
  esac
done

# ─── Prerequisites ─────────────────────────────────────────────────

command -v git >/dev/null 2>&1 || { err "git is required."; exit 1; }

# ─── Uninstall ──────────────────────────────────────────────────────

if [ "$UNINSTALL" = true ]; then
  echo ""
  echo -e "${BOLD}Uninstalling Astra...${RESET}"
  echo ""

  # Claude Code
  if command -v claude >/dev/null 2>&1; then
    claude plugin uninstall astra@local 2>/dev/null && ok "Claude Code plugin uninstalled" || true
    claude plugin marketplace remove local 2>/dev/null && ok "Marketplace removed" || true
  fi

  # Cursor
  rm -rf "$HOME/.cursor/plugins/astra" 2>/dev/null && ok "Cursor plugin files removed" || true

  # Legacy cleanup
  [ -f "$HOME/.local/bin/claude-astra" ] && rm -f "$HOME/.local/bin/claude-astra"
  for rc in "$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.profile" "$HOME/.zprofile" "$HOME/.bash_profile"; do
    if [ -f "$rc" ] && grep -q 'plugin-dir.*astra' "$rc" 2>/dev/null; then
      sed -i.bak '/plugin-dir.*astra/d; /# Astra plugin/d' "$rc" && rm -f "${rc}.bak"
      ok "Removed legacy alias from $(basename "$rc")"
    fi
  done

  # Clean stale JSON entries (from older installer versions)
  if command -v python3 >/dev/null 2>&1; then
    for jsonfile in "$HOME/.claude/plugins/installed_plugins.json" "$HOME/.claude/settings.json"; do
      [ -f "$jsonfile" ] && python3 -c "
import json, sys
with open(sys.argv[1]) as f: d = json.load(f)
d.get('plugins', {}).pop('astra@local', None)
d.get('enabledPlugins', {}).pop('astra@local', None)
with open(sys.argv[1], 'w') as f: json.dump(d, f, indent=2)
" "$jsonfile" 2>/dev/null
    done
  fi

  # Purge: delete source directory
  if [ "$PURGE" = true ]; then
    rm -rf "$ASTRA_DIR"
    ok "Deleted $ASTRA_DIR"
  else
    echo ""
    warn "Plugin source at $ASTRA_DIR not removed. Use --purge to delete everything."
  fi

  echo ""
  ok "Astra uninstalled."
  exit 0
fi

# ─── Detect editors ─────────────────────────────────────────────────

HAS_CLAUDE=false
HAS_CURSOR=false

if [ "$FORCE_CLAUDE" = true ]; then
  HAS_CLAUDE=true
elif [ "$FORCE_CURSOR" = true ]; then
  HAS_CURSOR=true
else
  { command -v claude >/dev/null 2>&1 || [ -d "$HOME/.claude" ]; } && HAS_CLAUDE=true
  { [ -d "$HOME/.cursor" ] || [ -d "/Applications/Cursor.app" ] || command -v cursor >/dev/null 2>&1; } && HAS_CURSOR=true
fi

if [ "$HAS_CLAUDE" = false ] && [ "$HAS_CURSOR" = false ]; then
  err "No supported editor detected."
  echo "  Install Claude Code: https://claude.ai/code"
  echo "  Install Cursor:      https://cursor.com"
  exit 1
fi

# ─── Header ─────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}  Astra Installer${RESET}"
echo -e "${DIM}  Complete development lifecycle plugin${RESET}"
echo ""

EDITORS=""
[ "$HAS_CLAUDE" = true ] && EDITORS="Claude Code"
[ "$HAS_CURSOR" = true ] && EDITORS="${EDITORS:+$EDITORS + }Cursor"
info "Detected: $EDITORS"
echo ""

# ─── Step 1: Clone / update ────────────────────────────────────────

if [ -d "$ASTRA_DIR/.git" ]; then
  info "Updating Astra..."
  git -C "$ASTRA_DIR" pull --quiet 2>/dev/null || warn "Could not pull latest. Using existing version."
  ok "Astra updated at $ASTRA_DIR"
else
  info "Cloning Astra..."
  git clone --quiet "$REPO_URL" "$ASTRA_DIR"
  ok "Astra cloned to $ASTRA_DIR"
fi

# ─── Step 2: Claude Code (marketplace CLI) ──────────────────────────

if [ "$HAS_CLAUDE" = true ]; then
  info "Configuring Claude Code..."

  if ! command -v claude >/dev/null 2>&1; then
    warn "claude CLI not found. Install Claude Code first: https://claude.ai/code"
  else
    # Register marketplace (idempotent)
    if claude plugin marketplace add "$ASTRA_DIR" 2>/dev/null; then
      ok "Marketplace registered"
    else
      warn "Marketplace registration failed"
    fi

    # Install plugin (idempotent)
    if claude plugin install astra@local 2>/dev/null; then
      ok "Plugin installed for Claude Code"
    else
      # Might already be installed — just enable
      claude plugin enable astra@local 2>/dev/null && ok "Plugin enabled" || \
        warn "Plugin install failed. Try: claude plugin install astra@local"
    fi
  fi
fi

# ─── Step 3: Cursor (file copy) ────────────────────────────────────

if [ "$HAS_CURSOR" = true ]; then
  info "Configuring Cursor..."

  cursor_target="$HOME/.cursor/plugins/astra"
  rm -rf "$cursor_target"
  mkdir -p "$cursor_target"
  for item in .cursor-plugin commands agents skills .mcp.json; do
    [ -e "$ASTRA_DIR/$item" ] && cp -R "$ASTRA_DIR/$item" "$cursor_target/"
  done

  ok "Plugin files copied to $cursor_target"
fi

# ─── Done ───────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}${GREEN}  Astra installed successfully!${RESET}"
echo ""

if [ "$HAS_CLAUDE" = true ]; then
  echo -e "  ${BOLD}Claude Code (CLI + Desktop + IDE):${RESET}"
  echo "    1. Open any project with Claude Code"
  echo "    2. First time? Type: /astra:setup"
  echo "    3. Build anything: /astra:forge \"your feature\""
  echo ""
fi

if [ "$HAS_CURSOR" = true ]; then
  echo -e "  ${BOLD}Cursor:${RESET}"
  echo "    1. Settings > Features > enable 'Include third-party Plugins'"
  echo "    2. Restart Cursor"
  echo "    3. Type / in chat — you should see astra:* commands"
  echo ""
fi

echo -e "  ${DIM}Docs:      https://github.com/Prateek080/astra${RESET}"
echo -e "  ${DIM}Update:    cd ~/astra && git pull && bash install.sh${RESET}"
echo -e "  ${DIM}Uninstall: ~/astra/install.sh --uninstall${RESET}"
echo ""
