#!/usr/bin/env python3
from __future__ import annotations

import argparse

from common import append_jsonl, findings_path, read_jsonl, require_task_dir, utc_now


def main() -> None:
    parser = argparse.ArgumentParser(description="Append an evidence-backed finding.")
    parser.add_argument("task_dir")
    parser.add_argument("--type", default="observation")
    parser.add_argument("--claim", required=True)
    parser.add_argument("--evidence", action="append", default=[])
    parser.add_argument("--confidence", type=float, default=0.5)
    parser.add_argument("--run-id")
    args = parser.parse_args()

    task_dir = require_task_dir(args.task_dir)
    index = len(read_jsonl(findings_path(task_dir))) + 1
    finding = {
        "finding_id": f"f_{index:04d}",
        "ts": utc_now(),
        "type": args.type,
        "claim": args.claim,
        "evidence": args.evidence,
        "confidence": args.confidence,
        "run_id": args.run_id,
        "verification_status": "unverified",
    }
    append_jsonl(findings_path(task_dir), finding)
    print(finding["finding_id"])


if __name__ == "__main__":
    main()

