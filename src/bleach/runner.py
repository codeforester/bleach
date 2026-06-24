from __future__ import annotations

from pathlib import Path

from bleach.learned import load_learned_values
from bleach.manifest import Manifest, config_hash
from bleach.processors import process_file, verify_file
from bleach.reporting import Record, write_report
from bleach.walker import Job, build_jobs


def redact(
    *,
    inputs: list[str],
    output_dir: str,
    profile: str,
    force: bool = False,
    silent: bool = False,
    report: str | None = None,
) -> int:
    profile_root = Path(output_dir) / profile
    learned_values = load_learned_values(profile)
    learned_hash = config_hash(profile, learned_values)
    manifest = Manifest(profile_root / ".bleach-manifest.json")
    records: list[Record] = []

    jobs = build_jobs([Path(item) for item in inputs], Path(output_dir), profile)
    for job in jobs:
        record = _run_job(
            job,
            profile=profile,
            learned_values=learned_values,
            learned_hash=learned_hash,
            manifest=manifest,
            force=force,
            silent=silent,
        )
        records.append(record)

    manifest.save()
    if report:
        write_report(Path(report), records)
    return 1 if any(record.status == "failed" for record in records) else 0


def _run_job(
    job: Job,
    *,
    profile: str,
    learned_values,
    learned_hash: str,
    manifest: Manifest,
    force: bool,
    silent: bool,
) -> Record:
    if job.error:
        if not silent:
            print(f"{job.source}: {job.error}")
        return Record(str(job.source), str(job.dest), profile, "failed", error=job.error)

    if not force and manifest.matches(
        source=job.source,
        dest=job.dest,
        profile=profile,
        learned_hash=learned_hash,
    ):
        if not silent:
            print(f"{job.source}: skipped existing output")
        return Record(str(job.source), str(job.dest), profile, "skipped")

    try:
        counts = process_file(job.source, job.dest, profile=profile, learned_values=learned_values)
        residual = verify_file(job.dest, profile=profile, learned_values=learned_values)
    except (OSError, UnicodeError, ValueError) as exc:
        message = str(exc) or exc.__class__.__name__
        if not silent:
            print(f"{job.source}: {message}")
        return Record(str(job.source), str(job.dest), profile, "failed", error=message)

    if residual:
        if not silent:
            print(f"{job.source}: verification failed")
        return Record(str(job.source), str(job.dest), profile, "failed", counts, "verification failed")

    manifest.update(source=job.source, dest=job.dest, profile=profile, learned_hash=learned_hash)
    if not silent:
        print(f"{job.source}: redacted")
    return Record(str(job.source), str(job.dest), profile, "redacted", counts)
