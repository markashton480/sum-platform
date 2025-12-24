# THEME-013 Work Report — Fix PortfolioBlock Template (Theme A)

## Objective

The goal was to align the `PortfolioBlock` template in Theme A with the wireframe requirements specified in Task 6 of the theme plan.

## Completed Tasks

- [x] Identified and confirmed `PortfolioBlock` field contract in `sum_core/blocks/content.py`.
- [x] Implemented Theme A override for `sum_core/blocks/portfolio.html` with mobile carousel and desktop grid.
- [x] Added right-edge fade overlay for mobile scroll.
- [x] Implemented metadata fallback (Constraint/Material/Outcome -> Location/Services).
- [x] Added 4:3 aspect ratio and hover zoom for card images.
- [x] Updated `docs/dev/blocks-reference.md` with missing fields.
- [x] Created `tests/themes/test_theme_a_portfolio_rendering.py` with structure and logic assertions.
- [x] Rebuilt Theme A CSS using Tailwind v3 toolchain.
- [x] Regenerated Build Fingerprint.
- [x] Verified full test suite pass.

## Verification

Full automated test suite including new rendering tests passed (734/734).

```bash
source .venv/bin/activate && make test
...
================= 734 passed, 45 warnings in 199.35s (0:03:19) =================
```

Modified files:

- `themes/theme_a/templates/sum_core/blocks/portfolio.html`
- `tests/themes/test_theme_a_portfolio_rendering.py`
- `docs/dev/blocks-reference.md`
- `themes/theme_a/static/theme_a/css/main.css`
- `themes/theme_a/static/theme_a/css/.build_fingerprint`
