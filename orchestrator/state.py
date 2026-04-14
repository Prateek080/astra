"""Pipeline state management for checkpoint/resume support."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class StageStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    FAILED = "failed"
    SKIPPED = "skipped"


class StageRecord(BaseModel):
    """Record of a single pipeline stage execution."""

    name: str
    status: StageStatus = StageStatus.PENDING
    session_id: str | None = None
    artifact_path: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    retry_count: int = 0
    gate_result: dict[str, Any] | None = None
    error: str | None = None


class PipelineState(BaseModel):
    """Full pipeline state — serialized to .astra-cache/pipeline-state.json."""

    pipeline_id: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"))
    feature: str
    mode: str = "full"  # "full" or "lite"
    current_stage: str = "init"
    stages: dict[str, StageRecord] = Field(default_factory=dict)
    started_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str | None = None
    requirement_ids: list[str] = Field(default_factory=list)

    def init_stages(self, mode: str) -> None:
        """Initialize stage records based on mode. Preserves existing completed stages."""
        self.mode = mode
        stage_names = ["scan", "spec"]
        if mode == "full":
            stage_names += ["design", "plan", "architect", "implement", "review", "wrapup"]
        else:
            stage_names += ["plan", "implement", "review", "wrapup"]

        for name in stage_names:
            if name not in self.stages:
                self.stages[name] = StageRecord(name=name)
            # Don't overwrite completed/in-progress stages on resume

        # Remove stages not in this mode (e.g., design/architect in lite mode)
        valid_names = set(stage_names)
        for name in list(self.stages.keys()):
            if name not in valid_names:
                record = self.stages[name]
                if record.status == StageStatus.PENDING:
                    record.status = StageStatus.SKIPPED

    def stage_complete(self, name: str) -> bool:
        record = self.stages.get(name)
        return record is not None and record.status in (StageStatus.COMPLETE, StageStatus.SKIPPED)

    def advance_to(self, stage_name: str) -> None:
        self.current_stage = stage_name
        record = self.stages.get(stage_name)
        if record:
            record.status = StageStatus.IN_PROGRESS
            record.started_at = datetime.now(timezone.utc).isoformat()

    def mark_complete(self, stage_name: str, artifact_path: str | None = None, session_id: str | None = None) -> None:
        record = self.stages.get(stage_name)
        if record:
            record.status = StageStatus.COMPLETE
            record.completed_at = datetime.now(timezone.utc).isoformat()
            record.artifact_path = artifact_path
            record.session_id = session_id

    def mark_failed(self, stage_name: str, error: str) -> None:
        record = self.stages.get(stage_name)
        if record:
            record.status = StageStatus.FAILED
            record.error = error
            record.completed_at = datetime.now(timezone.utc).isoformat()

    def mark_skipped(self, stage_name: str) -> None:
        record = self.stages.get(stage_name)
        if record:
            record.status = StageStatus.SKIPPED

    def record_gate(self, stage_name: str, result: dict[str, Any]) -> None:
        record = self.stages.get(stage_name)
        if record:
            record.gate_result = result

    def increment_retry(self, stage_name: str) -> int:
        record = self.stages.get(stage_name)
        if record:
            record.retry_count += 1
            return record.retry_count
        return 0

    def is_resumable(self) -> bool:
        """Can this pipeline be resumed from its current state?"""
        return any(
            r.status in (StageStatus.PENDING, StageStatus.IN_PROGRESS, StageStatus.FAILED)
            for r in self.stages.values()
        )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.model_dump_json(indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> PipelineState | None:
        if not path.is_file():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return cls.model_validate(data)
        except (json.JSONDecodeError, Exception):
            return None

    @classmethod
    def load_or_create(cls, path: Path, feature: str, mode: str = "full") -> PipelineState:
        existing = cls.load(path)
        if existing and existing.is_resumable():
            return existing
        state = cls(feature=feature)
        state.init_stages(mode)
        state.save(path)
        return state
