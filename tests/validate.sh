#!/usr/bin/env bash

required_files=(
  README.md
  VERSION
  CHANGELOG.md
  CONTRIBUTING.md
  .github/pull_request_template.md
  .github/base-project.yml
  LICENSE
  base_manifest.yaml
  pyproject.toml
  uv.lock
  docs/superpowers/specs/2026-06-24-bleach-product-design.md
  .github/workflows/project-intake.yml
  .github/workflows/tests.yml
)

for file in "${required_files[@]}"; do
  [[ -f "$file" ]] || {
    printf 'Missing required file: %s\n' "$file" >&2
    exit 1
  }
done

[[ -x bin/bleach ]] || {
  printf 'Missing executable launcher: bin/bleach\n' >&2
  exit 1
}

export UV_CACHE_DIR="${UV_CACHE_DIR:-${TMPDIR:-/tmp}/bleach-uv-cache}"
PYTHONPATH="${PWD}/src${PYTHONPATH:+:${PYTHONPATH}}" uv run python -m unittest discover -s tests -p 'test_*.py'

printf 'Repository baseline is present.\n'
