# Work Order: Visual Regression Testing v1

> **Parent:** [VD v0.8.0](../VD.md)
> **Branch:** `feature/visual-regression`
> **Priority:** P0

---

## Overview

### Goal

Establish automated visual regression testing infrastructure to catch unintended visual changes and validate wireframe parity. This provides a safety net for CSS changes and theme updates.

### Context

Currently, visual quality is verified manually. When CSS or template changes are made, there's no automated way to detect if they inadvertently affect other pages or components. This work order adds visual regression testing to catch these issues before they reach production.

---

## Acceptance Criteria

### Must Have

- [ ] Can capture screenshots of all page types
- [ ] Can compare screenshots against approved baselines
- [ ] Diff generation highlights visual changes
- [ ] Configurable threshold for acceptable difference
- [ ] CI integration fails on significant regressions
- [ ] Baseline approval workflow documented

### Should Have

- [ ] Multiple viewport sizes captured (mobile, tablet, desktop)
- [ ] Screenshots of key component states
- [ ] HTML report with side-by-side comparison
- [ ] Baseline update command

### Could Have

- [ ] Integration with external services (Percy, Chromatic)
- [ ] Automatic baseline updates on approval

---

## Technical Approach

### Tooling Decision: Playwright

Use Playwright for screenshot capture because:
- Already used for end-to-end testing in many projects
- Built-in screenshot comparison
- Cross-browser support
- Headless mode for CI
- Python bindings available

### Screenshot Configuration

```python
# tests/visual/conftest.py
import pytest
from playwright.sync_api import sync_playwright

VIEWPORTS = {
    'mobile': {'width': 375, 'height': 667},
    'tablet': {'width': 768, 'height': 1024},
    'desktop': {'width': 1280, 'height': 800},
}

PAGES_TO_CAPTURE = [
    ('/', 'home'),
    ('/about/', 'about'),
    ('/services/', 'services'),
    ('/blog/', 'blog_index'),
    ('/blog/sample-post/', 'blog_post'),
    ('/contact/', 'contact'),
]
```

### Baseline Management

```
tests/visual/
├── baselines/
│   ├── theme_a/
│   │   ├── desktop/
│   │   │   ├── home.png
│   │   │   ├── about.png
│   │   │   └── ...
│   │   ├── tablet/
│   │   └── mobile/
│   └── theme_b/
│       └── ...
├── diffs/           # Generated, gitignored
├── current/         # Generated, gitignored
├── conftest.py
├── test_visual_regression.py
└── capture_baselines.py
```

### Diff Threshold

Use pixel-based comparison with configurable threshold:

```python
# Default: 0.1% difference allowed for anti-aliasing variance
DIFF_THRESHOLD = 0.001
```

---

## CI Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/visual-regression.yml
name: Visual Regression

on:
  pull_request:
    paths:
      - 'themes/**'
      - 'core/sum_core/templates/**'
      - 'core/sum_core/static/**'

jobs:
  visual-regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
          playwright install chromium
      - name: Run visual regression tests
        run: pytest tests/visual/ --visual-regression
      - name: Upload diff artifacts
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: visual-diffs
          path: tests/visual/diffs/
```

---

## Baseline Workflow

### Initial Baseline Capture

```bash
# Capture baselines for all pages and viewports
python tests/visual/capture_baselines.py --theme theme_a
python tests/visual/capture_baselines.py --theme theme_b
```

### Updating Baselines

When intentional changes are made:

```bash
# Review current screenshots
python tests/visual/capture_baselines.py --theme theme_a --output current

# If changes are correct, update baselines
python tests/visual/capture_baselines.py --theme theme_a --update
```

### Reviewing Diffs

When tests fail:

1. Check CI artifacts for diff images
2. Review side-by-side in HTML report
3. Determine if change is intentional
4. If intentional, update baselines
5. If unintentional, fix the regression

---

## File Changes

### New Files

| File | Purpose |
| ---- | ------- |
| `tests/visual/__init__.py` | Visual test module |
| `tests/visual/conftest.py` | Playwright fixtures, viewport configs |
| `tests/visual/test_visual_regression.py` | Visual comparison tests |
| `tests/visual/capture_baselines.py` | Baseline capture script |
| `tests/visual/baselines/.gitkeep` | Baseline directory |
| `.github/workflows/visual-regression.yml` | CI workflow |
| `docs/dev/VISUAL-TESTING.md` | Documentation |

### Modified Files

| File | Changes |
| ---- | ------- |
| `requirements-dev.txt` | Add playwright |
| `.gitignore` | Add tests/visual/diffs/, tests/visual/current/ |
| `Makefile` | Add visual-test, update-baselines targets |

---

## Tasks

### TASK-001: Select and Configure Tooling

**Estimate:** 2-3 hours
**Risk:** Medium

Set up Playwright and configure for visual testing.

**Acceptance Criteria:**
- [ ] Playwright installed in dev requirements
- [ ] Playwright browsers install correctly
- [ ] Basic screenshot capture works
- [ ] Configuration documented

**Technical Notes:**
- Use `playwright install chromium` for CI
- Consider `pytest-playwright` for integration
- Document local setup requirements

**Branch:** `feature/visual-regression/001-tooling-setup`

---

### TASK-002: Create Screenshot Capture Scripts

**Estimate:** 3-4 hours
**Risk:** Medium

Create scripts to capture screenshots of all pages at all viewports.

**Acceptance Criteria:**
- [ ] Can capture single page screenshot
- [ ] Can capture all pages for a theme
- [ ] Supports multiple viewports
- [ ] Screenshots named consistently
- [ ] Server startup handled automatically

**Technical Notes:**
- Use Django's test server or runserver
- Wait for page load before capture
- Handle dynamic content (hide timestamps, etc.)

**Branch:** `feature/visual-regression/002-screenshot-capture`

---

### TASK-003: Implement Baseline Management

**Estimate:** 2-3 hours
**Risk:** Low

Create baseline storage and update workflow.

**Acceptance Criteria:**
- [ ] Baselines stored in git-tracked directory
- [ ] Baseline update command works
- [ ] Can update single page or all pages
- [ ] Clear directory structure per theme/viewport

**Technical Notes:**
- Store baselines in `tests/visual/baselines/`
- Use PNG format for lossless comparison
- Document baseline update workflow

**Branch:** `feature/visual-regression/003-baseline-management`

---

### TASK-004: Create Diff Generation and Reporting

**Estimate:** 2-4 hours
**Risk:** Medium

Implement image comparison and diff visualization.

**Acceptance Criteria:**
- [ ] Pixel-by-pixel comparison works
- [ ] Diff images generated highlighting changes
- [ ] Threshold configurable
- [ ] HTML report with side-by-side view
- [ ] Percentage difference reported

**Technical Notes:**
- Use Pillow for image comparison
- Generate diff overlay image
- Create simple HTML report template

**Branch:** `feature/visual-regression/004-diff-reporting`

---

### TASK-005: CI Integration

**Estimate:** 2-3 hours
**Risk:** Medium

Set up GitHub Actions workflow for visual regression testing.

**Acceptance Criteria:**
- [ ] Workflow triggers on relevant file changes
- [ ] Tests run in CI environment
- [ ] Diff artifacts uploaded on failure
- [ ] Clear failure messages in PR

**Technical Notes:**
- Use matrix for themes if needed
- Cache Playwright browsers
- Upload artifacts for debugging

**Branch:** `feature/visual-regression/005-ci-integration`

---

### TASK-006: Documentation and Workflow Guide

**Estimate:** 1-3 hours
**Risk:** Low

Document the visual regression testing workflow.

**Acceptance Criteria:**
- [ ] Setup guide for local development
- [ ] Baseline update workflow documented
- [ ] Diff review process explained
- [ ] Troubleshooting section
- [ ] CI integration explained

**Technical Notes:**
- Add to docs/dev/VISUAL-TESTING.md
- Include screenshots in documentation
- Link from HANDBOOK.md

**Branch:** `feature/visual-regression/006-documentation`

---

## Execution Order

```
001 (Tooling Setup)
    |
    v
002 (Screenshot Capture)
    |
    v
003 (Baseline Management)
    |
    v
004 (Diff Reporting)
    |
    v
005 (CI Integration)
    |
    v
006 (Documentation)
```

### Sequential Dependency

Each task builds on the previous. Limited parallelization opportunity.

---

## Testing Requirements

### Unit Tests

- Diff calculation logic
- Threshold comparison
- Path generation

### Integration Tests

- Full capture and compare cycle
- Baseline update workflow
- CI workflow (local simulation)

---

## Definition of Done

- [ ] All 6 tasks completed and merged
- [ ] All acceptance criteria met
- [ ] Can capture screenshots locally
- [ ] Can compare against baselines
- [ ] CI workflow triggers and runs
- [ ] Documentation complete
- [ ] Initial baselines captured for Elysian
- [ ] PR merged to `release/0.8.0`

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
| ---- | ---------- | ------ | ---------- |
| Flaky tests due to rendering variance | Medium | Medium | Threshold tuning, stable viewports |
| Large baseline files in git | Low | Low | Compress PNGs, consider LFS if needed |
| Slow CI due to screenshot capture | Medium | Low | Parallel capture, selective running |
| Dynamic content causes false positives | Medium | Medium | Hide timestamps, use seeded data |

---

## Sign-Off

| Role | Name | Date | Approved |
| ---- | ---- | ---- | -------- |
| Author | Claude-on-WSL | 2025-12-30 | - |
| Tech Lead | | | Pending |

---

## Revision History

| Date | Author | Changes |
| ---- | ------ | ------- |
| 2025-12-30 | Claude-on-WSL | Initial WO created |
