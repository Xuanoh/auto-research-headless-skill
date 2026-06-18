#!/usr/bin/env python3
from __future__ import annotations

import argparse

from common import append_jsonl, read_json, require_task_dir, utc_now, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Update an AutoResearch task heartbeat.")
    parser.add_argument("task_dir")
    parser.add_argument("--source", default="worker")
    parser.add_argument("--event", default="alive")
    args = parser.parse_args()

    task_dir = require_task_dir(args.task_dir)
    heartbeat_path = task_dir / "state" / "heartbeat.json"
    heartbeat = read_json(heartbeat_path, {})
    heartbeat.update({"last_seen": utc_now(), "source": args.source, "event": args.event})
    write_json(heartbeat_path, heartbeat)
    append_jsonl(task_dir / "logs" / "heartbeat.jsonl", heartbeat)
    print(heartbeat["last_seen"])


if __name__ == "__main__":
    main()

