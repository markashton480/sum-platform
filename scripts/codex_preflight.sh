#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

echo "[preflight] Checking working tree cleanliness..."
status_output=$(git status --porcelain)
if [ -n "$status_output" ]; then
  echo "[preflight] Working tree has uncommitted changes. Please commit or stash before continuing." >&2
  echo "$status_output" >&2
  exit 1
fi

echo "[preflight] Fetching origin..."
git fetch origin

if ! git show-ref --verify --quiet refs/remotes/origin/develop; then
  echo "[preflight] Missing remote branch origin/develop. Ensure it exists and re-run (git fetch origin develop)." >&2
  exit 1
fi

ahead_behind=$(git rev-list --left-right --count origin/develop...HEAD)
behind_count=${ahead_behind%% *}
ahead_count=${ahead_behind##* }

if [ "$behind_count" -gt 0 ] && [ "$ahead_count" -gt 0 ]; then
  echo "[preflight] Branch has diverged from origin/develop (behind: $behind_count, ahead: $ahead_count)." >&2
  echo "[preflight] Manual intervention required: rebasing may rewrite remote history." >&2
  exit 1
fi

if [ "$behind_count" -gt 0 ]; then
  echo "[preflight] Branch is behind origin/develop by $behind_count commit(s). Running rebase..."
  git rebase origin/develop
  echo "[preflight] Rebase completed."
else
  if [ "$ahead_count" -gt 0 ]; then
    echo "[preflight] Branch is ahead of origin/develop by $ahead_count commit(s); no rebase needed."
  else
    echo "[preflight] Branch is up to date with origin/develop."
  fi
fi

echo
echo "[preflight] Next steps:"
echo "- Run relevant tests (e.g., make test or targeted slices)."
echo "- If you changed theme templates/tailwind inputs, rebuild theme CSS + fingerprint before pushing."
echo "- If you hit conflicts in generated CSS/fingerprint: resolve by regenerating, not hand-merging."
