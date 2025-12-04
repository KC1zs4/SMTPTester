SMTP Tester
===========

Lightweight Python 3.12 script to open direct SMTP sessions to specified MX servers (IPv4, no TLS), driven by per-batch configuration and task definitions.

Layout
------

- `smtp_tester/` core modules and CLI entry.
- `batch/<name>/` a batch folder with:
  - `task.py` task/templates describing SMTP byte sequences.
  - `config.py` execution tuning (timeouts, delays, log path).
  - `mx_target.yaml` MX targets; each IPv4 is hit once per task.
- `logs/` session logs in YAML (`latin-1` payload to keep bytes intact).

Usage
-----

```
python -m smtp_tester.cli --batch batch/b0_example
# run specific tasks
python -m smtp_tester.cli --batch batch/b0_example --tasks test_mail noop_check
```

Notes
-----

- Uses plain sockets (`AF_INET`) and never negotiates TLS.
- Logs every send/receive byte sequence; errors/timeouts still produce a YAML log.
- PyYAML is optional; a minimal parser is included for `mx_target.yaml` if PyYAML is missing.
- Keep command data in templates as raw strings/bytes; `{placeholders}` are formatted per-task.
