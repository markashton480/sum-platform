# TEST-015A: Remove hidden/bidi Unicode from PR 19 and tighten CLI safety helpers

## Branch

- [ ] Checkout/create branch: `test/TEST-015-cli-safety-refactor`
- [ ] Verify: `git branch --show-current`

## Objective

Remove any hidden/bidirectional Unicode characters introduced in TEST-015 (GitHub is currently warning on multiple changed files), and apply a small correctness/readability pass to the CLI safety refactor by centralising duplicated helper assertions and making the “invalid theme” boundary assertion semantically accurate. This keeps the safety work mergeable and avoids future “invisible character” diff risks.

## Acceptance Criteria

- [ ] GitHub no longer shows “hidden or bidirectional Unicode text” warnings on the files changed in PR #19.
- [ ] A local scan of the touched files reports zero bidi/control characters (at minimum: U+202A–U+202E, U+2066–U+2069, U+200E, U+200F, U+061C, U+FEFF).
- [ ] `make lint` passes.
- [ ] `make test-cli` passes.
- [ ] `make test` passes (or if it is intentionally skipped, the follow-up explains why and provides the CI evidence).
- [ ] Duplicated helpers (`_assert_output_boundary`, `_assert_source_theme_present`) are defined once (preferably in `cli/tests/conftest.py`) and imported/used consistently.
- [ ] The “invalid theme” test no longer makes a boundary assertion on a non-existent project path; it either (a) asserts boundary on the intended target path after creation, or (b) asserts the output root choice independently of existence.

## Steps

1. Confirm you are on the PR branch and up to date.

   - `git fetch origin`
   - `git checkout test/TEST-015-cli-safety-refactor`
   - `git pull --ff-only`

2. Identify and remove hidden/bidirectional Unicode characters from the files GitHub flagged in PR #19.

   - Start with these (as per PR UI warnings):

     - `cli/tests/conftest.py`
     - `cli/tests/test_cli_init_and_check.py`
     - `cli/tests/test_cli_safety.py`
     - `cli/tests/test_theme_init.py`
     - `cli/tests/test_themes_command.py`
     - `pyproject.toml`
     - `docs/dev/Tasks/TEST/TEST-015.md`
     - `docs/dev/Tasks/TEST/TEST-015_followup.md`

   - Use an editor mode that shows invisibles, or a small script/one-liner to print line/col + codepoint names for any bidi/control chars, then delete them and re-save as plain UTF-8.

3. Add (or reuse, if it already exists) a small repo utility to scan for bidi/control chars so we can re-run quickly.

   - Preferred location: `scripts/scan_bidi_unicode.py`
   - It should exit non-zero if any banned characters are found, and print file + line numbers.
   - Scope it to scanning a provided list of file paths (don’t scan the entire repo by default unless you want to).

4. Centralise duplicated CLI test helper assertions.

   - Move `_assert_output_boundary` and `_assert_source_theme_present` into `cli/tests/conftest.py` (or a `cli/tests/utils.py` if that’s cleaner), then update tests to import and use the shared versions.

5. Fix the “invalid theme” test boundary assertion semantics.

   - Make sure the boundary check only applies to a meaningful path (created project root, or a deterministic “target root” that the CLI would use).

6. Run the standard verification commands.

   - `source .venv/bin/activate`
   - `make lint`
   - `make test-cli`
   - `make test`

## Documentation

- [ ] Create `docs/dev/Tasks/TEST/TEST-015A_followup.md` with:

  - Summary of changes made
  - Files modified/created
  - Any blockers or decisions
  - Test results (include command outputs or a concise summary)

## Commit & Push

- [ ] Stage changes: `git add -A`
- [ ] Commit: `fix(TEST-015A): remove bidi unicode and tidy cli safety helpers`

  - Include BOTH `docs/dev/Tasks/TEST/TEST-015A.md` AND `docs/dev/Tasks/TEST/TEST-015A_followup.md`

- [ ] Push: `git push origin test/TEST-015-cli-safety-refactor`

## Verification

- [ ] Run `git status --porcelain`
- [ ] Expected: empty (clean) OR only intentional untracked files (documented in followup)

## Recommended Agent

| Criteria      | Selection                                                                                                                                      |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **Model**     | GPT-5.1 Mini                                                                                                                                   |
| **Thinking**  | Standard                                                                                                                                       |
| **Rationale** | This is a contained hygiene/safety follow-up (unicode sanitisation + minor refactor), low risk and doesn’t require deep architectural changes. |
