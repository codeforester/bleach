import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin" / "bleach"


class TextRunnerTests(unittest.TestCase):
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

    def test_redact_single_text_file_under_profile_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "tax.txt"
            out = root / "out"
            report = root / "report.json"
            source.write_text("SSN 123-45-6789\n", encoding="utf-8")

            result = self.run_bleach(
                "redact",
                "--profile",
                "ai-share",
                str(source),
                "--output-dir",
                str(out),
                "--report",
                str(report),
                bleach_home=root / "state",
            )

            dest = out / "ai-share" / "tax.txt"
            payload = json.loads(report.read_text(encoding="utf-8"))
            redacted = dest.read_text(encoding="utf-8")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(redacted, "SSN [REDACTED:SSN]\n")
        self.assertEqual(payload["records"][0]["status"], "redacted")
        self.assertEqual(payload["records"][0]["detections"]["SSN"], 1)

    def test_directory_input_preserves_structure_under_profile_and_dir_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            docs = root / "docs2024"
            nested = docs / "nested"
            nested.mkdir(parents=True)
            source = nested / "data.csv"
            out = root / "out"
            source.write_text("name,ssn\nAda,123-45-6789\n", encoding="utf-8")

            result = self.run_bleach(
                "redact",
                "--profile",
                "cpa-share",
                str(docs),
                "--output-dir",
                str(out),
                bleach_home=root / "state",
            )

            dest = out / "cpa-share" / "docs2024" / "nested" / "data.csv"
            redacted = dest.read_text(encoding="utf-8")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("***-**-6789", redacted)

    def test_unsupported_files_are_errors_without_copy_through(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            text = root / "ok.txt"
            image = root / "photo.jpg"
            out = root / "out"
            text.write_text("email example@comcast.net\n", encoding="utf-8")
            image.write_bytes(b"not really an image")

            result = self.run_bleach(
                "redact",
                "--profile",
                "ai-share",
                str(text),
                str(image),
                "--output-dir",
                str(out),
                bleach_home=root / "state",
            )
            text_exists = (out / "ai-share" / "ok.txt").exists()
            image_exists = (out / "ai-share" / "photo.jpg").exists()

        self.assertEqual(result.returncode, 1)
        self.assertTrue(text_exists)
        self.assertFalse(image_exists)
        self.assertIn("unsupported file type", result.stdout)

    def test_incremental_run_skips_matching_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "tax.txt"
            out = root / "out"
            source.write_text("SSN 123-45-6789\n", encoding="utf-8")

            first = self.run_bleach(
                "redact",
                "--profile",
                "ai-share",
                str(source),
                "--output-dir",
                str(out),
                bleach_home=root / "state",
            )
            second = self.run_bleach(
                "redact",
                "--profile",
                "ai-share",
                str(source),
                "--output-dir",
                str(out),
                bleach_home=root / "state",
            )

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("skipped existing output", second.stdout)

    def test_refuses_output_directory_inside_input_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            docs = root / "docs"
            docs.mkdir()
            out = docs / "out"
            (docs / "tax.txt").write_text("SSN 123-45-6789\n", encoding="utf-8")

            result = self.run_bleach(
                "redact",
                "--profile",
                "ai-share",
                str(docs),
                "--output-dir",
                str(out),
                bleach_home=root / "state",
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("output directory must not be inside an input directory", result.stderr)


if __name__ == "__main__":
    unittest.main()
