#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from common import utc_now, write_json


AXES = ["data", "objective", "model", "training", "evaluation", "environment", "code"]


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower()).strip("_")
    return slug[:48] or "auto_research_task"


def hypotheses_from_insight(insight: str) -> list[dict]:
    return [
        {
            "hypothesis_id": "hyp_001",
            "axis": "data",
            "claim": f"The insight may be explained by a data/preprocessing condition: {insight}",
            "status": "open",
        },
        {
            "hypothesis_id": "hyp_002",
            "axis": "training",
            "claim": f"The insight may depend on training dynamics or optimization stability: {insight}",
            "status": "open",
        },
        {
            "hypothesis_id": "hyp_003",
            "axis": "evaluation",
            "claim": f"The insight may only hold under specific metrics, horizons, seeds, or splits: {insight}",
            "status": "open",
        },
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize an AutoResearch task directly from an experimental insight.")
    parser.add_argument("--insight", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--task-id")
    parser.add_argument("--title")
    parser.add_argument("--success-criteria", default="Produce evidence-backed findings and reproducible experiment logs.")
    parser.add_argument("--budget-rounds", type=int, default=10)
    parser.add_argument("--budget-hours", type=float, default=4.0)
    parser.add_argument("--root", default="auto_research/tasks")
    args = parser.parse_args()

    title = args.title or f"Insight study: {args.insight[:64]}"
    task_id = args.task_id or slugify(title)
    task_dir = Path(args.root) / task_id
    state = task_dir / "state"
    logs = task_dir / "logs"
    for folder in [state, logs, task_dir / "runs", task_dir / "reports"]:
        folder.mkdir(parents=True, exist_ok=True)

    spec = f"""# {title}

## Insight

{args.insight}

## Objective

Turn the insight into a sustained experimental research loop. Generate hypotheses, predict experiment outcomes, run bounded experiments, compare predictions with metrics, record findings, and pivot structurally when progress stalls.

## Workspace

{Path(args.workspace).resolve()}

## Success Criteria

- {args.success_criteria}

## Budgets

- Max rounds: {args.budget_rounds}
- Max hours: {args.budget_hours}

## Constraints

- Persist progress to task state files.
- Prefer small, verifiable experiments.
- Before each experiment, record an explicit prediction and confidence.
- After parsing metrics, compare actual results with the prediction and record any reasoning gap.
- Record negative results.
- Avoid repeating directions already listed in `directions_tried.json`.
- If `stale_count >= 2`, pivot across a structural axis: {", ".join(AXES)}.

## Initial Direction

Start with the smallest experiment that can validate or falsify one hypothesis derived from the insight.
"""
    (state / "task_spec.md").write_text(spec, encoding="utf-8")
    write_json(state / "hypotheses.json", {"insight": args.insight, "hypotheses": hypotheses_from_insight(args.insight)})
    write_json(
        state / "progress.json",
        {
            "task_id": task_id,
            "iteration": 0,
            "status": "idle",
            "stale_count": 0,
            "total_findings": 0,
            "primary_metric": {"name": None, "mode": "min", "best": None, "latest": None},
            "active_direction_id": None,
            "last_progress_at": None,
            "needs_human_attention": False,
            "budget_rounds": args.budget_rounds,
            "budget_hours": args.budget_hours,
            "started_at": utc_now(),
        },
    )
    write_json(state / "directions_tried.json", {"directions": []})
    write_json(state / "reasoning_patterns.json", {"useful_patterns": [], "failure_patterns": [], "uncertain_patterns": []})
    write_json(state / "heartbeat.json", {"task_id": task_id, "last_seen": utc_now(), "source": "init_from_insight"})
    for file_name in ["findings.jsonl", "iteration_log.jsonl", "predictions.jsonl", "reflections.jsonl"]:
        (state / file_name).touch()
    for file_name in ["work.jsonl", "orchestrator.jsonl", "heartbeat.jsonl"]:
        (logs / file_name).touch()

    print(task_dir)


if __name__ == "__main__":
    main()
