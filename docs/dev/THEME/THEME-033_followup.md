THEME-033 Followup

Summary of changes:
- Reworked Theme A GalleryBlock markup to match wireframe layout and token usage.
- Added Theme A gallery rendering test covering template override, caption, and alt fallback.

Files modified/created:
- themes/theme_a/templates/sum_core/blocks/gallery.html
- tests/themes/test_theme_a_gallery_rendering.py
- THEME-033_followup.md

Test results:
- `./.venv/bin/python -m pytest -q tests/themes/test_theme_a_gallery_rendering.py`
- `./.venv/bin/python -m pytest -q tests/themes`
- `make test`

Decisions made / blockers hit:
- Used the wireframe header treatment with Theme A tokens and a 4:3 gallery aspect ratio.
- No blockers.

Doc updates made:
- None.
