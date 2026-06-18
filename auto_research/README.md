# Auto Research

Headless AutoResearch system for long-running experimental work.

This project adapts the Deli_AutoResearch protocol into a local file protocol plus scripts. It is intentionally headless: the durable source of truth is the task directory, not a GUI or chat history.

## Core Idea

```text
direction -> hypothesis -> experiment -> metrics -> findings -> decision -> next iteration
```

Each task stores its state under `auto_research/tasks/<task_id>/`. Codex or another agent reads the curated state pack, performs one bounded iteration, writes back findings and logs, then the state machine decides whether to continue, pivot, or ask for human attention.

## Quick Start

Create a new task:

```bash
python3 auto_research/scripts/init_task.py \
  --task-id basic_ts_etth1_norm \
  --title "BasicTS ETTh1 normalization study" \
  --objective "Explore normalization and training-strategy changes for BasicTS ETTh1 forecasting." \
  --success-criteria "Find a reproducible metric improvement or a well-evidenced negative result." \
  --workspace /path/to/BasicTS
```

Build the prompt context for the next iteration:

```bash
python3 auto_research/scripts/build_state_pack.py auto_research/tasks/basic_ts_etth1_norm
```

Run a generic command as an experiment:

```bash
python3 auto_research/scripts/run_experiment.py \
  auto_research/tasks/basic_ts_etth1_norm \
  --name smoke \
  --cwd /path/to/workspace \
  -- echo '{"metric":"val/mae","value":0.42}'
```

Parse metrics from a run:

```bash
python3 auto_research/scripts/parse_metrics.py auto_research/tasks/basic_ts_etth1_norm/runs/<run_id>
```

Record an iteration:

```bash
python3 auto_research/scripts/record_iteration.py \
  auto_research/tasks/basic_ts_etth1_norm \
  --decision continue \
  --direction-id dir_001 \
  --summary "Smoke run completed." \
  --new-findings 1
```

Check stale state:

```bash
python3 auto_research/scripts/stale_detector.py auto_research/tasks/basic_ts_etth1_norm
```

## Protocol Files

```text
state/task_spec.md
state/progress.json
state/findings.jsonl
state/directions_tried.json
state/iteration_log.jsonl
state/heartbeat.json
state/state_pack.md
logs/work.jsonl
logs/orchestrator.jsonl
logs/heartbeat.jsonl
runs/
reports/
```

## Relationship To Skills

The project includes `skill/SKILL.md`, a portable Codex skill that describes how to operate this folder. The skill is the workflow contract. The scripts and state files are the durable machinery.
