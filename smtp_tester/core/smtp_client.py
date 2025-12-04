from __future__ import annotations

import socket
import time
from datetime import datetime
from typing import List, Optional

from .models import CommandSpec, SessionEvent


class SMTPClient:
    def __init__(
        self,
        host_ip: str,
        port: int = 25,
        connect_timeout: float = 8.0,
        command_timeout: float = 8.0,
        banner_timeout: float = 8.0,
        read_chunk: int = 4096,
        delay_between_commands: float = 0.0,
    ):
        self.host_ip = host_ip
        self.port = port
        self.connect_timeout = connect_timeout
        self.command_timeout = command_timeout
        self.banner_timeout = banner_timeout
        self.read_chunk = read_chunk
        self.delay_between_commands = delay_between_commands
        self.sock: Optional[socket.socket] = None

    def connect(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.connect_timeout)
        self.sock.connect((self.host_ip, self.port))
        self.sock.settimeout(self.banner_timeout)

    def close(self) -> None:
        if self.sock:
            try:
                self.sock.close()
            finally:
                self.sock = None

    def run_sequence(self, commands: List[CommandSpec]) -> List[SessionEvent]:
        events: List[SessionEvent] = []
        if not self.sock:
            raise RuntimeError("Socket is not connected")
        # Receive banner
        banner = self._recv_data(self.banner_timeout)
        if banner:
            events.append(SessionEvent(direction="recv", timestamp=datetime.utcnow(), payload=banner))
        for cmd in commands:
            self.sock.settimeout(self.command_timeout)
            sent_at = datetime.utcnow()
            self.sock.sendall(cmd.data)
            events.append(SessionEvent(direction="send", timestamp=sent_at, payload=cmd.data))
            if cmd.expect_response:
                received = self._recv_data(self.command_timeout)
                if received is not None:
                    events.append(SessionEvent(direction="recv", timestamp=datetime.utcnow(), payload=received))
            pause = self.delay_between_commands + cmd.pause_after
            if pause > 0:
                time.sleep(pause)
        return events

    def _recv_data(self, timeout: float) -> bytes | None:
        if not self.sock:
            return None
        self.sock.settimeout(timeout)
        try:
            data = self.sock.recv(self.read_chunk)
            return data
        except socket.timeout:
            return b""
