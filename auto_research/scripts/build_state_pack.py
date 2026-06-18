#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from common import directions_path, findings_path, progress_path, read_json, read_jsonl, require_task_dir, utc_now


def main() -> None:
    parser = argparse.ArgumentParser(description="Build curated state_pack.md for the next AutoResearch iteration.")
    parser.add_argument("task_dir")
    args = parser.parse_args()

    task_dir = require_task_dir(args.task_dir)
    task_spec = (task_dir / "state" / "task_spec.md").read_text(encoding="utf-8")
    progress = read_json(progress_path(task_dir), {})
    directions = read_json(directions_path(task_dir), {"directions": []})
    findings = read_jsonl(findings_path(task_dir))
    latest_findings = findings[-20:]

    pack = [
        "# AutoResearch State Pack",
        "",
        f"Generated: {utc_now()}",
        "",
        "## Task Spec",
        "",
        task_spec.strip(),
        "",
        "## Progress",
        "",
        "```json",
        json.dumps(progress, indent=2, ensure_ascii=False),
        "```",
        "",
        "## Directions Tried",
        "",
        "```json",
        json.dumps(directions, indent=2, ensure_ascii=False),
        "```",
        "",
        "## Latest Findings",
        "",
    ]

    if latest_findings:
        for finding in latest_findings:
            pack.append(f"- {json.dumps(finding, ensure_ascii=False)}")
    else:
        pack.append("- No findings recorded yet.")

    pack.extend(
        [
            "",
            "## Next Iteration Contract",
            "",
            "- Start fresh; do not rely on conversation history.",
            "- Choose a direction that differs from prior directions.",
            "- Run the smallest informative experiment.",
            "- Record evidence-backed findings.",
            "- Update progress and iteration log before stopping.",
            "- Pivot structurally if stale_count >= 2.",
            "",
        ]
    )

    out = task_dir / "state" / "state_pack.md"
    out.write_text("\n".join(pack), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()

