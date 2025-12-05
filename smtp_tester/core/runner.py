from __future__ import annotations

import socket
import time
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

from .logger import SessionLogger
from .models import MXRecord, SessionEvent, SessionLog, TaskDefinition
from .smtp_client import SMTPClient


class BatchRunner:
    def __init__(
        self,
        batch_path: Path,
        config: dict,
        tasks: List[TaskDefinition],
        mx_records: List[MXRecord],
    ):
        self.batch_path = batch_path
        self.config = config
        self.tasks = tasks
        self.mx_records = sorted(mx_records, key=lambda r: (r.domain, r.preference, r.hostname, r.ip))
        log_dir = Path(config.get("log_dir", "logs"))
        self.run_ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        self.logger = SessionLogger(log_dir, batch_path.name, run_ts=self.run_ts)

    def run(self, selected_tasks: Optional[Iterable[str]] = None) -> None:
        names = set(selected_tasks) if selected_tasks else None
        for record in self.mx_records:
            for task in self.tasks:
                if names and task.name not in names:
                    continue
                if task.target_values and record.domain not in task.target_values:
                    continue
                self._run_single(record, task)
            delay_hosts = float(self.config.get("delay_between_hosts", 0))
            if delay_hosts > 0:
                time.sleep(delay_hosts)

    def _run_single(self, record: MXRecord, task: TaskDefinition) -> None:
        start = datetime.utcnow()
        events: List[SessionEvent] = []
        status = "success"
        error: Optional[str] = None
        client = SMTPClient(
            host_ip=record.ip,
            port=int(self.config.get("port", 25)),
            connect_timeout=float(self.config.get("connect_timeout", 8.0)),
            command_timeout=float(self.config.get("command_timeout", 8.0)),
            banner_timeout=float(self.config.get("banner_timeout", 8.0)),
            read_chunk=int(self.config.get("read_chunk", 4096)),
            delay_before_first_command=float(self.config.get("delay_before_first_command", 0.0)),
            delay_between_commands=float(self.config.get("delay_between_commands", 0.0)),
        )
        print(f"[*] {record.domain} -> {record.ip} task={task.name}")
        try:
            client.connect()
            commands = task.render_commands(record.domain)
            client.run_sequence(commands, events=events)
        except (socket.timeout, ConnectionError, OSError) as exc:
            status = "error"
            error = str(exc)
        except Exception as exc:  # noqa: BLE001
            status = "error"
            error = f"Unexpected: {exc}"
        finally:
            client.close()
        end = datetime.utcnow()
        session = SessionLog(
            batch=self.batch_path.name,
            task=task.name,
            target_domain=record.domain,
            mx_hostname=record.hostname,
            mx_preference=record.preference,
            mx_ip=record.ip,
            start_time=start,
            end_time=end,
            status=status,
            error=error,
            events=events,
        )
        path = self.logger.log_session(session)
        if status == "success":
            print(f"[+] logged {path}")
        else:
            print(f"[!] failure logged {path} ({error})")
