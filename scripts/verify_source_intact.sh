#!/usr/bin/env bash
set -euo pipefail

required_paths=(
  "themes/theme_a"
  "themes/theme_a/theme.json"
)

protected_paths=(
  "themes"
  "boilerplate"
  "clients"
  "core"
  "cli"
  "docs"
  "infrastructure"
  "scripts"
)

missing_paths=()
for required_path in "${required_paths[@]}"; do
  if [ ! -e "$required_path" ]; then
    missing_paths+=("$required_path")
  fi
done

if [ ${#missing_paths[@]} -ne 0 ]; then
  echo "Missing required paths:" >&2
  for missing_path in "${missing_paths[@]}"; do
    echo "  - $missing_path" >&2
  done
  exit 1
fi

modified_tracked=$(git diff --name-only -- "${protected_paths[@]}")
if [ -n "$modified_tracked" ]; then
  echo "Tracked files modified under protected paths:" >&2
  echo "$modified_tracked" >&2
  exit 1
fi

untracked_files=$(git ls-files --others --exclude-standard -- "${protected_paths[@]}")
if [ -n "$untracked_files" ]; then
  echo "Untracked files found under protected paths:" >&2
  echo "$untracked_files" >&2
  exit 1
fi
