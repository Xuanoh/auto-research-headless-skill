# Validation

The initial scaffold was validated with Python 3.11.

Checks performed:

```bash
python3 -m py_compile auto_research/scripts/*.py
python3 auto_research/scripts/init_from_insight.py --root /tmp/ar_tasks --task-id insight_smoke --insight "Normalization may affect long-horizon forecasting robustness." --workspace /tmp --budget-rounds 2 --budget-hours 1
python3 auto_research/scripts/record_prediction.py /tmp/ar_tasks/insight_smoke --direction-id dir_001_data --hypothesis "Normalization should reduce validation MAE." --prediction "val/mae should improve relative to the baseline." --metric-name val/mae --expected-direction improve --confidence 0.6 --rationale "Scale variance should be reduced before training."
python3 auto_research/scripts/compare_prediction.py /tmp/ar_tasks/insight_smoke --prediction-id pred_0001 --metric-name val/mae --actual-value 0.48 --baseline-value 0.45 --metric-mode min --reasoning-gap "Assumed scale variance dominated, but the change likely disrupted horizon-specific calibration." --lesson "When normalization predictions fail, separate scale effects from horizon-specific calibration before pivoting."
python3 auto_research/scripts/orchestrator_loop.py /tmp/ar_tasks/insight_smoke --rounds 1 --dry-run
python3 auto_research/scripts/build_state_pack.py auto_research/tasks/demo_basic_ts
python3 auto_research/scripts/run_experiment.py auto_research/tasks/demo_basic_ts --name metric_smoke --cwd /path/to/workspace -- python3 -c 'print("{\"metric\":\"val/mae\",\"value\":0.42}")'
python3 auto_research/scripts/parse_metrics.py auto_research/tasks/demo_basic_ts/runs/<run_id>
python3 auto_research/scripts/append_finding.py auto_research/tasks/demo_basic_ts --type metric --claim "Demo smoke run produced val/mae=0.42 from stdout JSON." --evidence auto_research/tasks/demo_basic_ts/runs/<run_id>/metrics.parsed.jsonl --confidence 0.9 --run-id <run_id>
python3 auto_research/scripts/record_iteration.py auto_research/tasks/demo_basic_ts --decision continue --direction-id dir_001 --direction "Validate protocol machinery with smoke metric parsing." --summary "Smoke experiment produced a parsed metric and validated the local run/parse/record loop." --new-findings 1 --metric-name val/mae --metric-value 0.42 --metric-mode min --run-id <run_id> --prediction-id pred_0001 --prediction-match yes
python3 auto_research/scripts/stale_detector.py auto_research/tasks/demo_basic_ts
```

Prediction calibration was also smoke-tested with a deliberate mismatch. The mismatch wrote one row to `reflections.jsonl`, added a reusable failure lesson to `reasoning_patterns.json`, and surfaced both in the next `state_pack.md` and dry-run iteration prompt.

Expected stale detector output:

```json
{
  "status": "ok",
  "action": "continue",
  "stale_count": 0
}
```

The demo task committed in this scaffold is reset to iteration 0 so it remains a clean starter task.
