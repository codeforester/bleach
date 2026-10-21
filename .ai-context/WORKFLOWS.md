# Workflows

Use synthetic or explicitly selected local inputs when learning the tool:

```bash
bleach learn --profile ai-share --pii-file ./sensitive-values.txt
bleach redact --profile ai-share ./input-docs --output-dir ./redacted --report ./redacted/report.json
bleach verify --profile ai-share ./redacted/ai-share/input-docs
```

These commands write learned state or output files; they are not setup checks.
Review the report and verify the specific output selected for sharing. `--force`
reprocesses matching outputs. Consult CLI help for the exact supported options.

Development uses `pyproject.toml` and `uv.lock`. `basectl setup bleach` prepares
the project; the manifest's test runner uses uv. `./tests/validate.sh` checks the
baseline and invokes unittest through uv. Run `git diff --check` for docs and the
relevant format/verification tests when behavior changes.

Use an issue and a canonical category/issue/date branch in a separate worktree
based on the repository's default branch (`master`). Preserve unrelated local
files and generated output; context documentation does not change redaction
policy, learned data, or the release version.

Sources: [contribution guide](../CONTRIBUTING.md), [manifest](../base_manifest.yaml),
[validation](../tests/validate.sh), and [package metadata](../pyproject.toml).
