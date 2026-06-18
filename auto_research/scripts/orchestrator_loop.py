#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

from common import append_jsonl, progress_path, read_json, require_task_dir, utc_now, write_json


def run_script(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)


def read_workspace(task_dir: Path) -> Path:
    spec = (task_dir / "state" / "task_spec.md").read_text(encoding="utf-8")
    marker = "## Workspace"
    if marker not in spec:
        return Path.cwd()
    after = spec.split(marker, 1)[1].strip().splitlines()
    for line in after:
        value = line.strip()
        if value and not value.startswith("#"):
            return Path(value).expanduser().resolve()
    return Path.cwd()


def build_prompt(task_dir: Path, plan: dict) -> str:
    state_pack = task_dir / "state" / "state_pack.md"
    pack_text = state_pack.read_text(encoding="utf-8") if state_pack.exists() else ""
    return f"""You are running one bounded AutoResearch iteration.

Task directory: {task_dir}
Planned direction: {json.dumps(plan, ensure_ascii=False)}

Use the local AutoResearch protocol:
- update heartbeat at start and finish
- read state/task_spec.md, progress.json, findings.jsonl, directions_tried.json, hypotheses.json, state_pack.md
- run the smallest informative experiment
- store command runs under runs/ when possible using auto_research/scripts/run_experiment.py
- parse metrics with auto_research/scripts/parse_metrics.py when possible
- append evidence-backed findings with auto_research/scripts/append_finding.py
- record the iteration with auto_research/scripts/record_iteration.py
- rebuild state/state_pack.md before stopping
- do not ask the user; stop after one iteration

Curated state pack:

{pack_text}
"""


def codex_exec(codex_bin: str, workspace: Path, prompt: str, run_dir: Path, sandbox: str) -> int:
    final_path = run_dir / "codex-final.md"
    stdout_path = run_dir / "codex-events.jsonl"
    stderr_path = run_dir / "codex-stderr.log"
    args = [
        codex_bin,
        "--ask-for-approval",
        "never",
        "exec",
        "--json",
        "--cd",
        str(workspace),
        "--sandbox",
        sandbox,
        "--output-last-message",
        str(final_path),
        prompt,
    ]
    proc = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)
    stdout_path.write_text(proc.stdout, encoding="utf-8")
    stderr_path.write_text(proc.stderr, encoding="utf-8")
    return proc.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a continuous insight-driven AutoResearch loop.")
    parser.add_argument("task_dir")
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--sandbox", choices=["read-only", "workspace-write"], default="workspace-write")
    parser.add_argument("--dry-run", action="store_true", help="Generate prompts and plans without invoking Codex.")
    args = parser.parse_args()

    task_dir = require_task_dir(args.task_dir)
    repo_root = Path.cwd()
    workspace = read_workspace(task_dir)

    for _ in range(args.rounds):
        progress = read_json(progress_path(task_dir), {})
        if progress.get("needs_human_attention") or progress.get("status") == "completed":
            break
        if int(progress.get("iteration", 0)) >= int(progress.get("budget_rounds", args.rounds)):
            progress["status"] = "completed"
            write_json(progress_path(task_dir), progress)
            break

        run_script(["python3", "auto_research/scripts/heartbeat.py", str(task_dir), "--source", "orchestrator", "--event", "round_start"], repo_root)
        run_script(["python3", "auto_research/scripts/build_state_pack.py", str(task_dir)], repo_root)
        plan_result = run_script(["python3", "auto_research/scripts/plan_next_iteration.py", str(task_dir)], repo_root)
        plan = json.loads(plan_result.stdout)
        run_dir = task_dir / "runs" / f"orchestrator_{utc_now().replace(':', '').replace('.', '_')}"
        run_dir.mkdir(parents=True, exist_ok=True)
        prompt = build_prompt(task_dir, plan)
        (run_dir / "iteration-prompt.md").write_text(prompt, encoding="utf-8")

        append_jsonl(task_dir / "logs" / "orchestrator.jsonl", {"ts": utc_now(), "event": "planned_iteration", "detail": plan})
        if not args.dry_run:
            exit_code = codex_exec(args.codex_bin, workspace, prompt, run_dir, args.sandbox)
            append_jsonl(task_dir / "logs" / "orchestrator.jsonl", {"ts": utc_now(), "event": "codex_exec_finished", "exit_code": exit_code, "run_dir": str(run_dir)})
        else:
            append_jsonl(task_dir / "logs" / "orchestrator.jsonl", {"ts": utc_now(), "event": "dry_run_prompt_written", "run_dir": str(run_dir)})

        run_script(["python3", "auto_research/scripts/stale_detector.py", str(task_dir)], repo_root)
        run_script(["python3", "auto_research/scripts/heartbeat.py", str(task_dir), "--source", "orchestrator", "--event", "round_finish"], repo_root)
        time.sleep(1)


if __name__ == "__main__":
    main()

