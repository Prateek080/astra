"""Per-agent permission profiles."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PermissionProfile:
    """Permission profile for a specific agent role."""

    readonly: bool = True
    allowed_tools: list[str] = field(default_factory=list)
    write_paths: list[str] = field(default_factory=list)
    deny_paths: list[str] = field(default_factory=list)
    permission_mode: str = "default"


AGENT_PROFILES: dict[str, PermissionProfile] = {
    "pm": PermissionProfile(
        readonly=True,
        allowed_tools=["Read", "Grep", "Glob", "Bash"],
        permission_mode="default",
    ),
    "designer": PermissionProfile(
        readonly=True,
        allowed_tools=["Read", "Grep", "Glob", "Bash"],
        permission_mode="default",
    ),
    "architect": PermissionProfile(
        readonly=True,
        allowed_tools=["Read", "Grep", "Glob", "Bash"],
        permission_mode="default",
    ),
    "planner": PermissionProfile(
        readonly=True,
        allowed_tools=["Read", "Grep", "Glob", "Bash"],
        permission_mode="default",
    ),
    "reviewer": PermissionProfile(
        readonly=True,
        allowed_tools=["Read", "Grep", "Glob", "Bash"],
        permission_mode="default",
    ),
    "implementer": PermissionProfile(
        readonly=False,
        allowed_tools=["Read", "Write", "Edit", "Bash", "Grep", "Glob"],
        write_paths=["src/", "app/", "lib/", "tests/", "test/", "pages/"],
        deny_paths=[".env", ".git/", "node_modules/", "package-lock.json"],
        permission_mode="acceptEdits",
    ),
    "debugger": PermissionProfile(
        readonly=False,
        allowed_tools=["Read", "Write", "Edit", "Bash", "Grep", "Glob"],
        write_paths=["src/", "app/", "lib/", "tests/", "test/"],
        deny_paths=[".env", ".git/", "node_modules/"],
        permission_mode="acceptEdits",
    ),
}


def get_profile(agent_name: str) -> PermissionProfile:
    """Get permission profile for an agent, with safe default."""
    return AGENT_PROFILES.get(agent_name, PermissionProfile())
