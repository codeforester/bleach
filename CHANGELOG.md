# Changelog

All notable changes to bleach will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and versions are tracked in the repo-root `VERSION` file.

## [Unreleased]

### Added

- Initialized the repository with the Base-managed repo baseline.
- Added the MVP `bleach` CLI with `learn`, `redact`, and `verify`.
- Added local learned PII profile storage under `~/.base.d/bleach`.
- Added built-in regex detectors, masking profiles, JSON reports, manifests,
  incremental redaction, and verification.
- Added redaction support for text, delimited text, `.xlsx`, and text-layer PDF
  files.
