# Architecture

The Python implementation lives under `src/bleach/`. `cli.py` defines argparse
commands and profile selection. `learned.py` owns local learned-value profiles;
`detectors.py` and `masking.py` identify and transform sensitive values.
`walker.py` enumerates input files, `processors.py` handles supported formats,
and `runner.py` coordinates redact/verify operations and reporting.

Incremental matching in `manifest.py` binds an output to the source path/hash,
profile, learned-configuration hash, and tool version. Existing output is reused
only when that record matches. `--force` requests reprocessing. This cache
contract is separate from the AI-context export job's byte comparison.

The default learned-state location is under the user's Base directory;
`BLEACH_HOME` selects a separate state root for tests/automation. Never copy
learned profiles, original documents, generated reports, or real account/tax
values into this pack or test fixtures. Tests use synthetic data and exercise
text, spreadsheet, PDF, CLI, and verification paths.

Sources: [runner](../src/bleach/runner.py), [processors](../src/bleach/processors.py),
[incremental manifest](../src/bleach/manifest.py), [learned state](../src/bleach/learned.py),
and [tests](../tests/).
