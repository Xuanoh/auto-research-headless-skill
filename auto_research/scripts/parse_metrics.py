#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


METRIC_RE = re.compile(r"(?P<name>[A-Za-z0-9_./-]*(?:mae|rmse|mape|loss|acc|accuracy)[A-Za-z0-9_./-]*)\s*[:=]\s*(?P<value>-?\d+(?:\.\d+)?)", re.I)


def parse_jsonish(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            rows.extend(metrics_from_dict(data, source=str(path)))
    return rows


def metrics_from_dict(data: dict, source: str) -> list[dict]:
    rows: list[dict] = []
    if "metric" in data and "value" in data:
        rows.append({"name": str(data["metric"]), "value": float(data["value"]), "source": source})
    for key, value in data.items():
        if isinstance(value, (int, float)) and re.search(r"mae|rmse|mape|loss|acc|accuracy", key, re.I):
            rows.append({"name": key, "value": float(value), "source": source})
    return rows


def parse_csv(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rows.extend(metrics_from_dict(row, source=str(path)))
    return rows


def parse_text(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    for match in METRIC_RE.finditer(path.read_text(encoding="utf-8", errors="ignore")):
        rows.append({"name": match.group("name"), "value": float(match.group("value")), "source": str(path)})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse metrics from an AutoResearch run directory.")
    parser.add_argument("run_dir")
    args = parser.parse_args()
    run_dir = Path(args.run_dir).resolve()
    if not run_dir.is_dir():
        raise SystemExit(f"Run directory not found: {run_dir}")

    metrics: list[dict] = []
    for path in [run_dir / "metrics.jsonl", run_dir / "metrics.json", run_dir / "stdout.log", run_dir / "stderr.log"]:
        if path.suffix in [".json", ".jsonl"]:
            metrics.extend(parse_jsonish(path))
        else:
            metrics.extend(parse_text(path))
    for path in run_dir.glob("*.csv"):
        metrics.extend(parse_csv(path))

    out = run_dir / "metrics.parsed.jsonl"
    with out.open("w", encoding="utf-8") as handle:
        for metric in metrics:
            handle.write(json.dumps(metric, ensure_ascii=False) + "\n")
    print(out)


if __name__ == "__main__":
    main()

