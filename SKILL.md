---
name: auto-research-headless
description: Operate a headless AutoResearch experiment system using task state files, bounded iterations, stale detection, structural pivots, and local scripts. Use when the user gives a broad research or experiment direction and wants Codex to keep running experiments without a GUI.
---

# Auto Research Headless

Use this skill for long-running experimental work where the user provides a direction rather than a single concrete code edit.

This skill adapts the public Deli_AutoResearch protocol into local project machinery. The protocol ships no executable code by itself; this project supplies the scripts and state layout.

## Core Rule

Do not use chat history as the source of truth. The task directory is the source of truth.

## Required State Layout

Each task lives at:

```text
auto_research/tasks/<task_id>/
  state/
    task_spec.md
    progress.json
    findings.jsonl
    directions_tried.json
    iteration_log.jsonl
    heartbeat.json
    state_pack.md
  logs/
    work.jsonl
    orchestrator.jsonl
    heartbeat.jsonl
  runs/
  reports/
```

## When Starting A New Task

1. Create it with `auto_research/scripts/init_task.py`.
2. Build its state pack with `auto_research/scripts/build_state_pack.py`.
3. Tell the user the task id and the first next action.

## One Iteration Procedure

1. Run `auto_research/scripts/heartbeat.py <task_dir> --source worker --event start`.
2. Read `state/state_pack.md`.
3. Choose one direction that is different from prior directions.
4. Run the smallest informative experiment or make the smallest necessary code/config change.
5. Store every command run under `runs/` using `auto_research/scripts/run_experiment.py` when possible.
6. Parse metrics with `auto_research/scripts/parse_metrics.py`.
7. Append findings with `auto_research/scripts/append_finding.py`.
8. Record the iteration with `auto_research/scripts/record_iteration.py`.
9. Rebuild `state/state_pack.md`.
10. Run `auto_research/scripts/heartbeat.py <task_dir> --source worker --event finish`.

## Stale Handling

Use `auto_research/scripts/stale_detector.py`.

- `stale_count == 0`: continue.
- `stale_count == 1`: continue, but prefer stronger validation.
- `stale_count >= 2`: pivot structurally.
- `stale_count >= 4`: stop and produce a human-attention report.

Structural pivot axes:

- data
- objective
- model
- training
- evaluation
- environment
- code

Do not treat minor hyperparameter tuning as a structural pivot.

## Completion Report

At the end of a turn, report:

- task id
- iteration number
- run ids
- metrics
- new findings
- stale status
- next action

Keep the report short. The detailed record belongs in the task files.

