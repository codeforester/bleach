# Bleach Product Design

## Product Shape

`bleach` is an independent Base-managed product under `codeforester/bleach`.
It is a Python CLI managed by `uv`, orchestrated by Base as a peer repository,
and exposed through the command name `bleach`.

The product purpose is local, offline redaction of personally identifiable
information before documents are shared with AI tools, CPAs, or other third
parties. It is not a cloud service, not a DLP guarantee, and not a tax filing or
financial interpretation product.

## Base Contract

The repository is a normal Base project:

- `base_manifest.yaml` declares `project.name: bleach` and `python.manager: uv`.
- `tests/validate.sh` is the canonical project validation entry point.
- Base owns orchestration through `basectl setup bleach`, `basectl check bleach`,
  `basectl doctor bleach`, and `basectl test bleach`.
- Bleach owns its own code, dependencies, tests, learned profile storage, and
  product-specific setup.

The repo starts public under `codeforester/bleach`. The CLI package is not
intended for PyPI publication in the MVP.

## CLI Surface

The CLI has three top-level subcommands:

```bash
bleach learn --profile PROFILE --pii-file PATH
bleach redact --profile PROFILE INPUT [INPUT ...] --output-dir OUTDIR
bleach verify --profile PROFILE INPUT [INPUT ...]
```

`--profile` is required for every subcommand. Profiles separate output trees and
detector policy. The initial profiles are:

- `ai-share`: strongest masking, intended for sharing with AI tools.
- `cpa-share`: partial reveal where useful for a human reviewer.

`redact` writes into `OUTDIR/<profile>/...`. Individual file inputs are written
directly under the profile directory. Directory inputs create
`OUTDIR/<profile>/<input-dir-name>/...` and preserve the internal tree.

`verify` checks existing files or directories and fails when enabled detectors
still find sensitive material.

`learn` reads an explicit user-provided PII file and creates persistent local
learned detectors for the selected profile. On a successful `learn` run, the
previous learned profile is atomically replaced. On failure, the previous learned
profile remains untouched.

## Learned Profile Storage

Learned PII is local user state, not repository state. The initial storage path
is:

```text
~/.base.d/bleach/profiles/<profile>/learned.json
```

The learned store must be created with owner-only permissions. Raw learned
values must never appear in logs, reports, exception text, or test fixtures.

The MVP learned format is exact-value matching, not machine learning. The input
file supports key-value pairs such as:

```yaml
SSN: 123-45-6789
email: example@comcast.net
```

The implementation may normalize obvious variants, such as removing separators
from SSNs and credit cards, but it must preserve deterministic behavior.

## Redaction Defaults

Bleach is incremental by default. If the expected output exists and its manifest
shows the same source hash, profile, config hash, learned profile hash, and tool
version, `redact` skips the file and logs an INFO message. `--silent` suppresses
ordinary INFO output. `--force` reprocesses existing outputs.

File existence alone is not enough to skip work.

Unsupported files are per-file errors. They are skipped, processing continues,
and nothing is copied to the output tree. The output directory must contain only
files that Bleach has redacted and verified, plus Bleach-owned reports or
manifests.

Paths and filenames may appear in logs and reports. Users are responsible for
not putting sensitive values in filenames.

## MVP File Support

The MVP supports:

- Plain text: `.txt`, `.log`, `.md`
- Delimited text: `.csv`, `.tsv`
- Excel: `.xlsx`
- PDF: text-layer `.pdf`

The MVP explicitly rejects:

- Images
- Image-only or scanned PDFs
- Encrypted PDFs
- Signed PDFs
- PDFs with embedded files
- `.xls`
- `.xlsm`
- Workbooks with macros, pivot caches, external links, or unsupported embedded
  objects
- Unknown or unsupported file types

Rejected files are reported as per-file errors and do not abort the whole run.

## Detection

MVP detectors combine built-in regex detectors with learned exact-value
detectors. Built-in detectors include:

- US SSN
- email
- credit and debit card numbers with Luhn validation
- configurable bank-account-like numbers with conservative context constraints
- phone numbers
- EIN and ITIN
- India PAN
- India Aadhaar, disabled by default unless the profile enables it

The detector architecture must not assume plain text only. Processors extract
text segments with provenance so detections can be mapped back to document
locations such as text offsets, CSV cells, Excel cells, and PDF page text
locations.

## Processing Model

The pipeline is:

1. Expand inputs into jobs and planned destinations.
2. Validate collisions, unsupported input/output nesting, symlink behavior, and
   profile output roots before writing anything.
3. Load built-in, profile, and learned detectors.
4. Process each file independently.
5. Write outputs atomically.
6. Re-scan outputs through verification.
7. Write a report and incremental manifest.

The unit of parallelism is one file. A file failure is isolated and recorded
without aborting the whole batch unless argument validation fails before work
starts.

## Processor Requirements

Text and delimited processors replace matched substrings with profile-specific
masks while preserving file structure.

Excel MVP support uses `.xlsx` only. It overwrites stored cell values, scans all
sheets including hidden sheets, and strips or rejects workbook features it cannot
prove safe. It must not rely on formatting, hiding, or visual overlay.

PDF MVP support uses real PyMuPDF redactions and applies them so underlying text
is removed. It also strips metadata and rejects unsupported leak surfaces such as
encrypted files, signatures, attachments, image-only pages, and form-heavy files
until those are intentionally supported.

## Logging And Reports

Logs and reports must never include raw sensitive values. They may include file
paths, detector names, masked examples, counts, statuses, durations, and error
codes.

Reports are machine-readable JSON. Each file record includes source path,
destination path, profile, status, processor, detection counts by type, duration,
and error details without raw PII.

## Exit Codes

- `0`: all requested work completed cleanly.
- `1`: processing completed with per-file failures or verification failures.
- `2`: fatal argument, config, profile, collision, or input/output validation
  error before processing.

## MVP Scope

The MVP includes:

- Independent public `codeforester/bleach` repo.
- Base-managed project baseline.
- Python/uv project setup.
- `learn`, `redact`, and `verify` command surfaces.
- Required profiles and profile-scoped output directories.
- Persistent learned exact-value profile storage.
- Built-in regex detectors listed above.
- Text, CSV, TSV, `.xlsx`, and text-layer PDF processors.
- Manifest-based incremental processing.
- JSON report generation.
- Verification pass after redaction.
- Tests for path mapping, detectors, learning, incremental behavior, unsupported
  file errors, and safe logging.

## Deferred Features

These are deliberately outside the MVP and should be tracked as GitHub issues:

- OCR for images and scanned PDFs.
- NER for names, organizations, and addresses.
- `.xls` and `.xlsm` support.
- Advanced Excel pivot, macro, external-link, chart, comment, and embedded-object
  handling.
- Advanced PDF form, annotation, attachment, signature, bookmark, and OCR-layer
  handling.
- Encrypted or keychain-backed learned profile storage.
- Path privacy mode for logs and reports.
- User-defined profile creation and detector customization.
- Public release, packaging, and installer polish.
