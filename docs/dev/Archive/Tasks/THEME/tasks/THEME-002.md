# THEME-002 — Add missing fields to models (Portfolio metadata + established year)

## Goal

Add the missing data fields required by the wireframe-driven Theme A templates:

* Add `constraint`, `material`, `outcome` fields to `PortfolioItemBlock`
* Add `established_year` to `SiteSettings` so templates can stop hardcoding “Est. …”

This is explicitly called out in new-theme-plan “Task 2”.

## Why this matters

* Theme A’s `PortfolioBlock` template requirements include showing constraint/material/outcome metadata (with fallback to location/services). Those fields don’t exist yet, so the template can’t be correctly implemented.
* Theme A also needs a real `established_year` value coming from SiteSettings (no hardcoded branding).

## Scope

### A) Add Portfolio item metadata fields

**File:** `core/sum_core/blocks/gallery.py` 
**Change:** In `PortfolioItemBlock`, add:

* `constraint = blocks.CharBlock(max_length=100, required=False)`
* `material = blocks.CharBlock(max_length=100, required=False)`
* `outcome = blocks.CharBlock(max_length=100, required=False)`

**Notes / constraints:**

* Must be **additive only** (no renames/removals of existing fields) to preserve backward compatibility. 
* Keep existing fields (`location`, `services`, etc.) intact; Theme A template will fall back if the new fields are empty.

### B) Add established_year to SiteSettings

**File:** `core/sum_core/branding/models.py` 
**Change:** On `SiteSettings`, add:

* `established_year = models.IntegerField(null=True, blank=True)`

**Notes:**

* Should appear in Wagtail admin under Settings → Site Settings.
* Keep it nullable/blank to avoid forcing data entry on existing sites.

### C) Migrations

A migration is required for the `branding` app (SiteSettings model change). 

### D) Documentation update (do it in the same PR)

We’re changing public “reference reality”, so update docs immediately:

1. **Update `docs/dev/blocks-reference.md`**
   Add `constraint/material/outcome` to the `PortfolioItemBlock` field table. The current reference does not include them. 

*(Optional but recommended in this ticket if it’s straightforward)*
2) **Update `docs/dev/WIRING-INVENTORY.md`** (or whichever doc enumerates SiteSettings fields) to mention `established_year` exists and is intended for themes to consume. The wiring inventory already frames SiteSettings as the per-site place for branding/config.

## Implementation steps

1. Modify `PortfolioItemBlock` in `core/sum_core/blocks/gallery.py` to add the three optional CharBlocks.
2. Modify `SiteSettings` in `core/sum_core/branding/models.py` to add `established_year`.
3. Create and apply migrations:

```bash
cd core/
python manage.py makemigrations branding
python manage.py migrate
```

4. Update `docs/dev/blocks-reference.md` (PortfolioItemBlock section) to reflect the new fields.
5. Run tests (see below).

## Testing checklist

### Manual (required)

* Run the harness admin and confirm SiteSettings shows the new field:

  * Wagtail Admin → Settings → Site Settings → verify `established_year` exists and saves. 
* Edit a page containing `PortfolioBlock`:

  * Add/edit a portfolio item and verify the three new fields show up and save (even if blank). 

### Automated (required)

Add/adjust pytest coverage (keep it minimal but real):

* **Block schema test:** instantiate/import the `PortfolioItemBlock` and assert the new child block keys exist (`constraint`, `material`, `outcome`).
* **Model field test:** assert `SiteSettings._meta.get_field("established_year")` exists and is nullable/blankable.

(Tests live in `/tests/` and mirror package structure.)

## Definition of Done

* `constraint/material/outcome` appear in the Wagtail editor UI for portfolio items and persist on save. 
* `established_year` appears in SiteSettings, saves, and migration applies cleanly. 
* `docs/dev/blocks-reference.md` reflects the new fields. 
* Pytest passes (at least the relevant tests added/updated).

## Notes / pitfalls

* Changes must be **additive** (no breaking edits to existing block schemas or model fields). 
* Don’t “solve” anything by only changing the test harness: these are core fields used by real consumers. 

---