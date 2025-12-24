# THEME-026 Follow-up

## Summary
- Added a codex preflight script and Makefile wrapper to enforce clean trees, fetch origin, and rebase onto origin/develop when behind.
- Documented Codex prompt installation/usage and added a versioned prompt template for running the preflight.

## Files Modified/Created
- scripts/codex_preflight.sh
- Makefile
- docs/dev/codex/README.md
- docs/dev/codex/prompts/sum-preflight.md
- docs/dev/THEME/tasks/THEME-026_followup.md

## Tests
- `./.venv/bin/python -m pytest` (pass)

## Decisions / Blockers
- None; script intentionally stops on dirty trees or diverged branches to avoid unsafe rebases.

## Documentation Updates
- Added docs/dev/codex/README.md for prompt installation and usage.
