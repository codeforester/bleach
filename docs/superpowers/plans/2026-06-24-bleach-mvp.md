# Bleach MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the MVP `bleach` CLI from issue #1 with local learned PII profiles, regex redaction, profile-scoped output, incremental manifests, reports, verification, and safe handling for text, delimited, XLSX, and text-layer PDF files.

**Architecture:** Use a small src-layout Python CLI with focused modules for profiles, learning, detectors, masking, walking, manifests, processors, and orchestration. Keep Base integration through `bin/bleach`, `base_manifest.yaml`, and `tests/validate.sh`; keep persistent learned PII under `~/.base.d/bleach/profiles/<profile>/learned.json` unless tests override `BLEACH_HOME`.

**Tech Stack:** Python 3.12, stdlib `argparse`/`unittest`/`csv`/`json`, `openpyxl` for `.xlsx`, PyMuPDF (`fitz`) for text-layer PDFs, uv for dependency/runtime management, Base for project orchestration.

---

## File Structure

- `bin/bleach`: executable Base-friendly launcher for the CLI.
- `src/bleach/cli.py`: argument parsing and command dispatch.
- `src/bleach/profiles.py`: supported profiles and profile policy.
- `src/bleach/learned.py`: learned PII parsing, normalization, atomic persistence, and loading.
- `src/bleach/detectors.py`: built-in regex detectors, learned detectors, span merging.
- `src/bleach/masking.py`: profile-specific masking behavior.
- `src/bleach/walker.py`: input expansion, profile-scoped destination mapping, unsupported file classification.
- `src/bleach/manifest.py`: source/config/version hash metadata and incremental skip decisions.
- `src/bleach/processors.py`: text, CSV/TSV, XLSX, and PDF processors.
- `src/bleach/reporting.py`: JSON-safe report records and exit-code decisions.
- `src/bleach/runner.py`: redact and verify orchestration.
- `tests/test_*.py`: unittest coverage for each unit and integration flows.
- `tests/fixtures/`: small local-only sample files with non-real fake PII.
- `tests/validate.sh`: baseline plus unit test runner.

## Task 1: CLI Skeleton And Base Launcher

**Files:**
- Create: `bin/bleach`
- Create: `src/bleach/__init__.py`
- Create: `src/bleach/cli.py`
- Create: `tests/test_cli.py`
- Modify: `base_manifest.yaml`
- Modify: `tests/validate.sh`

- [ ] Write tests for required subcommands, required `--profile`, accepted profiles, and exit code `2` for invalid arguments.
- [ ] Run `uv run python -m unittest tests.test_cli -v` and confirm failures caused by missing CLI modules.
- [ ] Implement the minimal argparse CLI and launcher.
- [ ] Run the focused test until it passes.
- [ ] Run `uv run ./tests/validate.sh`.
- [ ] Commit with `git commit -m "Add bleach CLI skeleton"`.

## Task 2: Learned Profile Storage

**Files:**
- Create: `src/bleach/learned.py`
- Create: `tests/test_learned.py`
- Modify: `src/bleach/cli.py`

- [ ] Write tests proving `learn` parses key-value PII, normalizes obvious variants, writes `learned.json` under `BLEACH_HOME` in tests, uses owner-only permissions, and leaves the previous store untouched on invalid input.
- [ ] Run `uv run python -m unittest tests.test_learned -v` and confirm failures caused by missing learning behavior.
- [ ] Implement parser, normalization, atomic write, and load functions.
- [ ] Wire `bleach learn --profile PROFILE --pii-file PATH`.
- [ ] Run focused and full validation.
- [ ] Commit with `git commit -m "Add learned profile storage"`.

## Task 3: Detectors And Masking

**Files:**
- Create: `src/bleach/detectors.py`
- Create: `src/bleach/masking.py`
- Create: `tests/test_detectors.py`

- [ ] Write tests for SSN, email, card with Luhn validation, EIN, ITIN, PAN, phone, disabled Aadhaar by default, learned exact values, overlapping span resolution, `ai-share` full masking, and `cpa-share` partial masking.
- [ ] Run focused tests and confirm failures.
- [ ] Implement detector registry, span model, Luhn helper, learned detectors, merge policy, and masking.
- [ ] Run focused and full validation.
- [ ] Commit with `git commit -m "Add MVP detectors and masking"`.

## Task 4: Walker, Manifest, Report, Text And Delimited Redaction

**Files:**
- Create: `src/bleach/walker.py`
- Create: `src/bleach/manifest.py`
- Create: `src/bleach/reporting.py`
- Create: `src/bleach/processors.py`
- Create: `src/bleach/runner.py`
- Create: `tests/test_runner_text.py`
- Modify: `src/bleach/cli.py`

- [ ] Write tests for file and directory output mapping under `OUTDIR/<profile>`, unsupported file errors with no copy-through, input/output nesting refusal, incremental skip using manifest metadata, JSON reports, `--silent`, and `--force`.
- [ ] Run focused tests and confirm failures.
- [ ] Implement text, `.csv`, and `.tsv` processors plus runner orchestration.
- [ ] Wire `bleach redact`.
- [ ] Run focused and full validation.
- [ ] Commit with `git commit -m "Add text redaction runner"`.

## Task 5: Verify Command

**Files:**
- Create: `tests/test_verify.py`
- Modify: `src/bleach/runner.py`
- Modify: `src/bleach/cli.py`
- Modify: `src/bleach/reporting.py`

- [ ] Write tests proving `verify` exits `0` for clean files, exits `1` for residual detections, supports files and directories, rejects unsupported files as per-file errors, and never logs raw detected values.
- [ ] Run focused tests and confirm failures.
- [ ] Implement verification orchestration using the same detectors and supported processors.
- [ ] Run focused and full validation.
- [ ] Commit with `git commit -m "Add verify command"`.

## Task 6: XLSX Processor

**Files:**
- Create: `tests/test_xlsx_processor.py`
- Modify: `src/bleach/processors.py`
- Modify: `src/bleach/walker.py`

- [ ] Write tests using fake workbook values to prove `.xlsx` cell values are overwritten across visible and hidden sheets, `.xls`/`.xlsm` are rejected, and verification catches residual values.
- [ ] Run focused tests and confirm failures.
- [ ] Implement safe `.xlsx` handling with `openpyxl`.
- [ ] Run focused and full validation.
- [ ] Commit with `git commit -m "Add xlsx redaction processor"`.

## Task 7: Text-Layer PDF Processor

**Files:**
- Create: `tests/test_pdf_processor.py`
- Modify: `src/bleach/processors.py`
- Modify: `src/bleach/walker.py`

- [ ] Write tests with generated fake PDFs proving text-layer redaction removes extractable PII, metadata is cleared, encrypted/image-only PDFs are rejected or reported unsupported, and verification catches residual text.
- [ ] Run focused tests and confirm failures.
- [ ] Implement PyMuPDF text search, redact annotations, applied redactions, metadata clearing, and verification extraction.
- [ ] Run focused and full validation.
- [ ] Commit with `git commit -m "Add text-layer PDF redaction processor"`.

## Task 8: Documentation And PR Readiness

**Files:**
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/superpowers/specs/2026-06-24-bleach-product-design.md`
- Modify: `tests/validate.sh`

- [ ] Update README usage examples for `learn`, `redact`, `verify`, `BLEACH_HOME`, incremental behavior, and supported/rejected files.
- [ ] Fix the spec's remaining public/private wording.
- [ ] Ensure validation runs unit tests and baseline checks.
- [ ] Run `uv run ./tests/validate.sh`, `./tests/validate.sh`, `git diff --check`, and `basectl test bleach`.
- [ ] Push branch and open a draft PR closing issue #1.

## Self-Review

- Spec coverage: tasks cover CLI, profiles, learning, detectors, text/delimited, XLSX, PDF, manifests, reports, verification, Base validation, and docs.
- Deferred scope remains outside this plan: OCR, NER, advanced Office/PDF surfaces, encrypted learned storage, path privacy, custom profile policy, and packaging polish.
- Placeholder scan: no task depends on undefined future behavior; each task has a focused test-first command and concrete file scope.
