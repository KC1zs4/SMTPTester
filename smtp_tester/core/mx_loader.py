from __future__ import annotations

import ipaddress
from pathlib import Path
from typing import Any, Dict, List

from .models import MXRecord


def load_mx_targets(path: Path) -> List[MXRecord]:
    data = _read_yaml(path)
    if not isinstance(data, dict):
        raise ValueError("mx_target.yaml must be a mapping of domain to records")
    records: List[MXRecord] = []
    for domain, entries in data.items():
        if not isinstance(entries, list):
            continue
        for item in entries:
            if not isinstance(item, dict):
                continue
            hostname = str(item.get("hostname", "")).strip()
            preference = int(item.get("preference", 0))
            ips = item.get("ips", [])
            if not hostname or not isinstance(ips, list):
                continue
            for ip in ips:
                if not _is_ipv4(ip):
                    continue
                records.append(
                    MXRecord(
                        hostname=hostname,
                        preference=preference,
                        ip=str(ip),
                        domain=str(domain),
                    )
                )
    return records


def _read_yaml(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except Exception:
        return _minimal_yaml_parse(text)


def _minimal_yaml_parse(text: str) -> Any:
    lines = [line for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
    index = 0

    def current_indent(line: str) -> int:
        return len(line) - len(line.lstrip(" "))

    def parse_scalar(raw: str) -> Any:
        if raw.startswith("\"") and raw.endswith("\""):
            return raw[1:-1]
        if raw.lower() == "null":
            return None
        if raw.lower() in {"true", "false"}:
            return raw.lower() == "true"
        try:
            return int(raw)
        except ValueError:
            try:
                return float(raw)
            except ValueError:
                return raw

    def parse_block(expected_indent: int) -> Any:
        nonlocal index
        if index >= len(lines):
            return None
        line = lines[index]
        indent = current_indent(line)
        if indent != expected_indent:
            return None
        content = line.strip()
        if content.startswith("- "):
            items: list[Any] = []
            while index < len(lines):
                line = lines[index]
                indent = current_indent(line)
                if indent != expected_indent or not line.strip().startswith("- "):
                    break
                entry = line.strip()[2:]
                index += 1
                if ":" in entry:
                    key, rest = entry.split(":", 1)
                    key = key.strip()
                    if rest.strip():
                        item: Any = {key: parse_scalar(rest.strip())}
                    else:
                        item = {key: parse_block(expected_indent + 2)}
                elif entry:
                    item = parse_scalar(entry)
                else:
                    item = parse_block(expected_indent + 2)
                while index < len(lines) and current_indent(lines[index]) > expected_indent:
                    child = parse_block(expected_indent + 2)
                    if isinstance(item, dict) and isinstance(child, dict):
                        item.update(child)
                    elif isinstance(item, dict):
                        item["value"] = child
                    else:
                        item = child
                items.append(item)
            return items
        mapping: Dict[str, Any] = {}
        while index < len(lines):
            line = lines[index]
            indent = current_indent(line)
            if indent != expected_indent:
                break
            content = line.strip()
            if ":" not in content:
                index += 1
                continue
            key, rest = content.split(":", 1)
            if rest.strip():
                mapping[key.strip()] = parse_scalar(rest.strip())
                index += 1
            else:
                index += 1
                if index < len(lines) and current_indent(lines[index]) > expected_indent:
                    mapping[key.strip()] = parse_block(expected_indent + 2)
                else:
                    mapping[key.strip()] = None
        return mapping

    result = parse_block(0)
    return result


def _is_ipv4(value: str) -> bool:
    try:
        return ipaddress.ip_address(value).version == 4
    except ValueError:
        return False
