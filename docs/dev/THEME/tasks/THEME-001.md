# THEME-001 — Fast Iteration Setup (test_project → theme_a templates)

## Title

Point `test_project` template loader at `themes/theme_a/templates/` for fast iteration

## Background / Why

Right now, Theme A template work can’t be iterated on cleanly because the harness doesn’t load templates straight from `themes/theme_a`. The plan explicitly calls out “fast iteration is broken” and makes this the first task. 

## Goal

When running the test harness (`core/sum_core/test_project`), editing any file under:

* `themes/theme_a/templates/…`

…should reflect on browser refresh immediately, without copying/syncing templates.

## Scope

**In scope**

* Update `test_project` template configuration so theme templates come from `themes/theme_a/templates` (repo root), and override core templates.

**Out of scope**

* Changes to `sum init`, CLI theme copying rules, or client project wiring.
* Any block template changes (that’s next tasks).

## Files to change

* `core/sum_core/test_project/test_project/settings.py` 

## Implementation details

1. In `settings.py`, locate the existing `THEME_TEMPLATES_DIR` (the fix-plan suggests it currently points at `BASE_DIR / "theme" / "active" / "templates"`). 
2. Change it to point at repo-level Theme A templates:

   * `BASE_DIR.parent.parent.parent / "themes" / "theme_a" / "templates"` 
3. Ensure Django templates `DIRS` includes this directory **before** app templates so that theme overrides win:

   * Update `TEMPLATES[0]["DIRS"]` to include `THEME_TEMPLATES_DIR` (preferably first entry). 
4. Practical hardening (recommended):

   * If the directory doesn’t exist (e.g., weird CI context), fall back to the previous `theme/active/templates` path so the harness still boots.
   * Keep this logic **local to test_project** (this is a harness convenience, not “platform behavior”). 

## Test plan

### Manual smoke

```bash
cd core/sum_core/test_project
python manage.py runserver
```

* Visit a page that renders theme templates.
* Edit a known template in `themes/theme_a/templates/` (even something trivial like adding a comment or changing a heading).
* Refresh browser → see the change instantly. 

### Automated checks

* Run the standard test suite entrypoint (whatever the repo uses: `pytest`, `make test`, etc.).
* Specifically watch for template-resolution failures (TemplateDoesNotExist) caused by bad `DIRS` ordering.

## Acceptance criteria

* ✅ `runserver` renders using templates from `themes/theme_a/templates/`.
* ✅ Editing a theme template shows changes on refresh with no intermediate steps. 
* ✅ Tests still pass (or any failures are clearly attributable and fixed).
* ✅ No changes to core theme selection behavior (init-time theme choice remains a client concern, not a runtime toggle). 

## Notes / Risks

* The only real risk is accidentally making the harness depend on repo-root paths in contexts where they don’t exist. That’s why the fallback-to-old-path suggestion exists.
* Keep it boring: the point of this ticket is purely to unblock the feedback loop so the rest of the plan can move quickly. 

---
