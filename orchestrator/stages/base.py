"""Base stage class — defines the SDK integration pattern for all pipeline stages."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rich.console import Console

from orchestrator.config import AgentMeta, AstraConfig
from orchestrator.state import PipelineState

console = Console()


@dataclass
class StageResult:
    """Result of a single stage execution."""

    success: bool
    artifact_path: str | None = None
    session_id: str | None = None
    output: str = ""
    error: str | None = None


class Stage(ABC):
    """Base class for all pipeline stages.

    Each stage:
    1. Builds a prompt from pipeline state
    2. Configures agent options (tools, permissions, plugin loading)
    3. Calls query() with the prompt
    4. Captures the output and writes the artifact
    """

    name: str = ""
    agent_name: str = ""  # Key in config.agents
    readonly: bool = True
    artifact_filename: str | None = None  # e.g., "SPEC.md"

    @abstractmethod
    def build_prompt(self, state: PipelineState, config: AstraConfig) -> str:
        """Construct the prompt for the agent."""
        ...

    def get_agent_meta(self, config: AstraConfig) -> AgentMeta | None:
        """Get the agent metadata from config."""
        return config.agents.get(self.agent_name)

    def get_allowed_tools(self) -> list[str]:
        """Tools this stage's agent is allowed to use."""
        if self.readonly:
            return ["Read", "Grep", "Glob", "Bash", "Agent"]
        return ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "Agent"]

    def get_permission_mode(self) -> str:
        """Permission mode for this stage."""
        return "acceptEdits" if not self.readonly else "default"

    def build_agent_options(self, config: AstraConfig) -> dict[str, Any]:
        """Build ClaudeAgentOptions kwargs for query().

        Returns a dict that can be unpacked into ClaudeAgentOptions.
        We return a dict because the actual SDK import happens at call time.
        """
        from orchestrator.hooks import build_hooks_config

        opts: dict[str, Any] = {
            "allowed_tools": self.get_allowed_tools(),
            "permission_mode": self.get_permission_mode(),
            "cwd": str(config.project_dir),
            "hooks": build_hooks_config(readonly=self.readonly),
        }

        # Load Astra plugin for skills and agents
        plugin_path = str(config.astra_plugin_dir)
        if os.path.isdir(plugin_path):
            opts["plugins"] = [{"type": "local", "path": plugin_path}]

        return opts

    async def run(self, state: PipelineState, config: AstraConfig) -> StageResult:
        """Execute this stage via the Agent SDK."""
        from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

        agent_meta = self.get_agent_meta(config)
        if not agent_meta:
            return StageResult(
                success=False,
                error=f"Agent '{self.agent_name}' not found in plugin directory",
            )

        prompt = self.build_prompt(state, config)
        agent_opts = self.build_agent_options(config)

        # Build system prompt from agent body
        system_prompt = agent_meta.body
        if system_prompt:
            agent_opts["system_prompt"] = system_prompt

        console.print(f"  [bold]{self.name}[/] — running {self.agent_name} agent...")

        session_id = None
        output = ""

        try:
            options = ClaudeAgentOptions(**agent_opts)
            async for message in query(prompt=prompt, options=options):
                if isinstance(message, ResultMessage):
                    session_id = getattr(message, "session_id", None)
                    if hasattr(message, "result") and message.result:
                        output = message.result
                    if hasattr(message, "subtype") and message.subtype and message.subtype.startswith("error"):
                        return StageResult(
                            success=False,
                            session_id=session_id,
                            error=f"Agent returned error: {message.subtype}",
                        )
        except Exception as e:
            return StageResult(success=False, error=str(e))

        # Write artifact if configured
        artifact_path = None
        if self.artifact_filename and output:
            artifact_full_path = config.project_dir / self.artifact_filename
            artifact_full_path.write_text(output, encoding="utf-8")
            artifact_path = self.artifact_filename

        return StageResult(
            success=True,
            artifact_path=artifact_path,
            session_id=session_id,
            output=output,
        )

    def _read_file_if_exists(self, config: AstraConfig, filename: str) -> str:
        """Read a project file if it exists, return empty string otherwise."""
        path = config.project_dir / filename
        if path.is_file():
            return path.read_text(encoding="utf-8")
        return ""

    def _read_context_cache(self, config: AstraConfig) -> str:
        """Read .astra-cache/context.md if it exists."""
        if config.context_cache_path.is_file():
            return config.context_cache_path.read_text(encoding="utf-8")
        return ""

    def _get_memory_section(self, config: AstraConfig) -> str:
        """Get agent memory for inclusion in prompts."""
        # Check for memory injected by pipeline (parallel-safe)
        if hasattr(self, "_memory_context") and self._memory_context:
            return self._memory_context

        from orchestrator.memory import get_memory_prompt_section
        return get_memory_prompt_section(config.project_dir, self.agent_name)
