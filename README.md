# Auto Research Headless Skill

A Codex skill plus local scaffold for headless automatic experiment loops.

This repository adapts the public Deli_AutoResearch protocol into a concrete local workflow:

- a portable `SKILL.md`
- a project-level `auto_research/AGENTS.md`
- durable task state files
- standard-library Python scripts
- a reset demo task

Protocol reference: https://victorchen96.github.io/auto_research/framework.html

This is not the official Deli_AutoResearch repository. It is a local implementation scaffold intended for Codex-driven automatic experiments.

## What It Provides

```text
auto_research/
  AGENTS.md
  docs/
  scripts/
  templates/
  tasks/demo_basic_ts/
```

The loop is:

```text
direction -> hypothesis -> experiment -> metrics -> findings -> decision -> next iteration
```

## Use As A Codex Skill

Copy the root `SKILL.md` into your Codex skills directory, for example:

```bash
mkdir -p ~/.codex/skills/auto-research-headless
cp SKILL.md ~/.codex/skills/auto-research-headless/SKILL.md
```

Then copy `auto_research/` into the project where you want to run experiments.

## Initialize A New Task

```bash
python3 auto_research/scripts/init_task.py \
  --task-id basic_ts_etth1_norm \
  --title "BasicTS ETTh1 normalization study" \
  --objective "Explore normalization and training-strategy changes for BasicTS ETTh1 forecasting." \
  --success-criteria "Find a reproducible metric improvement or a well-evidenced negative result." \
  --workspace /path/to/workspace
```

Build the next iteration context:

```bash
python3 auto_research/scripts/build_state_pack.py auto_research/tasks/basic_ts_etth1_norm
```

## Validate The Scaffold

```bash
python3 -m py_compile auto_research/scripts/*.py
python3 auto_research/scripts/build_state_pack.py auto_research/tasks/demo_basic_ts
python3 auto_research/scripts/stale_detector.py auto_research/tasks/demo_basic_ts
```

## License

MIT
