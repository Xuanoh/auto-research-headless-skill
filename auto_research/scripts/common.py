#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def append_jsonl(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(data, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[Any]:
    if not path.exists():
        return []
    rows: list[Any] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append({"raw": line})
    return rows


def require_task_dir(value: str) -> Path:
    task_dir = Path(value).resolve()
    if not (task_dir / "state").is_dir():
        raise SystemExit(f"Task directory missing state/: {task_dir}")
    return task_dir


def log_line(task_dir: Path, stream: str, level: str, event: str, detail: Any) -> None:
    append_jsonl(
        task_dir / "logs" / f"{stream}.jsonl",
        {
            "ts": utc_now(),
            "source": stream,
            "level": level,
            "event": event,
            "detail": detail,
        },
    )


def progress_path(task_dir: Path) -> Path:
    return task_dir / "state" / "progress.json"


def findings_path(task_dir: Path) -> Path:
    return task_dir / "state" / "findings.jsonl"


def directions_path(task_dir: Path) -> Path:
    return task_dir / "state" / "directions_tried.json"


def iteration_log_path(task_dir: Path) -> Path:
    return task_dir / "state" / "iteration_log.jsonl"

