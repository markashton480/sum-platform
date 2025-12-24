# TEST-017 Followup

## Summary of changes
- Registered version-aware pytest markers and added collection-time skipping for 0.5.x vs 0.6+.
- Added a legacy smoke test suite for the 0.5.x line.
- Introduced a scheduled/manual GitHub Actions workflow to run the legacy smoke suite.

## Files modified/created
- pyproject.toml
- tests/conftest.py
- tests/smoke/test_smoke_0_5_x.py
- .github/workflows/legacy-smoke.yml
- docs/dev/Tasks/TEST/TEST-017_followup.md

## Legacy ref selection
- Workflow targets `release/0.5.x` if present.
- If the branch is missing, it falls back to the newest `v0.5.*` tag (sorted by version).
- This keeps the job aligned with the frozen 0.5.x line while allowing tags to serve as a backup.

## Blockers or decisions
- None.

## Test results
- Not run locally in this session.
