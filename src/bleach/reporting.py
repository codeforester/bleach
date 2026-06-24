from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Record:
    source: str
    dest: str
    profile: str
    status: str
    detections: dict[str, int] = field(default_factory=dict)
    error: str = ""


def write_report(path: Path, records: list[Record]) -> None:
    payload = {
        "records": [asdict(record) for record in records],
        "totals": _totals(records),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _totals(records: list[Record]) -> dict[str, int]:
    totals = {
        "redacted": 0,
        "skipped": 0,
        "failed": 0,
    }
    for record in records:
        if record.status in totals:
            totals[record.status] += 1
    return totals
