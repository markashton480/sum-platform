# THEME-037: Create PageHeaderBlock (breadcrumbs + interior header)

## Context
Theme A needs an interior page header block with breadcrumbs for consistent page
headers on about/portfolio/blog list/etc.

## Objective
- Add `PageHeaderBlock` to `sum_core` and register it in `PageStreamBlock`.
- Provide Theme A override template.
- Document the block and cover it with theme contract tests.

## Key Files
- `core/sum_core/blocks/content.py`
- `core/sum_core/blocks/base.py`
- `core/sum_core/templates/sum_core/blocks/page_header.html`
- `themes/theme_a/templates/sum_core/blocks/page_header.html`
- `tests/themes/test_theme_a_block_contracts.py`
- `docs/dev/blocks-reference.md`

## Issue
- https://github.com/markashton480/sum_platform/issues/76
