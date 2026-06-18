#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import directions_path, progress_path, read_json, read_jsonl, require_task_dir, utc_now, write_json


AXES = ["data", "objective", "model", "training", "evaluation", "environment", "code"]


def choose_axis(directions: list[dict], stale_count: int) -> str:
    tried_axes = [item.get("structural_axis") or item.get("axis") for item in directions]
    if stale_count >= 2:
        for axis in AXES:
            if axis not in tried_axes:
                return axis
    return AXES[len(directions) % len(AXES)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Plan the next insight-driven AutoResearch iteration.")
    parser.add_argument("task_dir")
    args = parser.parse_args()

    task_dir = require_task_dir(args.task_dir)
    progress = read_json(progress_path(task_dir), {})
    directions = read_json(directions_path(task_dir), {"directions": []}).get("directions", [])
    hypotheses = read_json(task_dir / "state" / "hypotheses.json", {"hypotheses": []})
    stale_count = int(progress.get("stale_count", 0))
    iteration = int(progress.get("iteration", 0)) + 1
    axis = choose_axis(directions, stale_count)
    direction_id = f"dir_{iteration:03d}_{axis}"
    open_hypotheses = [item for item in hypotheses.get("hypotheses", []) if item.get("status") == "open"]
    hypothesis = open_hypotheses[0]["claim"] if open_hypotheses else f"Explore the {axis} structural axis."
    plan = {
        "planned_at": utc_now(),
        "iteration": iteration,
        "direction_id": direction_id,
        "structural_axis": axis,
        "hypothesis": hypothesis,
        "stale_count": stale_count,
        "mode": "pivot" if stale_count >= 2 else "continue",
    }
    write_json(task_dir / "state" / "next_iteration.json", plan)
    print(json.dumps(plan, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

