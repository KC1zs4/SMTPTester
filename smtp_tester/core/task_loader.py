from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .models import CommandSpec, TaskDefinition
from .utils import load_python_module


class TaskLoader:
    def __init__(self, batch_path: Path):
        self.batch_path = batch_path
        self.templates: Dict[str, List[Any]] = {}
        self.tasks: List[TaskDefinition] = []

    def load(self) -> List[TaskDefinition]:
        module = load_python_module(self.batch_path / "task.py", f"{self.batch_path.name}_task")
        templates = getattr(module, "TEMPLATES", {})
        tasks = getattr(module, "TASKS", [])
        if not isinstance(templates, dict):
            raise ValueError("TEMPLATES must be a dictionary")
        if not isinstance(tasks, list):
            raise ValueError("TASKS must be a list")
        self.templates = templates
        self.tasks = [self._build_task(task) for task in tasks]
        return self.tasks

    def _build_task(self, data: dict) -> TaskDefinition:
        if "name" not in data:
            raise ValueError("Task missing name")
        name = data["name"]
        description = data.get("description")
        values = data.get("values", {})
        if not isinstance(values, dict):
            raise ValueError(f"Task {name} values must be dict")
        commands_source = data.get("commands")
        if commands_source is None:
            template_name = data.get("template")
            if template_name not in self.templates:
                raise ValueError(f"Task {name} references missing template {template_name}")
            commands_source = self.templates[template_name]
        commands = [self._normalize_command(cmd, values) for cmd in commands_source]
        return TaskDefinition(name=name, commands=commands, description=description, values=values)

    @staticmethod
    def _normalize_command(entry: Any, values: dict) -> CommandSpec:
        expect_response = True
        pause_after = 0.0
        raw = entry
        if isinstance(entry, dict):
            raw = entry.get("data")
            expect_response = entry.get("expect_response", True)
            pause_after = float(entry.get("pause_after", 0.0))
        data_bytes = TaskLoader._render_bytes(raw, values)
        return CommandSpec(data=data_bytes, expect_response=bool(expect_response), pause_after=pause_after)

    @staticmethod
    def _render_bytes(raw: Any, values: dict) -> bytes:
        if isinstance(raw, bytes):
            text = raw.decode("latin1")
        elif isinstance(raw, str):
            text = raw
        else:
            raise ValueError("Command data must be str or bytes or dict with data")
        formatted = text.format(**values) if values else text
        return formatted.encode("latin1")
