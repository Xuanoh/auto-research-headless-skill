# Auto Research Agent Instructions

When working under `auto_research/`, follow this headless AutoResearch protocol.

## Non-Negotiable Rules

- Persist progress to task files. Do not rely on chat history.
- Run one bounded iteration at a time.
- Start from `state/state_pack.md` when it exists; otherwise build it with `scripts/build_state_pack.py`.
- Before running an experiment, write a prediction to `state/predictions.jsonl` with `scripts/record_prediction.py`.
- After parsing metrics, compare actual results with the prediction using `scripts/compare_prediction.py`.
- If prediction and result disagree, record a reasoning gap and reusable lesson.
- Write findings to `state/findings.jsonl`.
- Write iteration outcomes to `state/iteration_log.jsonl` through `scripts/record_iteration.py`.
- Update heartbeat before and after long work with `scripts/heartbeat.py`.
- Run validation between iterations when the workspace supports it.
- Prefer structural pivots after repeated stalls.
- Do not ask the user during an active run unless the task is blocked by an external dependency or unsafe action.

## Insight-To-Loop Default

When the user provides an experimental insight, initialize a task with:

```bash
python3 auto_research/scripts/init_from_insight.py \
  --insight "<insight>" \
  --workspace "$(pwd)" \
  --budget-rounds 10 \
  --budget-hours 4
```

Then run or prepare the loop with:

```bash
python3 auto_research/scripts/orchestrator_loop.py auto_research/tasks/<task_id> --rounds 3
```

Use `--dry-run` for setup validation only.

## Iteration Loop

1. Read `state/task_spec.md`, `state/progress.json`, `state/directions_tried.json`, and `state/state_pack.md`.
2. Read `state/hypotheses.json` and `state/next_iteration.json` when present.
3. Pick a direction that differs from prior directions.
4. Record a prediction before running the experiment.
5. Make the smallest useful code/config change or run the smallest informative experiment.
6. Capture command output under `runs/<run_id>/`.
7. Parse metrics with `scripts/parse_metrics.py` when possible.
8. Compare actual metrics with the prediction and record any reasoning gap.
9. Append evidence-backed findings.
10. Record the iteration.
11. Build the next state pack.
12. If `stale_count >= 2`, pivot structurally.

## File Discipline

- Keep generated artifacts under the active task directory.
- Keep scripts standard-library only unless the task explicitly adds dependencies.
- Do not edit unrelated project files when updating the AutoResearch protocol.
