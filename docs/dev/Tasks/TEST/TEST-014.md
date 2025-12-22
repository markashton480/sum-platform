# TASK TICKET: TEST-014 — Theme test conftest + standard fixtures for theme suite

### Plan

1. Create/upgrade `tests/themes/conftest.py` to provide the standard theme fixtures described in the implementation plan (theme dir param, theme-aware settings, helper assertions).
2. Refactor existing theme tests (if any) to use the fixtures rather than bespoke path resolution.
3. Keep it narrow: fixtures + minimal refactor only (no new theme tests yet).

### Checklist & Commands

#### Implementation

- [ ] In `tests/themes/conftest.py`, add:

  - `theme_dir` fixture (parametrized across themes present under `themes/`)
  - `THEME_A_TEMPLATES` (or general `theme_templates_dir(theme_dir)` helper)
  - `theme_aware_settings` fixture (preferably `autouse=True` _only_ if it doesn’t cause side effects outside theme tests)
  - `assert_theme_template_used` helper/fixture factory (asserts origin path contains the theme templates dir when expected)

- [ ] Remove duplicated repo root resolution in theme conftest (use `repo_root` fixture or `tests.utils.REPO_ROOT`).
- [ ] Ensure nothing writes into `themes/` (tmp-only outputs).

#### Local verification (agent must paste output in follow-up)

```bash
make lint
pytest tests/themes/ --collect-only
make test-themes
make test-templates
make test
git status --porcelain
```

### Expected success signals

- Theme tests collect cleanly without import errors (`--collect-only` passes).
- Existing `make test-themes` still passes unchanged.
- No repo dirt after runs (`git status --porcelain` empty).

### Stop / rollback triggers

- Any fixture causing non-theme tests to fail (autouse leaking outside `tests/themes/`).
- Any mutation of protected dirs or theme source.
- Increased flakiness (collection order changes, nondeterminism).

### Record-keeping

- Add `docs/dev/Tasks/TEST/TEST-014.md`
- Add `docs/dev/Tasks/TEST/TEST-014_followup.md` with:

  - what fixtures were added/changed
  - why autouse is/isn’t used
  - verification output

---

## Agent Git hygiene (copy/paste into the ticket)

1. Start up-to-date from develop:

```bash
git fetch origin
git checkout develop
git pull --ff-only origin develop
git status
```

2. One branch per ticket:

```bash
git checkout -b test/TEST-014-theme-conftest origin/develop
```

3. Commit the ticket first:

```bash
git add docs/dev/Tasks/TEST/TEST-014.md
git commit -m "docs(TEST-014): add task ticket"
git push -u origin test/TEST-014-theme-conftest
```

4. Work in small commits, push, open PR → `develop`, include follow-up + verification output.

---

[1]: https://github.com/markashton480/sum_platform/pull/12 "Test/test 013 test infra by markashton480 · Pull Request #12 · markashton480/sum_platform · GitHub"
[2]: https://github.com/markashton480/sum_platform/pull/12/files "Test/test 013 test infra by markashton480 · Pull Request #12 · markashton480/sum_platform · GitHub"
