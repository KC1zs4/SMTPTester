from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .models import CommandTemplate, TaskDefinition
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
        target_values = data.get("targets") or data.get("target_values") or {}
        if target_values and not isinstance(target_values, dict):
            raise ValueError(f"Task {name} targets must be a dict keyed by domain")
        for domain, override in target_values.items():
            if not isinstance(override, dict):
                raise ValueError(f"Task {name} target override for {domain} must be a dict")
        commands_source = data.get("commands")
        if commands_source is None:
            template_name = data.get("template")
            if template_name not in self.templates:
                raise ValueError(f"Task {name} references missing template {template_name}")
            commands_source = self.templates[template_name]
        commands = [self._normalize_command(cmd) for cmd in commands_source]
        return TaskDefinition(
            name=name,
            commands=commands,
            description=description,
            values=values,
            target_values=target_values or None,
        )

    @staticmethod
    def _normalize_command(entry: Any) -> CommandTemplate:
        pause_after = 0.0
        raw = entry
        if isinstance(entry, dict):
            if "data" not in entry:
                raise ValueError("Command dict must include data")
            raw = entry.get("data")
            pause_after = float(entry.get("pause_after", 0.0))
        return CommandTemplate(raw=raw, pause_after=pause_after)
