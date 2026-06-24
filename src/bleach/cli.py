from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from bleach.learned import save_learned_profile


SUPPORTED_PROFILES = ("ai-share", "cpa-share")


class BleachArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        if "invalid choice" in message and "--profile" in message:
            message = f"unsupported profile; choose one of: {', '.join(SUPPORTED_PROFILES)}"
        super().error(message)


def build_parser() -> argparse.ArgumentParser:
    parser = BleachArgumentParser(
        prog="bleach",
        description="Local offline PII redaction CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    learn = subparsers.add_parser("learn", help="Persist learned PII for a profile.")
    _add_profile_argument(learn)
    learn.add_argument("--pii-file", required=True, help="Path to key-value PII file.")
    learn.set_defaults(handler=_handle_learn)

    redact = subparsers.add_parser("redact", help="Redact supported input files.")
    _add_profile_argument(redact)
    redact.add_argument("inputs", metavar="INPUT", nargs="+", help="Files or directories.")
    redact.add_argument("-o", "--output-dir", required=True, help="Output directory.")
    redact.add_argument("--force", action="store_true", help="Reprocess existing outputs.")
    redact.add_argument("--silent", action="store_true", help="Suppress ordinary INFO output.")
    redact.set_defaults(handler=_not_implemented_yet)

    verify = subparsers.add_parser("verify", help="Verify files are already redacted.")
    _add_profile_argument(verify)
    verify.add_argument("inputs", metavar="INPUT", nargs="+", help="Files or directories.")
    verify.set_defaults(handler=_not_implemented_yet)

    return parser


def _add_profile_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--profile",
        required=True,
        choices=SUPPORTED_PROFILES,
        help="Redaction profile.",
    )


def _not_implemented_yet(_args: argparse.Namespace) -> int:
    return 0


def _handle_learn(args: argparse.Namespace) -> int:
    try:
        save_learned_profile(args.profile, Path(args.pii_file))
    except OSError as exc:
        print(f"bleach: failed to learn PII values: {exc.strerror}", flush=True)
        return 1
    except ValueError as exc:
        print(f"bleach: failed to learn PII values: {exc}", flush=True)
        return 1
    print("learned 1 value" if _learned_count(args.profile) == 1 else f"learned {_learned_count(args.profile)} values")
    return 0


def _learned_count(profile: str) -> int:
    from bleach.learned import load_learned_values

    return len(load_learned_values(profile))


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
