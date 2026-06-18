#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import append_jsonl, directions_path, findings_path, iteration_log_path, progress_path, read_json, read_jsonl, require_task_dir, utc_now, write_json


def metric_worse(mode: str, best, latest) -> bool:
    if best is None or latest is None:
        return False
    return latest > best if mode == "min" else latest < best


def main() -> None:
    parser = argparse.ArgumentParser(description="Record one AutoResearch iteration and update progress.")
    parser.add_argument("task_dir")
    parser.add_argument("--decision", choices=["continue", "pivot", "completed", "failed"], required=True)
    parser.add_argument("--direction-id", required=True)
    parser.add_argument("--direction", default="")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--new-findings", type=int, default=0)
    parser.add_argument("--metric-name")
    parser.add_argument("--metric-value", type=float)
    parser.add_argument("--metric-mode", choices=["min", "max"], default="min")
    parser.add_argument("--run-id")
    parser.add_argument("--prediction-id")
    parser.add_argument("--prediction-match", choices=["yes", "no", "unknown"])
    args = parser.parse_args()

    task_dir = require_task_dir(args.task_dir)
    progress = read_json(progress_path(task_dir), {})
    progress["iteration"] = int(progress.get("iteration", 0)) + 1
    progress["status"] = "completed" if args.decision == "completed" else "idle"
    progress["active_direction_id"] = args.direction_id
    progress["last_progress_at"] = utc_now()
    progress["total_findings"] = len(read_jsonl(findings_path(task_dir)))

    if args.metric_name and args.metric_value is not None:
        metric = progress.get("primary_metric") or {}
        best = metric.get("best")
        mode = args.metric_mode or metric.get("mode", "min")
        latest = args.metric_value
        if best is None or (latest < best if mode == "min" else latest > best):
            best = latest
        progress["primary_metric"] = {"name": args.metric_name, "mode": mode, "best": best, "latest": latest}

    metric = progress.get("primary_metric") or {}
    stale = args.new_findings == 0 or metric_worse(metric.get("mode", "min"), metric.get("best"), metric.get("latest"))
    progress["stale_count"] = int(progress.get("stale_count", 0)) + 1 if stale else 0
    progress["needs_human_attention"] = progress["stale_count"] >= 4
    if progress["stale_count"] >= 2 and args.decision == "continue":
        progress["status"] = "pivoting"

    write_json(progress_path(task_dir), progress)

    directions = read_json(directions_path(task_dir), {"directions": []})
    if not any(item.get("direction_id") == args.direction_id for item in directions.get("directions", [])):
        directions.setdefault("directions", []).append(
            {
                "direction_id": args.direction_id,
                "created_at": utc_now(),
                "hypothesis": args.direction or args.summary,
                "status": "active" if args.decision == "continue" else args.decision,
            }
        )
        write_json(directions_path(task_dir), directions)

    append_jsonl(
        iteration_log_path(task_dir),
        {
            "iteration": progress["iteration"],
            "ts": utc_now(),
            "direction_id": args.direction_id,
            "run_id": args.run_id,
            "decision": args.decision,
            "summary": args.summary,
            "new_findings": args.new_findings,
            "metric": progress.get("primary_metric"),
            "prediction_id": args.prediction_id,
            "prediction_match": args.prediction_match,
            "stale_count": progress["stale_count"],
        },
    )
    print(progress_path(task_dir))


if __name__ == "__main__":
    main()
