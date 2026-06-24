from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from bleach.learned import LearnedValue


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    kind: str
    text: str
    score: int

    @property
    def length(self) -> int:
        return self.end - self.start


_BUILT_INS: tuple[tuple[str, re.Pattern[str], int], ...] = (
    ("email", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE), 90),
    ("SSN", re.compile(r"\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b"), 90),
    ("EIN", re.compile(r"\b\d{2}-\d{7}\b"), 80),
    ("ITIN", re.compile(r"\b9\d{2}-[78]\d-\d{4}\b"), 96),
    ("PAN", re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"), 80),
    ("phone", re.compile(r"\b(?:\+1[\s-]?)?(?:\(?\d{3}\)?[\s-]?)\d{3}[\s-]?\d{4}\b"), 50),
)

_CARD_CANDIDATE = re.compile(r"\b\d(?:[ -]?\d){12,18}\b")


def detect_text(
    text: str,
    *,
    profile: str,
    learned_values: Iterable[LearnedValue] = (),
) -> list[Span]:
    spans: list[Span] = []
    spans.extend(_detect_built_ins(text))
    spans.extend(_detect_cards(text))
    spans.extend(_detect_learned(text, learned_values))
    return merge_spans(spans)


def merge_spans(spans: Iterable[Span]) -> list[Span]:
    accepted: list[Span] = []
    for candidate in sorted(spans, key=lambda span: (-span.score, -span.length, span.start)):
        if any(_overlaps(candidate, existing) for existing in accepted):
            continue
        accepted.append(candidate)
    return sorted(accepted, key=lambda span: span.start)


def luhn_valid(digits: str) -> bool:
    if not digits.isdigit() or len(digits) < 13:
        return False
    total = 0
    reverse_digits = digits[::-1]
    for index, char in enumerate(reverse_digits):
        value = int(char)
        if index % 2 == 1:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return total % 10 == 0


def _detect_built_ins(text: str) -> list[Span]:
    spans: list[Span] = []
    for kind, pattern, score in _BUILT_INS:
        for match in pattern.finditer(text):
            spans.append(Span(match.start(), match.end(), kind, match.group(0), score))
    return spans


def _detect_cards(text: str) -> list[Span]:
    spans: list[Span] = []
    for match in _CARD_CANDIDATE.finditer(text):
        digits = re.sub(r"\D", "", match.group(0))
        if luhn_valid(digits):
            spans.append(Span(match.start(), match.end(), "card", match.group(0), 95))
    return spans


def _detect_learned(text: str, values: Iterable[LearnedValue]) -> list[Span]:
    spans: list[Span] = []
    for learned in values:
        needles = (learned.value, *learned.variants)
        for needle in dict.fromkeys(needles):
            if not needle:
                continue
            start = 0
            while True:
                index = text.find(needle, start)
                if index == -1:
                    break
                spans.append(Span(index, index + len(needle), learned.kind, needle, 100))
                start = index + len(needle)
    return spans


def _overlaps(left: Span, right: Span) -> bool:
    return left.start < right.end and right.start < left.end
