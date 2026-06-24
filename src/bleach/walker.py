from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from bleach.processors import SUPPORTED_EXTENSIONS


@dataclass(frozen=True)
class Job:
    source: Path
    dest: Path
    error: str = ""


def build_jobs(inputs: list[Path], output_dir: Path, profile: str) -> list[Job]:
    output_root = output_dir.resolve()
    profile_root = output_root / profile
    _validate_inputs(inputs, output_root)

    jobs: list[Job] = []
    seen: set[Path] = set()
    for input_path in inputs:
        resolved = input_path.resolve()
        if resolved.is_file():
            _add_job(jobs, seen, resolved, profile_root / resolved.name)
        elif resolved.is_dir():
            for source in sorted(resolved.rglob("*")):
                if source.is_symlink() or not source.is_file():
                    continue
                dest = profile_root / resolved.name / source.relative_to(resolved)
                _add_job(jobs, seen, source, dest)
        else:
            raise ValueError(f"input does not exist: {input_path}")
    return jobs


def _validate_inputs(inputs: list[Path], output_root: Path) -> None:
    for input_path in inputs:
        resolved = input_path.resolve()
        if not resolved.exists():
            raise ValueError(f"input does not exist: {input_path}")
        if resolved.is_dir() and output_root.is_relative_to(resolved):
            raise ValueError("output directory must not be inside an input directory")


def _add_job(jobs: list[Job], seen: set[Path], source: Path, dest: Path) -> None:
    resolved_dest = dest.resolve()
    if resolved_dest in seen:
        raise ValueError(f"output collision: {dest}")
    seen.add(resolved_dest)
    if source.suffix.lower() not in SUPPORTED_EXTENSIONS:
        jobs.append(Job(source, dest, "unsupported file type"))
    else:
        jobs.append(Job(source, dest))
