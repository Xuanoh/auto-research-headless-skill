#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from common import progress_path, read_json, require_task_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Report AutoResearch stale state.")
    parser.add_argument("task_dir")
    args = parser.parse_args()

    task_dir = require_task_dir(args.task_dir)
    progress = read_json(progress_path(task_dir), {})
    stale_count = int(progress.get("stale_count", 0))
    status = "ok"
    action = "continue"
    if stale_count >= 4:
        status = "needs_human_attention"
        action = "stop_and_report"
    elif stale_count >= 2:
        status = "pivoting"
        action = "structural_pivot"
    elif stale_count == 1:
        status = "watch"
        action = "continue_with_validation"

    print(json.dumps({"status": status, "action": action, "stale_count": stale_count}, indent=2))


if __name__ == "__main__":
    main()

