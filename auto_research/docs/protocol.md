# Protocol

This project adapts the public Deli_AutoResearch protocol into a local, scriptable experiment system.

Source: https://victorchen96.github.io/auto_research/framework.html

## Design Commitments

- State is persisted in files, not conversation memory.
- Each iteration should be reproducible from the task directory.
- Execution and evaluation are separated.
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

