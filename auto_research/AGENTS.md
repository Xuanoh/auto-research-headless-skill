# Auto Research Agent Instructions

When working under `auto_research/`, follow this headless AutoResearch protocol.

## Non-Negotiable Rules

- Persist progress to task files. Do not rely on chat history.
- Run one bounded iteration at a time.
- Start from `state/state_pack.md` when it exists; otherwise build it with `scripts/build_state_pack.py`.
- Write findings to `state/findings.jsonl`.
- Write iteration outcomes to `state/iteration_log.jsonl` through `scripts/record_iteration.py`.
- Update heartbeat before and after long work with `scripts/heartbeat.py`.
- Run validation between iterations when the workspace supports it.
- Prefer structural pivots after repeated stalls.
- Do not ask the user during an active run unless the task is blocked by an external dependency or unsafe action.

## Iteration Loop

1. Read `state/task_spec.md`, `state/progress.json`, `state/directions_tried.json`, and `state/state_pack.md`.
2. Pick a direction that differs from prior directions.
3. Make the smallest useful code/config change or run the smallest informative experiment.
4. Capture command output under `runs/<run_id>/`.
5. Parse metrics with `scripts/parse_metrics.py` when possible.
6. Append evidence-backed findings.
7. Record the iteration.
8. Build the next state pack.
9. If `stale_count >= 2`, pivot structurally.

## File Discipline

- Keep generated artifacts under the active task directory.
- Keep scripts standard-library only unless the task explicitly adds dependencies.
- Do not edit unrelated project files when updating the AutoResearch protocol.

