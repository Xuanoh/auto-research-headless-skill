# Auto Research

Headless AutoResearch system for long-running experimental work.

This project adapts the Deli_AutoResearch protocol into a local file protocol plus scripts. It is intentionally headless: the durable source of truth is the task directory, not a GUI or chat history.

## Core Idea

```text
direction -> hypothesis -> prediction -> experiment -> metrics -> prediction reflection -> findings -> decision -> next iteration
```

Each task stores its state under `auto_research/tasks/<task_id>/`. Codex or another agent reads the curated state pack, performs one bounded iteration, writes back findings and logs, then the state machine decides whether to continue, pivot, or ask for human attention.

The loop is prediction-calibrated: every experiment records an expected outcome before the benchmark runs, then compares actual metrics with that prediction. Mismatches become reasoning reflections and reusable lessons for later iterations.

## Quick Start

Start from an insight:

```bash
python3 auto_research/scripts/init_from_insight.py \
  --insight "A concrete experimental hunch or research direction." \
  --workspace "$(pwd)" \
  --budget-rounds 10 \
  --budget-hours 4
```

Run a dry loop that writes the next iteration prompt without invoking Codex:

```bash
python3 auto_research/scripts/orchestrator_loop.py auto_research/tasks/<task_id> --rounds 1 --dry-run
```

Run a live loop that invokes fresh Codex sessions:

```bash
python3 auto_research/scripts/orchestrator_loop.py auto_research/tasks/<task_id> --rounds 3
```

Manual task creation is still available when you already know the objective and success criteria.

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

Record a prediction before an experiment:

```bash
python3 auto_research/scripts/record_prediction.py \
  auto_research/tasks/basic_ts_etth1_norm \
  --direction-id dir_001 \
  --hypothesis "Normalization should reduce validation MAE." \
  --prediction "val/mae should improve relative to the current baseline." \
  --metric-name val/mae \
  --expected-direction improve \
  --confidence 0.6 \
  --rationale "The transform reduces scale variance across channels."
```

Compare the prediction with actual metrics:

```bash
python3 auto_research/scripts/compare_prediction.py \
  auto_research/tasks/basic_ts_etth1_norm \
  --prediction-id pred_0001 \
  --metric-name val/mae \
  --actual-value 0.42 \
  --baseline-value 0.45 \
  --metric-mode min \
  --lesson "Scale-normalization hypotheses should check leakage and horizon-specific effects separately."
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
state/predictions.jsonl
state/reflections.jsonl
state/reasoning_patterns.json
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
