from __future__ import annotations

import argparse
from collections.abc import Sequence


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
    learn.set_defaults(handler=_not_implemented_yet)

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


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
