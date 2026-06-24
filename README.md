# bleach

`bleach` is a local, offline PII redaction CLI for preparing sensitive files
before they are shared with AI tools, CPAs, or other third parties.

The product is intentionally conservative: unsupported files are skipped instead
of copied, learned PII stays in local user state, and redaction output is grouped
by required profile so incremental runs do not clobber different sharing
contexts.

The first implementation target is documented in
[Bleach Product Design](docs/superpowers/specs/2026-06-24-bleach-product-design.md).

## Usage

Learn exact PII values into a local profile:

```bash
bleach learn --profile ai-share --pii-file ./sensitive-values.txt
```

The PII file uses simple key-value lines:

```text
SSN: 123-45-6789
email: example@comcast.net
```

Redact files or directories into a profile-scoped output tree:

```bash
bleach redact --profile ai-share ./tax-docs --output-dir ./redacted --report ./redacted/report.json
```

Verify files or directories before sharing them:

```bash
bleach verify --profile ai-share ./redacted/ai-share/tax-docs
```

## Profiles

`--profile` is required. The MVP supports:

- `ai-share`: full typed replacement such as `[REDACTED:SSN]`.
- `cpa-share`: partial masking that keeps the last four digits where useful.

Learned profiles are stored locally under
`~/.base.d/bleach/profiles/<profile>/learned.json`. Tests and automation can set
`BLEACH_HOME` to use a different local state root.

## Supported Files

The MVP redacts and verifies:

- `.txt`, `.log`, `.md`
- `.csv`, `.tsv`
- `.xlsx`
- text-layer `.pdf`

Unsupported files are per-file errors and are not copied to the output tree.
`.xls`, `.xlsm`, images, scanned PDFs, encrypted PDFs, and blank/image-only PDFs
are intentionally rejected for now.

## Incremental Runs

`bleach redact` is incremental by default. Existing outputs are skipped only when
the manifest shows the same source hash, profile, learned profile hash, and tool
version. Use `--force` to reprocess existing outputs.

## Base

This repository is managed by [Base](https://github.com/basefoundry/base).

Common commands:

```bash
basectl setup bleach
basectl check bleach
basectl doctor bleach
basectl test bleach
```
