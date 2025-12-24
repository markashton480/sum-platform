## TEST-02 — Deterministic Template Resolution + Eliminate Settings Leakage (Fix THEME-15-A)

**Branch:** `develop`
**Goal:** Make template loading **identical in tests and production**, remove any conditional template-path logic (e.g. `RUNNING_TESTS`), and stop settings/state leakage that causes “passes alone, fails in suite” (THEME-15-A class issue).

### Context

Your post-MVP test strategy explicitly calls out a known issue: template overrides work in isolation but fail in the full suite due to **settings leakage** and conditional template-loading logic. The strategy’s intended fix is: **remove conditional logic and make template resolution deterministic everywhere**. 

TEST-01 focused on filesystem safety. Now we need to restore **correctness trust**: a test suite that is order-independent and loads templates consistently.

---

## Scope

### A) Identify and remove test/prod divergence in template configuration

* Find any conditional branches in settings (commonly `RUNNING_TESTS`, env flags, alternate `TEMPLATES[0]["DIRS"]`, etc.).
* Refactor so template discovery order is **explicit and stable**, matching the platform’s intended behaviour:

  1. active theme templates
  2. client overrides
  3. app templates (`APP_DIRS`)
* If settings are duplicated between test settings and “real” settings, consider a shared helper that both import (agent judgement; don’t over-engineer).

### B) Fix settings leakage between tests

* Locate where tests mutate settings globally (direct assignment, module-level changes, or fixtures that don’t unwind).
* Replace with safe patterns:

  * `override_settings(...)`
  * pytest-django `settings` fixture
  * fixture scopes tightened (avoid session/module scope unless required)
* Ensure template loaders/caches are not persisting across tests in a way that breaks override behaviour (agent to confirm if template caching is a factor).

### C) Turn the known-issue regression into a real pass

* Locate the THEME-15-A regression test (it may currently be `xfail` or marked as “known issue”).
* Make it **pass reliably** in:

  * isolated run (`pytest tests/themes/test_known_issues.py::...`)
  * full suite run (`pytest -q`)

### D) Add one “order independence” guard

Light-touch (don’t boil the ocean):

* Add a targeted test that loads the relevant template twice across distinct test functions / modules and asserts the origin is stable (theme override remains theme override).
  (If you already use random ordering tooling, great; if not, keep it deterministic and minimal.)

---

## Non-goals

* Expanding theme contract tests broadly (that can be TEST-03).
* Adding Lighthouse/axe/perf gates (later ticket once functional correctness is stable).

---

## Acceptance Criteria

* ✅ No `RUNNING_TESTS` (or equivalent) conditional behaviour affects template resolution (or it’s strictly limited to non-template concerns and documented).
* ✅ THEME-15-A regression test passes without `xfail`.
* ✅ Template origin assertions are stable:

  * `pytest tests/themes -q` passes
  * `pytest -q` (or your canonical full suite command) passes
* ✅ No cross-test leakage: rerunning the full suite twice yields the same result.
* ✅ Documentation updated if the implemented resolution order differs from what’s documented.

---

## Verification Steps (local)

Run, in this order, capturing output in the work report:

1. `pytest tests/themes -q`
2. `pytest -q` (or `make test` if that’s the canonical full suite runner, but ensure it truly runs the whole suite)
3. Run the full suite a second time to catch order/leak flakiness: `pytest -q`

---

## Git hygiene (mandatory)

**Start of task**

* `git checkout develop`
* `git pull`
* `git status --porcelain` must be empty (stash or reset before starting)

**Commits**

* Prefer **2 commits**:

  1. `test(TEST-02): deterministic template resolution; fix settings leakage`
  2. `docs/ci(TEST-02): update strategy/notes if needed` (only if docs/CI changed)

**End of task**

* `git status --porcelain` empty
* Work report must include:

  * commit SHA(s)
  * list of changed files
  * the exact commands run + pass/fail results

---

## Record-keeping

* Update `test-strategy-post-mvp-v1.md` if you change the described resolution mechanism or remove the documented “known issue”. 
* If this fixes a flaky pattern that previously burned time, append a short note to `docs/ops-pack/what-broke-last-time.md` (append-only).

---

**Complexity:** **Medium–High** (Django settings/template loader nuances + test isolation; may require careful debugging of where state leaks)

---

## Work Report — 2025-12-21

### Summary

- Template settings now build the same deterministic `[theme -> overrides -> APP_DIRS]` chain in every environment, removing the `RUNNING_TESTS` divergence that previously masked THEME-15-A.
- `theme_active_copy` refreshes Theme A into `theme/active` per test run and `_reset_django_template_loaders()` keeps cached loaders from leaking between modules.
- Regression coverage expanded: navigation/page/form/galleries assert Theme A markup and the new `tests/templates/test_template_loading_order.py` guards template origin stability + fallback semantics.
- Theme A CSS fingerprint regenerated to align with the regenerated fixture output.

### Verification

| Command | Result |
| --- | --- |
| `pytest tests/themes -q` | ✅ 69 passed, 7 warnings (Django URLField defaults) |
| `pytest -q` | ✅ 751 passed, 45 warnings (URLField + Sentry deprecation) |
| `pytest -q` | ✅ 751 passed, 45 warnings (repeat run to confirm no leakage) |

### Files Changed

core/sum_core/test_project/test_project/settings.py  
tests/conftest.py  
tests/pages/test_home_page.py  
tests/pages/test_standard_page.py  
tests/templates/test_base_template.py  
tests/templates/test_content_blocks_rendering.py  
tests/templates/test_form_blocks_rendering.py  
tests/templates/test_gallery_rendering.py  
tests/templates/test_homepage_rendering.py  
tests/templates/test_navigation_template.py  
tests/templates/test_process_faq_rendering.py  
tests/templates/test_standard_page_rendering.py  
tests/templates/test_template_loading_order.py  
tests/themes/test_test_project_theme_wiring.py  
tests/themes/test_theme_a_featured_case_study.py  
tests/themes/test_theme_a_hero_rendering.py  
tests/themes/test_theme_a_manifesto.py  
tests/themes/test_theme_a_portfolio_rendering.py  
tests/themes/test_theme_a_rendering.py  
themes/theme_a/static/theme_a/css/.build_fingerprint  
docs/dev/master-docs/test-strategy-post-mvp-v1.md  
docs/ops-pack/what-broke-last-time.md  
docs/dev/Tasks/TEST/TEST-002.md

### Commits

1. `test(TEST-02): deterministic template resolution; fix settings leakage` — d0e89c7b41a79133b42080dfa034d67ed311162e
2. `docs/ci(TEST-02): document deterministic template loader fix` — *(SHA equals the commit that includes this report; capture via `git rev-parse HEAD` after merge)*

### Notes

- Remaining pytest warnings stem from Django URLField scheme defaults and Sentry SDK deprecations; they pre-date this work and were observed on every run.

