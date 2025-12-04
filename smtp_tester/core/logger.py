from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List

from .models import SessionEvent, SessionLog
from .utils import simple_yaml_dump


class SessionLogger:
    def __init__(self, base_dir: Path, batch: str):
        self.base_dir = base_dir
        self.batch = batch
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def log_session(self, session: SessionLog) -> Path:
        filename = self._build_filename(session)
        payload = self._serialize(session)
        filename.parent.mkdir(parents=True, exist_ok=True)
        filename.write_text(payload, encoding="utf-8")
        return filename

    def _build_filename(self, session: SessionLog) -> Path:
        safe_task = session.task.replace(" ", "_")
        safe_domain = session.target_domain.replace(" ", "_")
        ts = session.start_time.strftime("%Y%m%dT%H%M%S")
        return self.base_dir / self.batch / f"{safe_domain}_{session.mx_ip}_{safe_task}_{ts}.yaml"

    def _serialize(self, session: SessionLog) -> str:
        data = {
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
        return simple_yaml_dump(data)

    @staticmethod
    def _serialize_events(events: List[SessionEvent]) -> list[dict]:
        serialized = []
        for event in events:
            serialized.append(
                {
                    "direction": event.direction,
                    "timestamp": event.timestamp.isoformat(),
                    "bytes": event.payload.decode("latin1", errors="surrogateescape"),
                }
            )
        return serialized
