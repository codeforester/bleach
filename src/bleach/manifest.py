from __future__ import annotations

import hashlib
import json
from pathlib import Path

from bleach import __version__
from bleach.learned import LearnedValue


def source_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def config_hash(profile: str, learned_values: list[LearnedValue]) -> str:
    payload = {
        "profile": profile,
        "version": __version__,
        "learned": [
            {"kind": value.kind, "value": value.value, "variants": value.variants}
            for value in learned_values
        ],
    }
    encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class Manifest:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.records = self._load()

    def matches(self, *, source: Path, dest: Path, profile: str, learned_hash: str) -> bool:
        key = str(dest.resolve())
        record = self.records.get(key)
        if not record or not dest.exists():
            return False
        return record == {
            "source": str(source.resolve()),
            "source_hash": source_hash(source),
            "profile": profile,
            "config_hash": learned_hash,
            "version": __version__,
        }

    def update(self, *, source: Path, dest: Path, profile: str, learned_hash: str) -> None:
        self.records[str(dest.resolve())] = {
            "source": str(source.resolve()),
            "source_hash": source_hash(source),
            "profile": profile,
            "config_hash": learned_hash,
            "version": __version__,
        }

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self.records, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def _load(self) -> dict[str, dict[str, str]]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))
