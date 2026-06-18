#!/usr/bin/env python3
from __future__ import annotations

import argparse
from typing import Any

from common import (
    append_jsonl,
    predictions_path,
    read_json,
    read_jsonl,
    reasoning_patterns_path,
    reflections_path,
    require_task_dir,
    utc_now,
    write_json,
)


def direction_from_values(mode: str, actual: float, baseline: float, tolerance: float) -> str:
    delta = actual - baseline
    if abs(delta) <= tolerance:
        return "neutral"
    if mode == "min":
        return "improve" if actual < baseline else "worse"
    return "improve" if actual > baseline else "worse"


def expected_value_match(actual: float, expected: float | None, tolerance: float) -> bool | None:
    if expected is None:
        return None
    return abs(actual - expected) <= tolerance


def direction_match(expected: str, actual: str | None) -> bool | None:
    if expected == "unknown" or actual is None:
        return None
    return expected == actual


def find_prediction(rows: list[Any], prediction_id: str) -> dict[str, Any]:
    for row in rows:
        if isinstance(row, dict) and row.get("prediction_id") == prediction_id:
            return row
    raise SystemExit(f"Prediction not found: {prediction_id}")


def update_reasoning_patterns(task_dir, matched: bool | None, reflection: dict[str, Any]) -> None:
    patterns = read_json(
        reasoning_patterns_path(task_dir),
        {"useful_patterns": [], "failure_patterns": [], "uncertain_patterns": []},
    )
    lesson = reflection.get("lesson")
    if not lesson:
        return
    if matched is True:
        key = "useful_patterns"
    elif matched is False:
        key = "failure_patterns"
    else:
        key = "uncertain_patterns"
    entries = patterns.setdefault(key, [])
    entry = {
        "ts": reflection["ts"],
        "prediction_id": reflection["prediction_id"],
        "direction_id": reflection.get("direction_id"),
        "lesson": lesson,
        "reasoning_gap": reflection.get("reasoning_gap"),
        "matched": matched,
    }
    if not any(item.get("lesson") == lesson for item in entries if isinstance(item, dict)):
        entries.append(entry)
    write_json(reasoning_patterns_path(task_dir), patterns)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare actual metrics with a pre-experiment AutoResearch prediction.")
    parser.add_argument("task_dir")
    parser.add_argument("--prediction-id", required=True)
    parser.add_argument("--metric-name")
    parser.add_argument("--actual-value", type=float, required=True)
    parser.add_argument("--baseline-value", type=float, help="Baseline or previous value used to classify improve/worse/neutral.")
    parser.add_argument("--metric-mode", choices=["min", "max"], default="min")
    parser.add_argument("--tolerance", type=float, default=0.0)
    parser.add_argument("--run-id")
    parser.add_argument("--reasoning-gap", default="", help="Why the prediction did or did not match the result.")
    parser.add_argument("--lesson", default="", help="Reusable reasoning lesson for future iterations.")
    args = parser.parse_args()

    task_dir = require_task_dir(args.task_dir)
    predictions = read_jsonl(predictions_path(task_dir))
    prediction = find_prediction(predictions, args.prediction_id)
    actual_direction = None
    if args.baseline_value is not None:
        actual_direction = direction_from_values(args.metric_mode, args.actual_value, args.baseline_value, args.tolerance)

    expected_direction = str(prediction.get("expected_direction") or "unknown")
    by_direction = direction_match(expected_direction, actual_direction)
    by_value = expected_value_match(args.actual_value, prediction.get("expected_value"), args.tolerance)
    matched = by_direction if by_direction is not None else by_value

    index = len(read_jsonl(reflections_path(task_dir))) + 1
    reflection = {
        "reflection_id": f"refl_{index:04d}",
        "ts": utc_now(),
        "prediction_id": args.prediction_id,
        "direction_id": prediction.get("direction_id"),
        "run_id": args.run_id or prediction.get("run_id"),
        "metric_name": args.metric_name or prediction.get("metric_name"),
        "expected": {
            "direction": expected_direction,
            "value": prediction.get("expected_value"),
            "confidence": prediction.get("confidence"),
            "rationale": prediction.get("rationale"),
        },
        "actual": {
            "value": args.actual_value,
            "baseline_value": args.baseline_value,
            "direction": actual_direction,
            "mode": args.metric_mode,
            "tolerance": args.tolerance,
        },
        "matched": matched,
        "reasoning_gap": args.reasoning_gap,
        "lesson": args.lesson,
    }
    append_jsonl(reflections_path(task_dir), reflection)
    update_reasoning_patterns(task_dir, matched, reflection)
    print(reflection["reflection_id"])


if __name__ == "__main__":
    main()
