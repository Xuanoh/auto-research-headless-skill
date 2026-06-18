# Validation

The initial scaffold was validated with Python 3.11.

Checks performed:

```bash
python3 -m py_compile auto_research/scripts/*.py
python3 auto_research/scripts/init_from_insight.py --root /tmp/ar_tasks --task-id insight_smoke --insight "Normalization may affect long-horizon forecasting robustness." --workspace /tmp --budget-rounds 2 --budget-hours 1
python3 auto_research/scripts/orchestrator_loop.py /tmp/ar_tasks/insight_smoke --rounds 1 --dry-run
python3 auto_research/scripts/build_state_pack.py auto_research/tasks/demo_basic_ts
python3 auto_research/scripts/run_experiment.py auto_research/tasks/demo_basic_ts --name metric_smoke --cwd /path/to/workspace -- python3 -c 'print("{\"metric\":\"val/mae\",\"value\":0.42}")'
python3 auto_research/scripts/parse_metrics.py auto_research/tasks/demo_basic_ts/runs/<run_id>
python3 auto_research/scripts/append_finding.py auto_research/tasks/demo_basic_ts --type metric --claim "Demo smoke run produced val/mae=0.42 from stdout JSON." --evidence auto_research/tasks/demo_basic_ts/runs/<run_id>/metrics.parsed.jsonl --confidence 0.9 --run-id <run_id>
python3 auto_research/scripts/record_iteration.py auto_research/tasks/demo_basic_ts --decision continue --direction-id dir_001 --direction "Validate protocol machinery with smoke metric parsing." --summary "Smoke experiment produced a parsed metric and validated the local run/parse/record loop." --new-findings 1 --metric-name val/mae --metric-value 0.42 --metric-mode min --run-id <run_id>
python3 auto_research/scripts/stale_detector.py auto_research/tasks/demo_basic_ts
```

Expected stale detector output:

```json
{
  "status": "ok",
  "action": "continue",
  "stale_count": 0
}
```

The demo task committed in this scaffold is reset to iteration 0 so it remains a clean starter task.
