import unittest

from bleach.detectors import Span, detect_text, luhn_valid, merge_spans
from bleach.learned import LearnedValue
from bleach.masking import mask_value


class DetectorTests(unittest.TestCase):
    def test_detects_core_built_in_identifiers(self) -> None:
        text = (
            "SSN 123-45-6789 email Example@Comcast.NET EIN 12-3456789 "
            "ITIN 912-78-1234 PAN ABCDE1234F phone +1 415-555-1234"
        )

        spans = detect_text(text, profile="ai-share")
        kinds = {span.kind for span in spans}

        self.assertIn("SSN", kinds)
        self.assertIn("email", kinds)
        self.assertIn("EIN", kinds)
        self.assertIn("ITIN", kinds)
        self.assertIn("PAN", kinds)
        self.assertIn("phone", kinds)

    def test_credit_card_detection_requires_luhn(self) -> None:
        text = "valid 4111 1111 1111 1111 invalid 4111 1111 1111 1112"

        spans = detect_text(text, profile="ai-share")

        self.assertEqual([span.text for span in spans if span.kind == "card"], ["4111 1111 1111 1111"])
        self.assertTrue(luhn_valid("4111111111111111"))
        self.assertFalse(luhn_valid("4111111111111112"))

    def test_aadhaar_is_disabled_for_initial_profiles(self) -> None:
        spans = detect_text("aadhaar 1234 5678 9012", profile="ai-share")

        self.assertNotIn("Aadhaar", {span.kind for span in spans})

    def test_learned_values_are_detected_with_variants(self) -> None:
        learned = [
            LearnedValue(
                kind="SSN",
                value="123-45-6789",
                variants=("123456789",),
            )
        ]

        spans = detect_text("compact 123456789", profile="ai-share", learned_values=learned)

        self.assertEqual(spans, [Span(8, 17, "SSN", "123456789", 100)])

    def test_merge_spans_keeps_highest_priority_then_longest(self) -> None:
        spans = [
            Span(0, 10, "short-low", "0123456789", 10),
            Span(0, 5, "short-high", "01234", 100),
            Span(20, 24, "other", "abcd", 10),
        ]

        merged = merge_spans(spans)

        self.assertEqual([span.kind for span in merged], ["short-high", "other"])

    def test_ai_share_masks_full_value_by_type(self) -> None:
        self.assertEqual(mask_value("123-45-6789", "SSN", "ai-share"), "[REDACTED:SSN]")

    def test_cpa_share_keeps_last_four_digits(self) -> None:
        self.assertEqual(mask_value("123-45-6789", "SSN", "cpa-share"), "***-**-6789")

    def test_cpa_share_masks_email_without_full_local_part(self) -> None:
        self.assertEqual(
            mask_value("Example@Comcast.NET", "email", "cpa-share"),
            "E***@***.NET",
        )


if __name__ == "__main__":
    unittest.main()
