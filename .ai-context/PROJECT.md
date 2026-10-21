# Bleach

Bleach is a local, offline PII-redaction CLI for preparing sensitive files for
sharing. Users learn exact sensitive values into a local profile, redact
supported files, then verify the intended output. The product is conservative:
unsupported files are reported and not copied as if they had been sanitized.

Every operation requires a profile. `ai-share` uses full typed replacements;
`cpa-share` keeps limited useful suffixes where its masking rules allow them.
Supported inputs include text/log/Markdown, CSV/TSV, XLSX, and text-layer PDF.
Legacy/macro-enabled spreadsheets, images, scanned or encrypted PDFs, and
blank/image-only PDFs are outside the documented MVP support boundary.

Outputs are grouped by profile so different sharing contexts do not collide.
Learned values and output/report data remain local runtime state. A successful
supported-format run is evidence about this tool's detection and processing
rules, not a universal guarantee that arbitrary documents contain no private data.

Sources: [README](../README.md),
[product design](../docs/superpowers/specs/2026-06-24-bleach-product-design.md), and
[CLI](../src/bleach/cli.py).
