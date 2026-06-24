from __future__ import annotations

import re


def mask_value(value: str, kind: str, profile: str) -> str:
    if profile == "ai-share":
        return f"[REDACTED:{kind}]"
    if kind == "email" and "@" in value:
        return _mask_email(value)
    return _mask_keep_last_digits(value, keep=4)


def _mask_email(value: str) -> str:
    local, domain = value.split("@", 1)
    first = local[:1] or "*"
    if "." in domain:
        _name, suffix = domain.rsplit(".", 1)
        return f"{first}***@***.{suffix}"
    return f"{first}***@***"


def _mask_keep_last_digits(value: str, *, keep: int) -> str:
    digit_positions = [match.start() for match in re.finditer(r"\d", value)]
    visible = set(digit_positions[-keep:])
    chars: list[str] = []
    for index, char in enumerate(value):
        if char.isdigit() and index not in visible:
            chars.append("*")
        else:
            chars.append(char)
    return "".join(chars)
