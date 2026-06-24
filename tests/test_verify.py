import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin" / "bleach"


class VerifyTests(unittest.TestCase):
    def run_bleach(self, *args: str, bleach_home: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(BIN), *args],
            cwd=ROOT,
            env={**os.environ, "BLEACH_HOME": str(bleach_home)},
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_verify_clean_file_returns_zero(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            clean = root / "clean.txt"
            clean.write_text("SSN [REDACTED:SSN]\n", encoding="utf-8")

            result = self.run_bleach(
                "verify",
                "--profile",
                "ai-share",
                str(clean),
                bleach_home=root / "state",
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("verified", result.stdout)

    def test_verify_dirty_file_returns_one_without_raw_pii(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            dirty = root / "dirty.txt"
            dirty.write_text("SSN 123-45-6789\n", encoding="utf-8")

            result = self.run_bleach(
                "verify",
                "--profile",
                "ai-share",
                str(dirty),
                bleach_home=root / "state",
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("residual sensitive data", result.stdout)
        self.assertNotIn("123-45-6789", result.stdout)
        self.assertNotIn("123-45-6789", result.stderr)

    def test_verify_directory_checks_nested_supported_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            docs = root / "docs"
            docs.mkdir()
            (docs / "a.txt").write_text("clean\n", encoding="utf-8")
            (docs / "b.md").write_text("email person@example.com\n", encoding="utf-8")

            result = self.run_bleach(
                "verify",
                "--profile",
                "ai-share",
                str(docs),
                bleach_home=root / "state",
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("residual sensitive data", result.stdout)

    def test_verify_unsupported_file_is_per_file_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            image = root / "photo.jpg"
            image.write_bytes(b"fake")

            result = self.run_bleach(
                "verify",
                "--profile",
                "ai-share",
                str(image),
                bleach_home=root / "state",
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("unsupported file type", result.stdout)


if __name__ == "__main__":
    unittest.main()
