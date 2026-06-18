#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from common import (
    directions_path,
    findings_path,
    predictions_path,
    progress_path,
    read_json,
    read_jsonl,
    reasoning_patterns_path,
    reflections_path,
    require_task_dir,
    utc_now,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build curated state_pack.md for the next AutoResearch iteration.")
    parser.add_argument("task_dir")
    args = parser.parse_args()

    task_dir = require_task_dir(args.task_dir)
    task_spec = (task_dir / "state" / "task_spec.md").read_text(encoding="utf-8")
    progress = read_json(progress_path(task_dir), {})
    directions = read_json(directions_path(task_dir), {"directions": []})
    findings = read_jsonl(findings_path(task_dir))
    predictions = read_jsonl(predictions_path(task_dir))
    reflections = read_jsonl(reflections_path(task_dir))
    reasoning_patterns = read_json(
        reasoning_patterns_path(task_dir),
        {"useful_patterns": [], "failure_patterns": [], "uncertain_patterns": []},
    )
    latest_findings = findings[-20:]
    latest_predictions = predictions[-10:]
    latest_reflections = reflections[-10:]

    pack = [
        "# AutoResearch State Pack",
        "",
        f"Generated: {utc_now()}",
        "",
        "## Task Spec",
        "",
        task_spec.strip(),
        "",
        "## Progress",
        "",
        "```json",
        json.dumps(progress, indent=2, ensure_ascii=False),
        "```",
        "",
        "## Directions Tried",
        "",
        "```json",
        json.dumps(directions, indent=2, ensure_ascii=False),
        "```",
        "",
        "## Latest Findings",
        "",
    ]

    if latest_findings:
        for finding in latest_findings:
            pack.append(f"- {json.dumps(finding, ensure_ascii=False)}")
    else:
        pack.append("- No findings recorded yet.")

    pack.extend(["", "## Prediction Calibration", ""])
    pack.extend(
        [
            "Before each experiment, write an explicit prediction. After metrics are parsed, compare actual results with the prediction and record the reasoning gap.",
            "",
            "### Recent Predictions",
            "",
        ]
    )
    if latest_predictions:
        for prediction in latest_predictions:
            pack.append(f"- {json.dumps(prediction, ensure_ascii=False)}")
    else:
        pack.append("- No predictions recorded yet.")

    pack.extend(["", "### Recent Reflections", ""])
    if latest_reflections:
        for reflection in latest_reflections:
            pack.append(f"- {json.dumps(reflection, ensure_ascii=False)}")
    else:
        pack.append("- No prediction reflections recorded yet.")

    pack.extend(
        [
            "",
            "### Reasoning Patterns",
            "",
            "```json",
            json.dumps(reasoning_patterns, indent=2, ensure_ascii=False),
            "```",
        ]
    )

    pack.extend(
        [
            "",
            "## Next Iteration Contract",
            "",
            "- Start fresh; do not rely on conversation history.",
            "- Choose a direction that differs from prior directions.",
            "- Before running the experiment, record a prediction with `auto_research/scripts/record_prediction.py`.",
            "- Run the smallest informative experiment.",
            "- After parsing metrics, compare the result with the prediction using `auto_research/scripts/compare_prediction.py`.",
            "- If prediction and result disagree, record the reasoning gap and a reusable lesson.",
            "- Record evidence-backed findings.",
            "- Update progress and iteration log before stopping.",
            "- Pivot structurally if stale_count >= 2.",
            "",
        ]
    )

    out = task_dir / "state" / "state_pack.md"
    out.write_text("\n".join(pack), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
