# bleach

`bleach` is a local, offline PII redaction CLI for preparing sensitive files
before they are shared with AI tools, CPAs, or other third parties.

The product is intentionally conservative: unsupported files are skipped instead
of copied, learned PII stays in local user state, and redaction output is grouped
by required profile so incremental runs do not clobber different sharing
contexts.

The first implementation target is documented in
[Bleach Product Design](docs/superpowers/specs/2026-06-24-bleach-product-design.md).

## Base

This repository is managed by [Base](https://github.com/basefoundry/base).

Common commands:

```bash
basectl setup bleach
basectl check bleach
basectl doctor bleach
basectl test bleach
```
