#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from common import append_jsonl, log_line, require_task_dir, utc_now


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a command as an AutoResearch experiment.")
    parser.add_argument("task_dir")
    parser.add_argument("--name", default="experiment")
    parser.add_argument("--cwd", default=".")
    parser.add_argument("--timeout-sec", type=int, default=0)
    args, command = parser.parse_known_args()

    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise SystemExit("Command is required after --")

    task_dir = require_task_dir(args.task_dir)
    run_id = f"run_{utc_now().replace(':', '').replace('.', '_')}"
    run_dir = task_dir / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "run_id": run_id,
        "name": args.name,
        "task_dir": str(task_dir),
        "cwd": str(Path(args.cwd).resolve()),
        "command": command,
        "started_at": utc_now(),
        "status": "running",
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    log_line(task_dir, "work", "info", "run_started", manifest)

    env = os.environ.copy()
    env["AUTO_RESEARCH_RUN_ID"] = run_id
    env["AUTO_RESEARCH_RUN_DIR"] = str(run_dir)

    with (run_dir / "stdout.log").open("w", encoding="utf-8") as stdout_file, (run_dir / "stderr.log").open(
        "w", encoding="utf-8"
    ) as stderr_file:
        try:
            proc = subprocess.run(
                command,
                cwd=args.cwd,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=args.timeout_sec if args.timeout_sec > 0 else None,
            )
            stdout_file.write(proc.stdout)
            stderr_file.write(proc.stderr)
            exit_code = proc.returncode
            status = "completed" if exit_code == 0 else "failed"
        except subprocess.TimeoutExpired as exc:
            stdout_file.write(exc.stdout or "")
            stderr_file.write(exc.stderr or "")
            exit_code = None
            status = "timeout"

    manifest.update({"ended_at": utc_now(), "status": status, "exit_code": exit_code})
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    append_jsonl(task_dir / "logs" / "work.jsonl", {"ts": utc_now(), "source": "work", "level": "info", "event": "run_finished", "detail": manifest})
    print(run_dir)
    if status != "completed":
        sys.exit(1)


if __name__ == "__main__":
    main()
