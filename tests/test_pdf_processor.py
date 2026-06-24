import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin" / "bleach"


class PdfProcessorTests(unittest.TestCase):
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

    def test_redact_pdf_removes_extractable_text_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "tax.pdf"
            out = root / "out"
            _write_pdf(source, "SSN 123-45-6789")

            result = self.run_bleach(
                "redact",
                "--profile",
                "ai-share",
                str(source),
                "--output-dir",
                str(out),
                bleach_home=root / "state",
            )

            dest = out / "ai-share" / "tax.pdf"
            with fitz.open(dest) as doc:
                text = "".join(page.get_text() for page in doc)
                title = doc.metadata.get("title")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("123-45-6789", text)
        self.assertIn("[REDACTED:SSN]", text)
        self.assertFalse(title)

    def test_verify_pdf_catches_residual_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "tax.pdf"
            _write_pdf(source, "SSN 123-45-6789")

            result = self.run_bleach(
                "verify",
                "--profile",
                "ai-share",
                str(source),
                bleach_home=root / "state",
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("residual sensitive data", result.stdout)

    def test_blank_image_only_pdf_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "blank.pdf"
            out = root / "out"
            doc = fitz.open()
            doc.new_page()
            doc.save(source)
            doc.close()

            result = self.run_bleach(
                "redact",
                "--profile",
                "ai-share",
                str(source),
                "--output-dir",
                str(out),
                bleach_home=root / "state",
            )

        self.assertEqual(result.returncode, 1)
        self.assertIn("unsupported PDF without extractable text", result.stdout)


def _write_pdf(path: Path, text: str) -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    doc.set_metadata({"title": "Sensitive fixture"})
    doc.save(path)
    doc.close()


if __name__ == "__main__":
    unittest.main()
