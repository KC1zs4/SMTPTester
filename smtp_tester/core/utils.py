from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


def load_python_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def simple_yaml_dump(data: Any) -> str:
    """Minimal YAML serializer for simple dict/list/str content with multiline support."""

    def serialize(obj: Any, indent: int = 0) -> list[str]:
        pad = " " * indent
        if isinstance(obj, dict):
            lines: list[str] = []
            for key, value in obj.items():
                if isinstance(value, str) and _has_newline(value):
                    lines.append(f"{pad}{key}: |")
                    lines.extend(_block_lines(value, indent + 2))
                elif isinstance(value, (dict, list)):
                    lines.append(f"{pad}{key}:")
                    lines.extend(serialize(value, indent + 2))
                else:
                    lines.append(f"{pad}{key}: {scalar(value)}")
            return lines
        if isinstance(obj, list):
            lines: list[str] = []
            for item in obj:
                if isinstance(item, str) and _has_newline(item):
                    lines.append(f"{pad}- |")
                    lines.extend(_block_lines(item, indent + 2))
                elif isinstance(item, (dict, list)):
                    lines.append(f"{pad}-")
                    lines.extend(serialize(item, indent + 2))
                else:
                    lines.append(f"{pad}- {scalar(item)}")
            return lines
        return [f"{pad}{scalar(obj)}"]

    def scalar(value: Any) -> str:
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        text = str(value)
        if any(ch in text for ch in [":", "-", "#"]):
            escaped = text.replace("\n", "\\n").replace("\r", "\\r")
            return f"\"{escaped}\""
        return text

    def _has_newline(value: str) -> bool:
        return "\n" in value or "\r" in value

    def _block_lines(text: str, indent: int) -> list[str]:
        block_pad = " " * indent
        # Normalize to visible lines while preserving empty trailing lines.
        parts = text.splitlines()
        if text.endswith(("\n", "\r")):
            parts.append("")
        if not parts:
            return [block_pad]
        return [f"{block_pad}{line}" for line in parts]

    return "\n".join(serialize(data)) + "\n"
