# WO: Link Health Tooling (v0.7.0)

## Metadata

- **Version:** v0.7.0
- **Component:** core
- **Priority:** P1 (If Time Permits)
- **Branch:** `feature/link-health`
- **Parent VD:** #TBD
- **Issue:** #TBD

---

## Description

Add management command and reporting for detecting broken internal links across the site. This pairs with WO3 (Internal Linking) to provide editors with tools to maintain link health. The tool should detect links to deleted pages, unpublished pages, and potentially invalid anchor references.

**Why this matters:**
- Internal links can break when pages are deleted or unpublished
- Editors need visibility into link health
- Broken links hurt SEO and user experience
- Proactive detection prevents embarrassing broken links

**Priority Note:** This is P1 (optional) - only proceed if P0 items are complete or on track.

---

## Acceptance Criteria

- [ ] `manage.py check_links` command exists and runs
- [ ] Command detects broken page references
- [ ] Command detects links to unpublished pages
- [ ] Output is clear and actionable
- [ ] Optional JSON output for tooling integration
- [ ] Documentation for running and interpreting results

---

## Deliverables

1. **Management Command**
   - `check_links` command in sum_core
   - Console output with clear formatting
   - Optional `--format json` for machine-readable output
   - Optional `--fix` suggestions (future)

2. **Link Scanner**
   - Scan all StreamFields for UniversalLinkBlock
   - Check page references are valid
   - Check pages are published
   - Report broken/problematic links

3. **Report Output**
   - List of broken links with location
   - List of links to unpublished pages
   - Summary statistics
   - Actionable recommendations

---

## Technical Approach

### Command Structure

```python
# core/sum_core/management/commands/check_links.py

from django.core.management.base import BaseCommand
from wagtail.models import Page
from sum_core.links.scanner import LinkScanner

class Command(BaseCommand):
    help = 'Check for broken internal links across the site'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            choices=['text', 'json'],
            default='text',
            help='Output format'
        )
        parser.add_argument(
            '--include-unpublished',
            action='store_true',
            help='Include links to unpublished pages'
        )

    def handle(self, *args, **options):
        scanner = LinkScanner()
        results = scanner.scan_all_pages()

        if options['format'] == 'json':
            self.output_json(results)
        else:
            self.output_text(results)
```

### Link Scanner

```python
# core/sum_core/links/scanner.py

class LinkScanner:
    def scan_all_pages(self):
        results = {
            'broken': [],
            'unpublished': [],
            'valid': 0,
            'total': 0,
        }

        for page in Page.objects.live().specific():
            page_results = self.scan_page(page)
            # Aggregate results...

        return results

    def scan_page(self, page):
        # Find all StreamFields on the page
        # Recursively scan blocks for UniversalLinkBlock
        # Check each link target
        pass
```

---

## Boundaries

### Do

- Create management command with clear output
- Scan all pages with StreamFields
- Detect broken and unpublished page links
- Provide actionable output
- Support JSON output for tooling
- Write tests for scanner logic

### Do NOT

- Add admin dashboard integration (defer)
- Add automatic link repair
- Scan external URLs (different tool)
- Add scheduled scanning
- Add email notifications

---

## Subtasks

### TASK-001: Create Link Scanner Core

**Description:**
Create the LinkScanner class that can recursively scan StreamFields and extract all UniversalLinkBlock instances with their targets.

**Acceptance Criteria:**
- [ ] LinkScanner class in `core/sum_core/links/`
- [ ] Can scan a single page for links
- [ ] Recursively handles nested blocks
- [ ] Extracts link type and target
- [ ] Returns structured results

**Boundaries:**
- Do: Handle all block nesting levels
- Do: Handle all UniversalLinkBlock link types
- Do NOT: Validate external URLs
- Do NOT: Follow redirects

**Branch:** `feature/link-health/001-link-scanner`

---

### TASK-002: Create check_links Command

**Description:**
Create the Django management command that uses LinkScanner to check all pages and output results.

**Acceptance Criteria:**
- [ ] `manage.py check_links` runs successfully
- [ ] Scans all live pages
- [ ] Reports broken links with page location
- [ ] Reports links to unpublished pages
- [ ] Clear console output

**Boundaries:**
- Do: Use LinkScanner from TASK-001
- Do: Handle large sites efficiently
- Do NOT: Add progress bars (keep simple)
- Do NOT: Add database writes

**Branch:** `feature/link-health/002-check-links-command`

---

### TASK-003: Add JSON Output Format

**Description:**
Add `--format json` option to check_links command for machine-readable output.

**Acceptance Criteria:**
- [ ] `--format json` outputs valid JSON
- [ ] JSON structure is documented
- [ ] Includes all link details
- [ ] Suitable for CI/CD integration

**Boundaries:**
- Do: Output well-structured JSON
- Do: Include source page, block path, target
- Do NOT: Add complex filtering options
- Do NOT: Add streaming JSON output

**Branch:** `feature/link-health/003-json-output`

---

### TASK-004: Link Health Tests

**Description:**
Add comprehensive tests for LinkScanner and check_links command.

**Acceptance Criteria:**
- [ ] Tests for LinkScanner with various block types
- [ ] Tests for broken link detection
- [ ] Tests for unpublished page detection
- [ ] Tests for JSON output format
- [ ] Tests for edge cases (empty pages, no links)

**Boundaries:**
- Do: Test all link types
- Do: Test nested blocks
- Do NOT: Test performance
- Do NOT: Add integration tests with real pages

**Branch:** `feature/link-health/004-tests`

---

### TASK-005: Documentation

**Description:**
Document the check_links command usage, output interpretation, and recommended workflows.

**Acceptance Criteria:**
- [ ] Command usage documented
- [ ] Output format documented
- [ ] Common workflows described
- [ ] CI/CD integration examples
- [ ] Added to HANDBOOK.md or similar

**Boundaries:**
- Do: Provide clear examples
- Do: Explain what each status means
- Do NOT: Over-document
- Do NOT: Promise future features

**Branch:** `feature/link-health/005-documentation`

---

## Merge Order

1. TASK-001 (Scanner Core) - foundational
2. TASK-002 (Command) - depends on 001
3. TASK-003 (JSON Output) - depends on 002
4. TASK-004 (Tests) - can start after 001, finish after 003
5. TASK-005 (Documentation) - after 002-003

---

## Estimated Effort

| Task | Estimate | Risk |
| ---- | -------- | ---- |
| TASK-001 | 3-4 hours | Medium |
| TASK-002 | 2-3 hours | Low |
| TASK-003 | 1-2 hours | Low |
| TASK-004 | 2-3 hours | Low |
| TASK-005 | 1-2 hours | Low |

**Total:** 9-14 hours

---

## Dependencies

- WO3 (Internal Linking) should be complete or in progress
- Understanding of UniversalLinkBlock structure required

---

## Future Considerations (Not in Scope)

- Admin dashboard widget showing link health
- Scheduled scanning with notifications
- External URL checking
- Automatic link repair suggestions
- Broken link redirect creation

---

## Notes

- This is P1 - don't delay P0 work for this
- Focus on detection, not repair
- JSON output enables future tooling
- Consider CI/CD integration as primary use case
- Keep scope minimal - this is a utility tool
