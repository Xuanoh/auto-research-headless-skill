---
name: auto-research-headless
description: Turn a user's research insight into a headless continuous experiment loop. Use when the user gives a broad experimental insight or research direction and wants Codex to initialize task state, generate hypotheses, run bounded experiment iterations, record findings, detect stalls, pivot structurally, and continue with minimal human intervention.
---

# Auto Research Headless

Use this skill for long-running experimental work where the user provides an insight rather than a single concrete code edit.

This skill adapts the public Deli_AutoResearch protocol into local project machinery. The protocol ships no executable code by itself; this project supplies the scripts and state layout.

## Core Rule

Do not use chat history as the source of truth. The task directory is the source of truth.

## Primary User Experience

The intended interaction is:

```text
User gives insight -> initialize task -> generate hypotheses -> run experiment loop -> record findings -> continue or pivot.
```

Prefer this path over asking the user to choose subcommands manually.

## Insight-To-Loop Entry Point

When the user provides an insight and asks to start or continue automatic research:

1. If no task exists, initialize one with `auto_research/scripts/init_from_insight.py`.
2. Build the initial state pack with `auto_research/scripts/build_state_pack.py`.
3. Start or prepare the continuous loop with `auto_research/scripts/orchestrator_loop.py`.
4. Report only task id, current iteration, run location, findings, stale status, and next action.

Example:

```bash
python3 auto_research/scripts/init_from_insight.py \
  --insight "<user insight>" \
  --workspace "$(pwd)" \
  --budget-rounds 10 \
  --budget-hours 4

python3 auto_research/scripts/orchestrator_loop.py auto_research/tasks/<task_id> --rounds 3
```

Use `--dry-run` only when validating setup or generating prompts without spending Codex/runtime budget.

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

1. Prefer creating insight-driven tasks with `auto_research/scripts/init_from_insight.py`.
2. Use `auto_research/scripts/init_task.py` only when the user already has a full objective and success criteria.
3. Build its state pack with `auto_research/scripts/build_state_pack.py`.
4. Tell the user the task id and the first next action.

## One Iteration Procedure

1. Run `auto_research/scripts/heartbeat.py <task_dir> --source worker --event start`.
2. Read `state/state_pack.md`, `state/hypotheses.json` when present, and `state/next_iteration.json` when present.
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

## Continuous Loop Contract

`orchestrator_loop.py` is the loop driver. It repeatedly:

- updates heartbeat
- builds `state_pack.md`
- writes `state/next_iteration.json`
- creates a fresh iteration prompt
- invokes Codex with a fresh `codex exec` session unless `--dry-run` is set
- expects the worker iteration to update findings/progress/iteration log
- checks stale state

The loop should stop when:

- `progress.status == "completed"`
- `needs_human_attention == true`
- budget rounds are reached
- an unsafe external dependency blocks progress

Do not use resume for research iterations. Fresh context plus state files is the protocol.

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
