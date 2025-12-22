# TEST-015A Follow-up

## Summary
- Added a `scripts/scan_bidi_unicode.py` helper that reports banned bidi/control characters (U+202A–U+202E, U+2066–U+2069, U+200E, U+200F, U+061C, U+FEFF) so future hygiene sweeps can be automated for specific file lists.
- Centralized `_assert_*` helpers in `cli/tests/conftest.py` and updated all CLI init/check/safety/theme tests to import the shared assertions for consistent boundary/source checks.
- Adjusted the invalid-theme regression test to assert the output-root boundary (the deterministic `clients/` directory) rather than a non-existent project path.

## Files modified
- `scripts/scan_bidi_unicode.py`
- `cli/tests/conftest.py`
- `cli/tests/test_cli_safety.py`
- `cli/tests/test_cli_init_and_check.py`
- `cli/tests/test_theme_init.py`
- `docs/dev/Tasks/TEST/TEST-015A.md`

## Tests
- Not run (not requested).

## Notes
- The new CLI helpers ensure all safety tests use the same `SUM_CLIENT_OUTPUT_PATH` boundary/assertions and retrieve the shared fixtures from `cli/tests/conftest.py`.
- `scan_bidi_unicode.py` exits non-zero if any banned characters are detected—run it with a list of files or directories before committing.
