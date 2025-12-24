# TEST-016 Followup

## Summary of changes
- Added a reusable source-integrity verification script and Make target.
- Switched CI test jobs to call the new verification target after each slice.

## Files modified/created
- .github/workflows/ci.yml
- Makefile
- scripts/verify_source_intact.sh
- docs/dev/Tasks/TEST/TEST-016_followup.md

## Blockers or decisions
- None.

## Test results
- make lint (partial): ruff + mypy completed; black --check on full scope hung.
- Investigation: black --check core completes; black --check cli/tests stalls. No non-UTF-8 Python files; no very large .py files. Black process active but slow.

## CI notes
- Updated jobs: test-templates, test-full, test-cli, test-themes
- Verification step name: "Verify source integrity"
