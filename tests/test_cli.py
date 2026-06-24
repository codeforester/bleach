import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin" / "bleach"


class CliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(BIN), *args],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_help_lists_mvp_subcommands(self) -> None:
        result = self.run_cli("--help")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("learn", result.stdout)
        self.assertIn("redact", result.stdout)
        self.assertIn("verify", result.stdout)

    def test_redact_requires_profile(self) -> None:
        result = self.run_cli("redact", "input.txt", "--output-dir", "out")

        self.assertEqual(result.returncode, 2)
        self.assertIn("--profile", result.stderr)

    def test_rejects_unknown_profile(self) -> None:
        result = self.run_cli(
            "redact",
            "--profile",
            "casual",
            "input.txt",
            "--output-dir",
            "out",
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("unsupported profile", result.stderr)

    def test_learn_requires_pii_file(self) -> None:
        result = self.run_cli("learn", "--profile", "ai-share")

        self.assertEqual(result.returncode, 2)
        self.assertIn("--pii-file", result.stderr)

    def test_verify_requires_input(self) -> None:
        result = self.run_cli("verify", "--profile", "ai-share")

        self.assertEqual(result.returncode, 2)
        self.assertIn("INPUT", result.stderr)


if __name__ == "__main__":
    unittest.main()
