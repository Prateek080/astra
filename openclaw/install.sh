#!/usr/bin/env bash
# Astra for OpenClaw — Installer
# Copies skills, scripts, agents, and orchestration files to the OpenClaw workspace.
#
# Usage:
#   bash openclaw/install.sh                    # Install to default workspace
#   bash openclaw/install.sh --workspace ~/my-workspace  # Custom workspace path
#   bash openclaw/install.sh --uninstall        # Remove Astra from workspace

set -euo pipefail

ASTRA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OPENCLAW_WORKSPACE="${HOME}/.openclaw/workspace"
ASTRA_DEST="astra"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
DIM='\033[2m'
NC='\033[0m'

info()  { echo -e "${GREEN}✓${NC} $*"; }
warn()  { echo -e "${YELLOW}⚠${NC} $*"; }
error() { echo -e "${RED}✗${NC} $*"; }
dim()   { echo -e "${DIM}  $*${NC}"; }

# ── Parse arguments ──────────────────────────────────────────
UNINSTALL=false
WORKSPACE_OVERRIDE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --workspace)
            WORKSPACE_OVERRIDE="$2"
            shift 2
            ;;
        --uninstall)
            UNINSTALL=true
            shift
            ;;
        -h|--help)
            echo "Astra for OpenClaw — Installer"
            echo ""
            echo "Usage:"
            echo "  bash openclaw/install.sh                         Install to default workspace"
            echo "  bash openclaw/install.sh --workspace ~/my-ws     Custom workspace path"
            echo "  bash openclaw/install.sh --uninstall             Remove from workspace"
            echo ""
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [[ -n "$WORKSPACE_OVERRIDE" ]]; then
    OPENCLAW_WORKSPACE="$WORKSPACE_OVERRIDE"
fi

DEST="${OPENCLAW_WORKSPACE}/${ASTRA_DEST}"

# ── Uninstall ────────────────────────────────────────────────
if $UNINSTALL; then
    echo "Removing Astra from OpenClaw workspace..."

    if [[ -d "$DEST" ]]; then
        rm -rf "$DEST"
        info "Removed ${DEST}"
    else
        warn "Astra not found at ${DEST}"
    fi

    # Remove skills
    SKILLS_DEST="${OPENCLAW_WORKSPACE}/skills/astra"
    if [[ -d "$SKILLS_DEST" ]]; then
        rm -rf "$SKILLS_DEST"
        info "Removed skills from ${SKILLS_DEST}"
    fi

    echo ""
    info "Astra uninstalled from OpenClaw."
    exit 0
fi

# ── Pre-flight checks ────────────────────────────────────────
echo "Astra for OpenClaw — Installer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check OpenClaw
if command -v openclaw &>/dev/null; then
    info "OpenClaw CLI found"
else
    warn "OpenClaw CLI not found in PATH"
    dim "Install OpenClaw first, then re-run this installer."
    dim "Continuing anyway (files will be copied for when OpenClaw is available)..."
    echo ""
fi

# Check Python
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
    info "Python ${PYTHON_VERSION} found"
else
    error "Python 3.10+ required"
    exit 1
fi

# Check git
if command -v git &>/dev/null; then
    info "Git found"
else
    error "Git required"
    exit 1
fi

# Optional tools
if command -v gh &>/dev/null; then
    info "GitHub CLI found"
else
    dim "GitHub CLI (gh) not found — PR creation will be manual"
fi

if command -v aider &>/dev/null; then
    info "Aider found"
else
    dim "Aider not found — coder agent will use direct exec for code changes"
fi

echo ""

# ── Install Python dependencies ──────────────────────────────
echo "Installing Python dependencies..."
pip install graphifyy pydantic rich pyyaml --quiet 2>/dev/null || {
    warn "Some Python dependencies failed to install"
    dim "Try: pip install graphifyy pydantic rich pyyaml"
}
info "Python dependencies installed"
echo ""

# ── Create destination directories ───────────────────────────
echo "Copying Astra files to ${DEST}..."
mkdir -p "$DEST"
mkdir -p "${DEST}/scripts"
mkdir -p "${DEST}/templates"
mkdir -p "${OPENCLAW_WORKSPACE}/skills/astra"

# ── Copy OpenClaw-specific files ─────────────────────────────

# Plugin manifest
cp "${ASTRA_DIR}/openclaw/plugin.json" "${DEST}/plugin.json"
info "Plugin manifest"

# Agent definitions
cp "${ASTRA_DIR}/openclaw/AGENTS.md" "${DEST}/AGENTS.md"
info "Agent definitions (7 agents)"

# Orchestration
cp "${ASTRA_DIR}/openclaw/HEARTBEAT.md" "${DEST}/HEARTBEAT.md"
info "HEARTBEAT orchestration"

# Dexter personality
cp "${ASTRA_DIR}/openclaw/SOUL.md" "${DEST}/SOUL.md"
info "Dexter (SOUL.md)"

# Bootstrap
cp "${ASTRA_DIR}/openclaw/BOOTSTRAP.md" "${DEST}/BOOTSTRAP.md"
info "Bootstrap setup"

# Templates
cp "${ASTRA_DIR}/openclaw/templates/"*.md "${DEST}/templates/" 2>/dev/null
info "Artifact templates (4 files)"

# Mediator scripts
cp "${ASTRA_DIR}/openclaw/scripts/"*.py "${DEST}/scripts/" 2>/dev/null
info "Mediator scripts (12 files)"

# ── Copy shared code ─────────────────────────────────────────

# Stage-gate checks (reused from orchestrator/)
if [[ -d "${ASTRA_DIR}/orchestrator/checks" ]]; then
    mkdir -p "${DEST}/orchestrator/checks"
    cp "${ASTRA_DIR}/orchestrator/checks/"*.py "${DEST}/orchestrator/checks/" 2>/dev/null
    info "Stage-gate checks (S1-S5, D1-D5, P1-P4, T1-T5, I1-I4)"

    # Also copy __init__.py for the orchestrator package
    cp "${ASTRA_DIR}/orchestrator/__init__.py" "${DEST}/orchestrator/" 2>/dev/null || true
fi

# Skills (shared with Claude Code / Cursor)
SKILL_COUNT=0
for skill_dir in "${ASTRA_DIR}/skills/"*/; do
    if [[ -f "${skill_dir}SKILL.md" ]]; then
        skill_name=$(basename "$skill_dir")
        mkdir -p "${OPENCLAW_WORKSPACE}/skills/astra/${skill_name}"
        cp "${skill_dir}SKILL.md" "${OPENCLAW_WORKSPACE}/skills/astra/${skill_name}/SKILL.md"
        SKILL_COUNT=$((SKILL_COUNT + 1))
    fi
done
info "Skills (${SKILL_COUNT} skills)"

# Rules
if [[ -d "${ASTRA_DIR}/rules" ]]; then
    mkdir -p "${DEST}/rules"
    cp "${ASTRA_DIR}/rules/"*.md "${DEST}/rules/" 2>/dev/null
    info "Path-scoped rules"
fi

echo ""

# ── Configuration prompts ────────────────────────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Optional configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Reporting
echo "Notification channel for pipeline events?"
echo "  1) Telegram"
echo "  2) Discord"
echo "  3) None (default)"
read -r -p "Choice [3]: " REPORT_CHOICE
REPORT_CHOICE=${REPORT_CHOICE:-3}

case "$REPORT_CHOICE" in
    1)
        read -r -p "Telegram Bot Token: " TG_TOKEN
        read -r -p "Telegram Chat ID: " TG_CHAT
        if [[ -n "$TG_TOKEN" && -n "$TG_CHAT" ]]; then
            printf 'export TELEGRAM_BOT_TOKEN=%q\n' "${TG_TOKEN}" >> "${DEST}/.env"
            printf 'export TELEGRAM_CHAT_ID=%q\n' "${TG_CHAT}" >> "${DEST}/.env"
            chmod 600 "${DEST}/.env"
            info "Telegram configured (secrets in ${DEST}/.env — chmod 600)"
        fi
        ;;
    2)
        read -r -p "Discord Webhook URL: " DC_URL
        if [[ -n "$DC_URL" ]]; then
            printf 'export DISCORD_WEBHOOK_URL=%q\n' "${DC_URL}" >> "${DEST}/.env"
            chmod 600 "${DEST}/.env"
            info "Discord configured (secrets in ${DEST}/.env — chmod 600)"
        fi
        ;;
    *)
        dim "No reporting configured"
        ;;
esac

echo ""

# ── Summary ──────────────────────────────────────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
info "Astra installed to: ${DEST}"
echo ""
echo "  Workspace:  ${OPENCLAW_WORKSPACE}"
echo "  Skills:     ${OPENCLAW_WORKSPACE}/skills/astra/ (${SKILL_COUNT} skills)"
echo "  Plugin:     ${DEST}/plugin.json"
echo "  Agents:     ${DEST}/AGENTS.md (7 agents)"
echo "  Scripts:    ${DEST}/scripts/ (12 mediator scripts)"
echo "  Checks:     ${DEST}/orchestrator/checks/ (24 stage-gate checks)"
echo ""
echo "  Next steps:"
echo "    1. Configure model preferences in ${DEST}/plugin.json"
echo "    2. In your project: run BOOTSTRAP.md to initialize workspace"
echo "    3. Start building: send 'build: <feature>' to Dexter"
echo ""
echo "  Update Astra:"
echo "    cd ~/astra && git pull && bash openclaw/install.sh"
echo ""
