from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core.config_loader import load_config
from .core.mx_loader import load_mx_targets
from .core.runner import BatchRunner
from .core.task_loader import TaskLoader


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Direct SMTP sender against MX servers")
    parser.add_argument("--batch", required=True, help="Path to batch directory containing task.py/config.py/mx_target.yaml")
    parser.add_argument("--tasks", nargs="*", help="Optional task names to run")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    batch_path = Path(args.batch).expanduser().resolve()
    if not batch_path.exists():
        print(f"[!] batch path {batch_path} not found")
        sys.exit(1)
    try:
        print(f"[*] loading config from {batch_path}/config.py")
        config = load_config(batch_path)
        print(f"[*] loading tasks from {batch_path}/task.py")
        tasks = TaskLoader(batch_path).load()
        print(f"[*] loading MX targets from {batch_path}/mx_target.yaml")
        mx_records = load_mx_targets(batch_path / "mx_target.yaml")
        if not mx_records:
            print("[!] No MX targets loaded")
            sys.exit(1)
        runner = BatchRunner(batch_path, config, tasks, mx_records)
        runner.run(args.tasks)
    except Exception as exc:  # noqa: BLE001
        print(f"[!] fatal error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
