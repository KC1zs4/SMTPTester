from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class CommandSpec:
    data: bytes
    pause_after: float = 0.0


@dataclass
class CommandTemplate:
    raw: Any
    pause_after: float = 0.0


@dataclass
class TaskDefinition:
    name: str
    commands: List[CommandTemplate]
    description: str | None = None
    values: dict | None = None
    target_values: Dict[str, dict] | None = None

    def render_commands(self, domain: str | None = None) -> List[CommandSpec]:
        merged_values: Dict[str, Any] = {}
        if self.values:
            merged_values.update(self.values)
        if domain and self.target_values and domain in self.target_values:
            domain_values = self.target_values[domain]
            if isinstance(domain_values, dict):
                merged_values.update(domain_values)
            else:
                raise ValueError(f"Task {self.name} target_values for {domain} must be a dict")
        return [
            CommandSpec(
                data=self._render_bytes(cmd.raw, merged_values),
                pause_after=cmd.pause_after,
            )
            for cmd in self.commands
        ]

    @staticmethod
    def _render_bytes(raw: Any, values: dict) -> bytes:
        if isinstance(raw, bytes):
            text = raw.decode("latin1")
        elif isinstance(raw, str):
            text = raw
        else:
            raise ValueError("Command data must be str or bytes or dict with data")
        formatted_values = {
            key: val.decode("latin1") if isinstance(val, (bytes, bytearray)) else val
            for key, val in values.items()
        } if values else {}
        formatted = text.format(**formatted_values) if formatted_values else text
        return formatted.encode("latin1")


@dataclass
class MXRecord:
    hostname: str
    preference: int
    ip: str
    domain: str


@dataclass
class SessionEvent:
    direction: str  # "send" or "recv"
    payload: bytes


@dataclass
class SessionLog:
    batch: str
    task: str
    target_domain: str
    mx_hostname: str
    mx_preference: int
    mx_ip: str
    start_time: datetime
    end_time: datetime
    status: str
    error: Optional[str] = None
    events: List[SessionEvent] = field(default_factory=list)
