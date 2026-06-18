You are running one bounded AutoResearch iteration.

Read:

- `state/task_spec.md`
- `state/progress.json`
- `state/findings.jsonl`
- `state/directions_tried.json`
- `state/state_pack.md`

Rules:

- Do not rely on chat history.
- Do not ask the user during this iteration.
- Choose a direction that differs from previous directions.
- Run the smallest informative experiment or code/config change.
- Persist every result under this task directory.
- Append findings to `state/findings.jsonl`.
- Record the iteration with `scripts/record_iteration.py`.
- Rebuild `state/state_pack.md` before stopping.

Completion:

- Stop after one iteration.
- Report the files changed, run ids, findings, metrics, and next recommended state.

