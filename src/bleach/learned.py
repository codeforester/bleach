from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class LearnedValue:
    kind: str
    value: str
    variants: tuple[str, ...] = ()


def default_bleach_home() -> Path:
    override = os.environ.get("BLEACH_HOME")
    if override:
        return Path(override)
    return Path.home() / ".base.d" / "bleach"


def learned_profile_path(profile: str, home: Path | None = None) -> Path:
    root = home if home is not None else default_bleach_home()
    return root / "profiles" / profile / "learned.json"


def parse_pii_file(path: Path) -> list[LearnedValue]:
    values: list[LearnedValue] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"invalid PII entry on line {line_number}: expected 'key: value'")
        kind, value = line.split(":", 1)
        kind = kind.strip()
        value = value.strip()
        if not kind or not value:
            raise ValueError(f"invalid PII entry on line {line_number}: empty key or value")
        values.append(LearnedValue(kind=kind, value=value, variants=_variants_for(kind, value)))
    if not values:
        raise ValueError("PII file did not contain any values")
    return values


def save_learned_profile(profile: str, pii_file: Path, home: Path | None = None) -> Path:
    values = parse_pii_file(pii_file)
    path = learned_profile_path(profile, home)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.parent.chmod(0o700)

    payload = {
        "schema_version": 1,
        "profile": profile,
        "values": [asdict(value) for value in values],
    }

    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
    ) as handle:
        temp_path = Path(handle.name)
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")

    temp_path.chmod(0o600)
    temp_path.replace(path)
    path.chmod(0o600)
    return path


def load_learned_values(profile: str, home: Path | None = None) -> list[LearnedValue]:
    path = learned_profile_path(profile, home)
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [
        LearnedValue(
            kind=item["kind"],
            value=item["value"],
            variants=tuple(item.get("variants", ())),
        )
        for item in payload.get("values", [])
    ]


def _variants_for(kind: str, value: str) -> tuple[str, ...]:
    variants: list[str] = []
    compact = re.sub(r"[\s-]", "", value)
    if compact != value and compact:
        variants.append(compact)
    lowercase = value.lower()
    if lowercase != value and "email" in kind.lower():
        variants.append(lowercase)
    return tuple(dict.fromkeys(variants))
