# What Broke Last Time

**Purpose:** Append-only log of deployment/upgrade issues and resolutions.  
**Update:** After every incident, failed deploy, rollback, or issue discovered.

---

## Why This Document Exists

**Problem:** Repeating the same mistakes across deployments.

**Solution:** Document every issue, resolution, and follow-up idea.

**Goal:** Learn from mistakes, improve runbooks, automate recurring issues.

---

## How to Use

**After any deploy/upgrade:**

1. If something broke, append an entry below
2. Include: site, date, version transition, symptom, fix, follow-up
3. Never delete entries (append-only)
4. Review before next deploy to avoid repeating issues

---

## Template

```markdown
## Site: <site-slug>

**Date:** YYYY-MM-DD  
**Version:** vOLD → vNEW  
**Symptom:** <what went wrong>  
**Fix:** <what you did to resolve>  
**Follow-up:** <automation idea / process improvement>

---
```

---

## Log Entries

## Site: sum-platform (Core)

**Date:** 2026-01-03  
**Version:** v0.7.1-dev  
**Symptom:** `make test` timed out locally after 300 seconds while running the full suite.  
**Fix:** None yet; rerun with a longer timeout or a focused test selection.  
**Follow-up:** Consider documenting expected runtime or adding a `make test-long` target for full suite runs.

---

## Site: sum-platform (Core)

**Date:** 2026-01-03  
**Version:** v0.7.1-dev  
**Symptom:** `gh pr create` failed with `No commits between feature/test-tiering and task/ci-tiering` when the draft PR was opened before any commits.  
**Fix:** Create at least one commit before running `gh pr create`.  
**Follow-up:** Add a quick PR checklist note to commit before opening draft PRs.

---

## Site: sum-platform (Core)

**Date:** 2026-01-03  
**Version:** v0.7.1-dev  
**Symptom:** `make lint` failed locally with `make: mypy: No such file or directory`, and `make test` failed with `/usr/bin/python: No module named pytest`.  
**Fix:** Install dev dependencies (e.g., `make install-dev`) and ensure the `.venv` is active before running lint/tests.  
**Follow-up:** Add a quick environment check in onboarding docs or Make targets to confirm `mypy`/`pytest` are installed.

---

## Site: sum-platform (Core)

**Date:** 2025-12-25
**Version:** v0.7.1-dev
**Symptom:** `make format` rewrote files inside `.venv/`. This started after `fix(THEME-016-A)` (commit `8bc2a00b`) changed `format` to `black --exclude '(?:^|/)(boilerplate|clients)/' .` + `isort .`. Passing `--exclude` overrides Black's default excludes (including `.venv`), so running at repo root started touching dot-directories.
**Fix:** Scoped `make format` to `core`, `cli`, `tests`, and switched Black to use `pyproject.toml` (`--config`) so the default + extended excludes apply (`.venv`, `boilerplate`, `clients`, dot paths). Kept isort pointed at `pyproject.toml` for its `skip_glob` rules.
**Follow-up:** Keep lint/format targets scoped to tracked source dirs and avoid overriding Black defaults with `--exclude`; prefer `--config` or `--extend-exclude` when custom exclusions are needed.

---

## Site: sum-platform (Core)

**Date:** 2025-12-24
**Version:** v0.5.0 → v0.5.1
**Symptom:** Pip install from public tag failed (`project.name` was `Straight Up Marketing Platform`, not a valid PEP 508 identifier). Release verification broke at `pip install "sum_core @ git+...@v0.5.0"`.
**Fix:** Set `project.name` to `sum-core` in the monorepo `pyproject.toml`, bumped versioning to v0.5.1, regenerated boilerplate pinning, and re-ran release flow.
**Follow-up:** Keep `project.name` PEP 508-compliant before tagging; add a quick `pip install "sum_core @ git+...@<tag>"` check when cutting releases.

---

## Site: sum-platform (Core)

**Date:** 2025-12-18  
**Version:** v0.4.0-dev  
**Symptom:** `make lint` reported success despite 32 type errors and Zero Python files checked by Black.  
**Fix:** Restored Black `include` regex; updated `Makefile` to enforce root Ruff config and make Mypy failure gating; implemented `MYPY_SOFT=1` mode.  
**Follow-up:** Tools now truthfully fail. Ensure "QA Tooling Sanity" check is part of future toolchain audits.

---

## Site: sum-platform (Core)

**Date:** 2025-12-21  
**Version:** v0.4.1-dev  
**Symptom:** Theme Delete Drama regression resurfaced in CI when destructive cleanup quietly targeted repo assets, threatening `themes/theme_a` during CLI/theme tests.  
**Fix:** Introduced `tests/utils/safe_cleanup.py`, the `filesystem_sandbox` fixture, and autouse fixtures for CLI/theme tests so `safe_rmtree` only ever runs inside pytest’s sandbox, added unit/regression tests that trip on a missing `themes/theme_a`, and enforced a CI guard that verifies the directory exists and no protected paths changed.  
**Follow-up:** Keep this entry visible before running destructive test suites to remind maintainers that guard rails are in place and to review them when adding new cleanup logic.

---

## Site: sum-platform (Core)

**Date:** 2025-12-21  
**Version:** v0.4.1-dev  
**Symptom:** Template overrides (THEME-15-A) passed when run alone but failed in the full suite because `RUNNING_TESTS` altered template resolution order and tests mutated `settings.TEMPLATES` per module.  
**Fix:** Rewired `core/sum_core/test_project/test_project/settings.py` to load theme/active templates first with deterministic candidate lists, introduced the shared `theme_active_copy` fixture, and added `tests/templates/test_template_loading_order.py` + wiring guards to prove template origins stay stable.  
**Follow-up:** Any new template fixtures should plug into `theme_active_copy` (or equivalent override_settings usage) instead of hand-editing `settings.TEMPLATES`; add regression tests whenever template precedence changes.

---

## Site: sum-platform (Core)

**Date:** 2025-12-21  
**Version:** v0.4.1-dev  
**Symptom:** `make lint` failed in CI due to Ruff UP032 in boilerplate settings and an unused variable in CLI theme init tests.  
**Fix:** Converted `str.format` calls to f-strings in both boilerplate settings templates and removed the unused `project_root` assignment in `cli/tests/test_theme_init.py`.  
**Follow-up:** Keep the boilerplate + CLI scaffold templates in the lint scope so future edits don’t bypass Ruff.

---

## Site: sum-platform (Core)

**Date:** 2025-12-21  
**Version:** v0.4.1-dev  
**Symptom:** `make lint` failed in CI with mypy `[no-redef]` error in boilerplate optional import pattern. Pattern was: standalone type annotation, then `from x import X as <same_name>` in try block.  
**Fix:** Removed standalone annotation, let the import be the first definition of the name, added `type: ignore[assignment,misc]` to the except branch where `None` is assigned.  
**Follow-up:** When writing optional imports in boilerplate, avoid annotating the name before importing into it. Use pattern: `try: from x import X as _X / except: _X = None  # type: ignore` then assign to properly typed variable.

---

## Site: sum-platform (Core)

**Date:** 2025-12-24  
**Version:** v0.5.1  → v0.5.2
**Symptom:** `make release-check` failed because mypy recursed into `cli/sum_cli/boilerplate/` (synced copy of `boilerplate/`) and tripped on template-only type errors.  
**Fix:** Added mypy excludes for both `boilerplate/` and `cli/sum_cli/boilerplate/` in `pyproject.toml` and documented the exclusions in `docs/dev/hygiene.md`; drift check `make check-cli-boilerplate` left intact.  
**Follow-up:** Keep both boilerplate directories excluded from lint/type checks when adding new tooling, and rerun `make release-check` after syncing boilerplate into the CLI.

---

## Site: sum-platform (Core)

**Date:** 2025-12-24  
**Version:** v0.5.0 → v0.5.1  
**Symptom:** Pip install from public tag failed (`project.name` was `Straight Up Marketing Platform`, not a valid PEP 508 identifier). Release verification broke at `pip install "sum_core @ git+...@v0.5.0"`.  
**Fix:** Set `project.name` to `sum-core` in the monorepo `pyproject.toml`, bumped versioning to v0.5.1, regenerated boilerplate pinning, and re-ran release flow.  
**Follow-up:** Keep `project.name` PEP 508-compliant before tagging; add a quick `pip install "sum_core @ git+...@<tag>"` check when cutting releases.
---

## Site: sage-and-stone

**Date:** 2025-12-29  
**Version:** N/A → v0.6.0  
**Symptom:** Initial staging deploy failed due to missing client production deps (`gunicorn`, `redis`) and a seeder import bug:

- systemd: `sum-sage-and-stone-gunicorn.service` failed with `status=203/EXEC` because `/srv/sum/sage-and-stone/venv/bin/gunicorn` did not exist (gunicorn not installed in venv).
- seeder: `python manage.py seed_sage_stone ...` raised `ModuleNotFoundError: No module named 'home'` because the command imported `HomePage` from `home.models` (breaks packaged projects where the app is `<project>.home`).
- cache: during seeding, Wagtail cache operations raised `ModuleNotFoundError: No module named 'redis'` when using `django.core.cache.backends.redis.RedisCache` without the `redis` Python client installed.

**Fix:** Added `gunicorn` + `redis` to client requirements; updated `seed_sage_stone` to use a packaged import with a safe fallback for file-path-loaded tests; re-deployed, enabled gunicorn, and re-ran seeding.  
**Follow-up:** Ensure boilerplate requirements include production deps used by our runbooks/scripts; add a deploy preflight check that verifies `gunicorn` is present and health is checked over HTTPS (and consider a quick import check for `redis` when Redis cache backend is configured).

---

## Site: sage-and-stone

**Date:** 2025-12-29  
**Version:** v0.6.0 (staging)  
**Symptom:** Admin protection smoke check looked like a failure when tested over plain HTTP (Caddy redirected `/admin/` to HTTPS with `308`), and some clients may not resolve wildcard DNS locally.  
**Fix:** Test admin protection over HTTPS (`/admin/` should be `401`/`403`), and use `curl --resolve sage-and-stone.lintel.site:443:91.98.118.201` when local DNS is not resolving.  
**Follow-up:** Update `docs/ops-pack/smoke-tests.md` to note the HTTPS redirect and the `--resolve` pattern for early-stage deployments.

---

## Site: sum-platform (Core)

**Date:** 2026-01-03  
**Version:** N/A (tooling)  
**Symptom:** `gh pr edit` failed with `GraphQL: Projects (classic) is being deprecated ... (repository.pullRequest.projectCards)` and `gh issue view` returned `HTTP 401: Bad credentials` until authentication was refreshed.  
**Fix:** Refresh GitHub App auth via `~/.codex/bin/gh-app-auth --org markashton480 --configure-gh`, and update PR bodies via REST (`gh api --method PATCH repos/{owner}/{repo}/pulls/<n> -F body=@-`) when `gh pr edit` fails.  
**Follow-up:** Document the REST-based PR edit workaround (or bump `gh` CLI) to avoid GraphQL breakages when Projects (classic) fields are removed.

---

## Site: sum-platform (Core)

**Date:** 2026-01-03  
**Version:** v0.7.1-dev  
**Symptom:** `make test` failed once with `tests/pages/test_blog_templates.py::TestBlogIndexPageTemplateRendering::test_blog_index_displays_featured_images`, then passed on rerun.  
**Fix:** Re-ran `make test`; the specific test passed when executed alone.  
**Follow-up:** Investigate potential flake in blog template rendering test (e.g., test data ordering or shared state) if this recurs.

---

## Follow-Up Tracking

**Automation ideas from this log:**

_(Extract from follow-up notes above and prioritize)_

**High priority:**

- [ ] Add `collectstatic` check to deploy script
- [ ] Add Redis service check to deploy runbook prerequisites

**Medium priority:**

- [ ] Document migration troubleshooting in runbook
- [ ] Add env var validation to deploy script

**Low priority / Future:**

- [ ] Automated smoke test script (covers most common issues)
- [ ] Pre-deploy checklist generator from release notes

---

## Review Cadence

**Before every deploy/upgrade:**

- Review this log for similar sites
- Check if any previous issues apply to current upgrade
- Implement follow-ups if time permits

**Monthly review:**

- Review all entries from last month
- Prioritize automation follow-ups
- Update runbooks with lessons learned

---

## Related Documentation

- [`loop-sites-matrix.md`](loop-sites-matrix.md) — Track site versions
- [`deploy-runbook.md`](deploy-runbook.md) — Fresh deploy process
- [`upgrade-runbook.md`](upgrade-runbook.md) — Upgrade process
- [`rollback-runbook.md`](rollback-runbook.md) — Rollback process

---

**Remember:** Every issue is a lesson. Document it.
