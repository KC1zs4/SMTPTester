from __future__ import annotations

import socket
import time
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
        delay_before_first_command: float = 0.0,
        delay_between_commands: float = 0.0,
    ):
        self.host_ip = host_ip
        self.port = port
        self.connect_timeout = connect_timeout
        self.command_timeout = command_timeout
        self.banner_timeout = banner_timeout
        self.read_chunk = read_chunk
        self.delay_before_first_command = delay_before_first_command
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

    def run_sequence(self, commands: List[CommandSpec], events: Optional[List[SessionEvent]] = None) -> List[SessionEvent]:
        events = events if events is not None else []
        if not self.sock:
            raise RuntimeError("Socket is not connected")
        # Receive banner
        banner = self._recv_data(self.banner_timeout, f"waiting for SMTP banner from {self.host_ip}:{self.port}")
        if banner:
            events.append(SessionEvent(direction="recv", payload=banner))
        if self.delay_before_first_command > 0:
            time.sleep(self.delay_before_first_command)
        for cmd in commands:
            self.sock.settimeout(self.command_timeout)
            self.sock.sendall(cmd.data)
            events.append(SessionEvent(direction="send", payload=cmd.data))
            preview = self._preview_command(cmd.data)
            received = self._recv_data(
                self.command_timeout,
                f"waiting for response to command {preview} from {self.host_ip}:{self.port}",
            )
            if received is not None:
                events.append(SessionEvent(direction="recv", payload=received))
            pause = self.delay_between_commands + cmd.pause_after
            if pause > 0:
                time.sleep(pause)
        return events

    def _recv_data(self, timeout: float, stage: str) -> bytes:
        if not self.sock:
            raise RuntimeError("Socket is not connected")
        self.sock.settimeout(timeout)
        try:
            data = self.sock.recv(self.read_chunk)
        except socket.timeout as exc:
            raise socket.timeout(f"{stage} (timeout {timeout}s)") from exc
        if data == b"":
            raise ConnectionError(f"Connection closed while {stage}")
        return data

    @staticmethod
    def _preview_command(payload: bytes, max_length: int = 40) -> str:
        # Show a short, safe preview of the command to make timeout errors easier to read.
        text = payload.decode("latin1", errors="replace")
        if len(text) > max_length:
            text = f"{text[:max_length]}..."
        return repr(text)
