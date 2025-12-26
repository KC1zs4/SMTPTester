from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List

from .models import SessionEvent, SessionLog
from .utils import simple_yaml_dump


class SessionLogger:
    def __init__(self, base_dir: Path, batch: str, run_ts: str | None = None):
        self.base_dir = base_dir
        self.batch = batch
        self.run_ts = run_ts or datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.run_dir = self.base_dir / f"{self.batch}_{self.run_ts}"
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_by_domain: Dict[str, List[SessionLog]] = {}

    def log_session(self, session: SessionLog) -> Path:
        safe_domain = session.target_domain.replace(" ", "_")
        sessions = self.sessions_by_domain.setdefault(safe_domain, [])
        sessions.append(session)
        filename = self.run_dir / f"{safe_domain}.yaml"
        payload = self._serialize_domain(sessions)
        filename.write_text(payload, encoding="utf-8")
        return filename

    def _serialize_domain(self, sessions: List[SessionLog]) -> str:
        data = [self._serialize(session) for session in sessions]
        return simple_yaml_dump(data)

    def _serialize(self, session: SessionLog) -> dict:
        return {
            "batch": session.batch,
            "task": session.task,
            "target_domain": session.target_domain,
            "mx_hostname": session.mx_hostname,
            "mx_preference": session.mx_preference,
            "mx_ip": session.mx_ip,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat(),
            "status": session.status,
            "error": session.error or "",
            "events": self._serialize_events(session.events),
        }

    @staticmethod
    def _serialize_events(events: List[SessionEvent]) -> list[dict]:
        serialized = []
        for event in events:
            raw_text = event.payload.decode("latin1", errors="surrogateescape")
            # Keep visible CRLF markers while emitting YAML multiline blocks.
            escaped_lines = [
                line.replace("\r", "\\r").replace("\n", "\\n")
                for line in raw_text.splitlines(keepends=True)
            ]
            serialized.append(
                {
                    "direction": event.direction,
                    "bytes_raw": "\n".join(escaped_lines),
                }
            )
        return serialized
