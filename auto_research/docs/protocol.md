# Protocol

This project adapts the public Deli_AutoResearch protocol into a local, scriptable experiment system.

Source: https://victorchen96.github.io/auto_research/framework.html

## Design Commitments

- State is persisted in files, not conversation memory.
- Each iteration should be reproducible from the task directory.
- Execution and evaluation are separated.
- Each experiment starts with a recorded prediction and ends with a prediction-vs-result comparison.
- Stale detection is mechanical.
- Pivoting changes a structural constraint, not just a tactical parameter.
- Heartbeats make long runs observable.

## State Machine

```text
idle
  -> planning
  -> running
  -> analyzing
  -> completed

failure and loop branches:
  running -> failed -> planning
  analyzing -> stale -> pivoting -> planning
  stale_count >= 4 -> needs_human_attention
```

## Insight-To-Loop Mode

Insight-to-loop mode treats the user's insight as a seed, not a one-off prompt.

```text
insight
  -> task_spec.md
  -> hypotheses.json
  -> next_iteration.json
  -> fresh Codex iteration
  -> predictions.jsonl
  -> benchmark metrics
  -> reflections.jsonl
  -> findings.jsonl
  -> progress.json
  -> continue or structural pivot
```

The loop driver is `scripts/orchestrator_loop.py`. It does not replace Codex's research judgment; it supplies the durable state machine and fresh-session scheduling.

## Prediction-Calibrated Iterations

Before running a benchmark, the worker records a prediction with `scripts/record_prediction.py`.

The prediction should include the expected metric direction or value, confidence, rationale, and likely failure modes. After parsing metrics, the worker runs `scripts/compare_prediction.py` to classify the result as matched, mismatched, or uncertain.

When the result disagrees with the prediction, record the reasoning gap and a reusable lesson. These lessons are stored in `state/reasoning_patterns.json` and surfaced in the next `state_pack.md`, so the loop learns better research heuristics over time.

## Stale Rules

An iteration is stale when:

- it creates zero new findings, or
- the primary metric gets worse, or
- the run fails without producing useful evidence.

Effects:

- stale iteration: `stale_count += 1`
- useful iteration: `stale_count = 0`
- `stale_count >= 2`: pivot structurally
- `stale_count >= 4`: flag human attention

## Structural Pivot Axes

- data: normalization, split, leakage, sampling, missingness
- objective: loss, horizon weighting, metric definition
- model: architecture family, inductive bias, baseline choice
- training: optimizer, schedule, curriculum, seed protocol
- evaluation: benchmark subset, aggregation, statistical confidence
- environment: dependency, GPU memory, cache, version mismatch
- code: runner/config refactor, nondeterminism, instrumentation
