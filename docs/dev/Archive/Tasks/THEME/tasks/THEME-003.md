## THEME-002 review

### What was delivered (per report)

* PortfolioItem metadata fields added: `constraint`, `material`, `outcome`. 
* `SiteSettings.established_year` added and exposed in admin. 
* Migration created, tests added, docs updated. 
* Testing **not run**. 

### Where it diverges from the plan (and why it matters)

1. **PortfolioItemBlock file location**

* Plan says PortfolioItemBlock change should be in `core/sum_core/blocks/gallery.py`. 
* Report says it was done in `core/sum_core/blocks/content.py`. 
  **Risk:** we might have edited the wrong block (or there are two similarly named blocks), and Theme A’s `portfolio.html` work will later “mysteriously” not see the new fields.

2. **Migration location / app label looks suspicious**

* Plan says `makemigrations branding`. 
* Report says they ran `makemigrations sum_core` and the migration lives at `core/sum_core/migrations/0007_sitesettings_established_year.py`. 
* In our repo structure, `branding` is a first-class Django app under `sum_core/branding/`. 
  **Risk:** the migration may not actually apply to the `branding` app’s models, meaning `established_year` may not exist in real DB state once you run `migrate` cleanly.

3. **No verification loop yet**

* The plan’s success criteria explicitly requires “fields appear in admin, save successfully.” 
* Tests weren’t run, and admin wasn’t confirmed. 

### Verdict

THEME-002 is **directionally correct**, but I would not mark it “done” yet. It needs a tight stabilisation pass to:

* confirm we edited the *canonical* PortfolioItemBlock used by PortfolioBlock
* ensure the `branding` migration is in the right place and applies cleanly
* run the small test slice

That stabilisation pass should be the *next ticket* before we build any templates that rely on these fields (PortfolioBlock template work is coming very soon). 

---

## Task Ticket — THEME-003: Stabilise THEME-002 (canonical block + correct migration + verify)

### Goal

Make THEME-002 changes *real* and reliable:

* `constraint/material/outcome` exist on the **actual** PortfolioItemBlock used by PortfolioBlock
* `established_year` exists on SiteSettings with a **correct** migration under the correct Django app
* minimal tests + migrations run cleanly

### Context

* Theme A’s Portfolio template requirements explicitly rely on `constraint/material/outcome`. 
* `branding` is a dedicated app within `sum_core`, so its model migrations should live with that app. 

### Scope

#### A) PortfolioItemBlock: ensure correct definition is updated

1. Locate the canonical `PortfolioItemBlock` definition that is used by the block registered as `portfolio` in PageStreamBlock (and therefore in StandardPage/HomePage streamfields). (See page-types reference: StandardPage uses PageStreamBlock.) 
2. Ensure this canonical `PortfolioItemBlock` has:

   * `constraint = blocks.CharBlock(max_length=100, required=False)`
   * `material = blocks.CharBlock(max_length=100, required=False)`
   * `outcome = blocks.CharBlock(max_length=100, required=False)`
3. If there are duplicate/conflicting `PortfolioItemBlock` definitions:

   * consolidate to a single source of truth
   * update imports/references accordingly
   * update tests to target the canonical block module

#### B) SiteSettings.established_year: correct migration + admin panel

1. Confirm `SiteSettings` is defined in `sum_core.branding.models` (as per wiring inventory). 
2. Ensure:

   * `established_year = models.IntegerField(null=True, blank=True)`
3. Ensure Wagtail admin exposes the field in the appropriate settings panel.
4. Fix migrations:

   * Ensure the migration is created under the **branding app’s migrations** (expected in `core/sum_core/branding/migrations/` given app layout). 
   * If a stray migration exists under `core/sum_core/migrations/`, remove or neutralize it in a safe way (don’t break existing migration history). Prefer regenerating correctly rather than hand-moving files unless you know the dependency graph is clean.

#### C) Docs

Update **authoritative** docs under `docs/dev/`:

* `docs/dev/blocks-reference.md` reflects new PortfolioItem fields
* `docs/dev/WIRING-INVENTORY.md` reflects `established_year` (where SiteSettings fields are described)

(Repo structure explicitly calls `docs/dev/blocks-reference.md` the authoritative catalogue.) 

### Files likely involved

* `core/sum_core/blocks/gallery.py` (or wherever canonical PortfolioItemBlock actually lives)
* `core/sum_core/blocks/content.py` (only if canonical lives here, or to remove duplicate)
* `core/sum_core/branding/models.py`
* `core/sum_core/branding/migrations/00xx_*.py`
* `tests/blocks/...` (update to match canonical module)
* `tests/branding/...`
* `docs/dev/blocks-reference.md`
* `docs/dev/WIRING-INVENTORY.md`

### Test plan (must run)

From repo root:

1. Run targeted tests:

   * `pytest tests/branding/test_site_settings_model.py`
   * `pytest tests/blocks/ -k portfolio` (or the specific portfolio/content block tests that assert the new fields)
2. Run migrations cleanly in the harness project:

   * `python core/sum_core/test_project/manage.py showmigrations`
   * `python core/sum_core/test_project/manage.py migrate`
3. Manual sanity check (quick):

   * Wagtail admin → Settings → Site Settings: verify `established_year` appears and saves
   * Edit a page with PortfolioBlock: verify the new fields exist on each portfolio item and save

### Acceptance criteria

* Canonical PortfolioItemBlock exposes `constraint/material/outcome` in admin and persists values. 
* `SiteSettings.established_year` appears in admin, saves, and migrations apply without errors. 
* Targeted tests pass.
* No orphan/incorrect migrations left behind that will confuse future upgrades.

### Notes / pitfalls to watch

* If `PortfolioBlock` uses an inner struct/list that imports PortfolioItemBlock from a specific module, editing a “different” PortfolioItemBlock won’t affect anything. This is the core reason we’re stabilising now.
* Generating migrations with a mis-targeted app label (`makemigrations sum_core` instead of `branding`) is the most likely cause of the migration-path weirdness reported.

---
