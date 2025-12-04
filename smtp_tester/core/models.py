from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class CommandSpec:
    data: bytes
    expect_response: bool = True
    pause_after: float = 0.0


@dataclass
class TaskDefinition:
    name: str
    commands: List[CommandSpec]
    description: str | None = None
    values: dict | None = None


@dataclass
class MXRecord:
    hostname: str
    preference: int
    ip: str
    domain: str


@dataclass
class SessionEvent:
    direction: str  # "send" or "recv"
    timestamp: datetime
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
