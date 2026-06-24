import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

from bleach.learned import (
    LearnedValue,
    learned_profile_path,
    load_learned_values,
    parse_pii_file,
    save_learned_profile,
)


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin" / "bleach"


class LearnedProfileTests(unittest.TestCase):
    def test_parse_pii_file_normalizes_obvious_variants(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            pii_file = Path(temp) / "pii.txt"
            pii_file.write_text(
                "SSN: 123-45-6789\nemail: Example@Comcast.NET\n",
                encoding="utf-8",
            )

            values = parse_pii_file(pii_file)

        self.assertEqual(
            values,
            [
                LearnedValue(kind="SSN", value="123-45-6789", variants=("123456789",)),
                LearnedValue(kind="email", value="Example@Comcast.NET", variants=("example@comcast.net",)),
            ],
        )

    def test_save_learned_profile_writes_owner_only_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            pii_file = home / "pii.txt"
            pii_file.write_text("SSN: 123-45-6789\n", encoding="utf-8")

            path = save_learned_profile("ai-share", pii_file, home)

            self.assertEqual(path, learned_profile_path("ai-share", home))
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(path.parent.stat().st_mode), 0o700)
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["profile"], "ai-share")
            self.assertEqual(payload["values"][0]["kind"], "SSN")
            self.assertEqual(payload["values"][0]["value"], "123-45-6789")

    def test_successful_learn_replaces_previous_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            old_file = home / "old.txt"
            new_file = home / "new.txt"
            old_file.write_text("SSN: 123-45-6789\n", encoding="utf-8")
            new_file.write_text("email: example@comcast.net\n", encoding="utf-8")

            save_learned_profile("ai-share", old_file, home)
            save_learned_profile("ai-share", new_file, home)

            values = load_learned_values("ai-share", home)

        self.assertEqual([value.kind for value in values], ["email"])
        self.assertEqual(values[0].value, "example@comcast.net")

    def test_failed_learn_preserves_previous_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            old_file = home / "old.txt"
            bad_file = home / "bad.txt"
            old_file.write_text("SSN: 123-45-6789\n", encoding="utf-8")
            bad_file.write_text("this is not a key value file\n", encoding="utf-8")
            save_learned_profile("ai-share", old_file, home)

            with self.assertRaises(ValueError):
                save_learned_profile("ai-share", bad_file, home)

            values = load_learned_values("ai-share", home)

        self.assertEqual(values[0].value, "123-45-6789")

    def test_learn_cli_uses_bleach_home_override(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp) / "state"
            pii_file = Path(temp) / "pii.txt"
            pii_file.write_text("SSN: 123-45-6789\n", encoding="utf-8")

            result = subprocess.run(
                [str(BIN), "learn", "--profile", "ai-share", "--pii-file", str(pii_file)],
                cwd=ROOT,
                env={**os.environ, "BLEACH_HOME": str(home)},
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            values = load_learned_values("ai-share", home)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("learned 1 value", result.stdout)
        self.assertEqual(values[0].value, "123-45-6789")


if __name__ == "__main__":
    unittest.main()
