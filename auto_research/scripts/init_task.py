#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import utc_now, write_json


def render_template(template: str, values: dict[str, str]) -> str:
    result = template
    for key, value in values.items():
        result = result.replace("{{" + key + "}}", value)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize an AutoResearch task.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--success-criteria", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--root", default="auto_research/tasks")
    args = parser.parse_args()

    task_dir = Path(args.root) / args.task_id
    state = task_dir / "state"
    logs = task_dir / "logs"
    for folder in [state, logs, task_dir / "runs", task_dir / "reports"]:
        folder.mkdir(parents=True, exist_ok=True)

    template_path = Path("auto_research/templates/task_spec.md")
    template = template_path.read_text(encoding="utf-8")
    spec = render_template(
        template,
        {
            "title": args.title,
            "objective": args.objective,
            "success_criteria": args.success_criteria,
            "workspace": str(Path(args.workspace).resolve()),
        },
    )
    (state / "task_spec.md").write_text(spec, encoding="utf-8")

    write_json(
        state / "progress.json",
        {
            "task_id": args.task_id,
            "iteration": 0,
            "status": "idle",
            "stale_count": 0,
            "total_findings": 0,
            "primary_metric": {"name": None, "mode": "min", "best": None, "latest": None},
            "active_direction_id": None,
            "last_progress_at": None,
            "needs_human_attention": False,
        },
    )
    write_json(state / "directions_tried.json", {"directions": []})
    write_json(state / "reasoning_patterns.json", {"useful_patterns": [], "failure_patterns": [], "uncertain_patterns": []})
    write_json(state / "heartbeat.json", {"task_id": args.task_id, "last_seen": utc_now(), "source": "init"})
    for file_name in ["findings.jsonl", "iteration_log.jsonl", "predictions.jsonl", "reflections.jsonl"]:
        (state / file_name).touch()
    for file_name in ["work.jsonl", "orchestrator.jsonl", "heartbeat.jsonl"]:
        (logs / file_name).touch()

    print(task_dir)


if __name__ == "__main__":
    main()
