#!/usr/bin/env python3
from __future__ import annotations

import argparse

from common import predictions_path, progress_path, read_json, read_jsonl, require_task_dir, utc_now, append_jsonl


def bounded_confidence(value: str) -> float:
    number = float(value)
    if number < 0 or number > 1:
        raise argparse.ArgumentTypeError("confidence must be between 0 and 1")
    return number


def main() -> None:
    parser = argparse.ArgumentParser(description="Record a pre-experiment prediction for one AutoResearch iteration.")
    parser.add_argument("task_dir")
    parser.add_argument("--direction-id", required=True)
    parser.add_argument("--hypothesis", required=True)
    parser.add_argument("--prediction", required=True, help="Plain-language prediction before running the experiment.")
    parser.add_argument("--metric-name", help="Metric expected to move, such as val/mae.")
    parser.add_argument("--expected-direction", choices=["improve", "worse", "neutral", "unknown"], default="unknown")
    parser.add_argument("--expected-value", type=float)
    parser.add_argument("--confidence", type=bounded_confidence, default=0.5)
    parser.add_argument("--rationale", default="", help="Why this prediction should hold.")
    parser.add_argument("--failure-mode", action="append", default=[], help="Potential reason the prediction could fail.")
    parser.add_argument("--run-id")
    args = parser.parse_args()

    task_dir = require_task_dir(args.task_dir)
    progress = read_json(progress_path(task_dir), {})
    index = len(read_jsonl(predictions_path(task_dir))) + 1
    prediction = {
        "prediction_id": f"pred_{index:04d}",
        "ts": utc_now(),
        "iteration": int(progress.get("iteration", 0)) + 1,
        "direction_id": args.direction_id,
        "hypothesis": args.hypothesis,
        "prediction": args.prediction,
        "metric_name": args.metric_name,
        "expected_direction": args.expected_direction,
        "expected_value": args.expected_value,
        "confidence": args.confidence,
        "rationale": args.rationale,
        "failure_modes": args.failure_mode,
        "run_id": args.run_id,
        "status": "pending",
    }
    append_jsonl(predictions_path(task_dir), prediction)
    print(prediction["prediction_id"])


if __name__ == "__main__":
    main()
