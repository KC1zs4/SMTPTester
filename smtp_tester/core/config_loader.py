from __future__ import annotations

from pathlib import Path
from typing import Any

from .utils import load_python_module


DEFAULTS: dict[str, Any] = {
    "connect_timeout": 5.0,
    "command_timeout": 5.0,
    "banner_timeout": 5.0,
    "delay_before_first_command": 0.0,
    "delay_between_commands": 0,
    "delay_between_hosts": 1.0,
    "log_dir": "log",
    "read_chunk": 4096,
    "port": 25,
}


def load_config(batch_path: Path) -> dict[str, Any]:
    cfg_path = batch_path / "config.py"
    module = load_python_module(cfg_path, f"{batch_path.name}_config")
    if not hasattr(module, "CONFIG") or not isinstance(module.CONFIG, dict):
        raise ValueError("config.py must define CONFIG dictionary")
    config = DEFAULTS.copy()
    config.update(module.CONFIG)
    return config
