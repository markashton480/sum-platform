# Subtask

**Title:** `CLI-005: seed_homepage Management Command (sum_core)`

---

## Parent

**Work Order:** #WO-CLI-V2 — CLI v2 Enhanced Architecture (v2.0.0)

---

## Branch

| Branch | Target |
|--------|--------|
| `feature/cli-v2/005-seed-homepage-cmd` | `feature/cli-v2` |

```bash
git checkout feature/cli-v2
git pull origin feature/cli-v2
git checkout -b feature/cli-v2/005-seed-homepage-cmd
git push -u origin feature/cli-v2/005-seed-homepage-cmd
```

---

## Deliverable

This subtask will deliver:

- `core/sum_core/management/commands/seed_homepage.py` — Django management command for seeding homepage
- `tests/sum_core/test_seed_homepage.py` — Unit tests for the command

---

## Boundaries

### Do

- Implement `seed_homepage` management command with:
  - `--preset` argument for future theme preset support (Phase 2 prep)
  - `--force` flag to recreate homepage even if exists
  - Idempotent behavior (skip if homepage exists unless `--force`)
- Create `HomePage` instance with default content:
  - title: "Welcome"
  - slug: "home"
  - seo_title: "Home"
  - search_description: "Welcome to our website"
  - StreamField body with hero_gradient and rich_text blocks
- Add homepage as child of root page
- **Publish the homepage** so it's live (call `save_revision().publish()`)
- Set homepage as site root page
- **When `--force` deleting:** Update site root to Wagtail root page FIRST, then delete, to avoid dangling reference
- Print success message with homepage ID and URL

### Do NOT

- ❌ Do not implement CLI integration — owned by #CLI-006
- ❌ Do not implement preset loading logic — Phase 4 (future)
- ❌ Do not modify any CLI files
- ❌ Do not create client-specific seed configurations

---

## Acceptance Criteria

- [ ] `python manage.py seed_homepage` creates homepage with default content
- [ ] Command is idempotent — running twice shows warning and skips creation
- [ ] `--force` flag deletes existing homepage and recreates
- [ ] **`--force` safely updates site root before deletion** to avoid dangling reference
- [ ] Homepage is added as child of Wagtail root page
- [ ] **Homepage is published** (not just created as draft)
- [ ] Homepage is set as default site's root page
- [ ] Success message includes homepage ID: `✅ Homepage created successfully (ID: X)`
- [ ] Success message includes URL: `URL: http://127.0.0.1:8000/`
- [ ] Default content includes `hero_gradient` block with:
  - headline: "Welcome to Your New Site"
  - subheadline: "Your professional website is ready to customize."
- [ ] Default content includes `rich_text` block with placeholder text
- [ ] `--preset` argument is accepted (for future use, currently no-op)
- [ ] Unit tests verify command behavior
- [ ] `make lint && make test` passes in sum_core

---

## Test Commands

```bash
make lint
make test

# Specific tests
python -m pytest tests/sum_core/test_seed_homepage.py -v

# Manual test in client project
cd clients/test-project
source .venv/bin/activate
python manage.py seed_homepage
python manage.py seed_homepage  # Should show "already exists"
python manage.py seed_homepage --force  # Should recreate
```

---

## Files Expected to Change

```
core/sum_core/management/__init__.py           # Ensure exists
core/sum_core/management/commands/__init__.py  # Ensure exists
core/sum_core/management/commands/seed_homepage.py  # New
tests/sum_core/test_seed_homepage.py           # New
```

---

## Dependencies

**Depends On:**
- [ ] None — this is a sum_core change independent of CLI tasks
- [ ] Assumes `home.models.HomePage` exists with StreamField body
- [ ] Assumes `hero_gradient` and `rich_text` block types exist

**Blocks:**
- #CLI-006 Seeding & Orchestrator is waiting for this

---

## Risk

**Level:** Medium

**Why:**
- Cross-component work (sum_core ↔ CLI integration in #CLI-006)
- Depends on existing HomePage model structure
- Depends on StreamField block types being available
- Wagtail page tree manipulation requires care

---

## Labels

- [ ] `type:task`
- [ ] `agent:*`
- [ ] `component:sum-core`
- [ ] `risk:medium`
- [ ] Milestone: `v2.0.0`

---

## Project Fields

- [ ] Agent: (assigned)
- [ ] Model Planned: (selected)
- [ ] Component: sum-core
- [ ] Change Type: feat
- [ ] Risk: medium
- [ ] Release: `v2.0.0`

---

## Definition of Done

- [ ] Acceptance criteria met
- [ ] `make lint && make test` passes
- [ ] PR merged to feature branch
- [ ] **Model Used** field set
- [ ] `model:*` label applied
- [ ] Parent Work Order updated

---

## Commit Message

```
feat(sum-core): add seed_homepage management command

- Add management command to create initial homepage
- Support --force flag for recreation
- Support --preset argument (prep for Phase 2)
- Set homepage as site root automatically
- Include default hero_gradient and rich_text blocks

Closes #CLI-005
```

---

## Implementation Notes

### Command Structure

```python
"""
File: core/sum_core/management/commands/seed_homepage.py
Name: seed_homepage command
Purpose: Create initial homepage for new client projects
Dependencies: wagtail.models, home.models
Family: Django management command, called by CLI orchestrator
"""

from typing import Any, Optional

from django.core.management.base import BaseCommand
from wagtail.models import Page, Site

from home.models import HomePage


class Command(BaseCommand):
    help = 'Seed initial homepage for a new client project'

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--preset',
            type=str,
            help='Theme preset name (premium-trade, professional-blue, etc.)',
            required=False
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Recreate homepage even if it exists'
        )

    def handle(self, *args: Any, **options: Any) -> None:
        preset: Optional[str] = options.get('preset')
        force: bool = options.get('force', False)
        
        # Check if homepage already exists
        existing = HomePage.objects.filter(slug='home').first()
        
        if existing and not force:
            self.stdout.write(
                self.style.WARNING(
                    f'Homepage already exists (ID: {existing.id}). '
                    'Use --force to recreate.'
                )
            )
            return
        
        if existing and force:
            self.stdout.write('Removing existing homepage...')
            # IMPORTANT: Update site root FIRST to avoid dangling reference
            site = Site.objects.get(is_default_site=True)
            root = Page.get_first_root_node()
            if site.root_page_id == existing.id:
                site.root_page = root
                site.save()
            existing.delete()
        
        # Get root page
        root = Page.get_first_root_node()
        
        # Create homepage with appropriate content
        homepage = HomePage(
            title="Welcome",
            slug="home",
            seo_title="Home",
            search_description="Welcome to our website",
            body=self._get_default_content(preset)
        )
        
        root.add_child(instance=homepage)
        
        # IMPORTANT: Publish the page so it's live (not just a draft)
        homepage.save_revision().publish()
        
        # Set as site root
        site = Site.objects.get(is_default_site=True)
        site.root_page = homepage
        site.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Homepage created successfully (ID: {homepage.id})'
            )
        )
        self.stdout.write(f'   URL: http://127.0.0.1:8000/')

    def _get_default_content(self, preset: Optional[str]) -> list:
        """Get default StreamField content for homepage."""
        # Future: Load from preset configuration
        return [
            {
                'type': 'hero_gradient',
                'value': {
                    'headline': 'Welcome to Your New Site',
                    'subheadline': 'Your professional website is ready to customize.',
                    'cta_buttons': []
                }
            },
            {
                'type': 'rich_text',
                'value': '<p>This is your homepage. Edit this content in the Wagtail admin.</p>'
            }
        ]
```

### Test Strategy

```python
import pytest
from io import StringIO
from django.core.management import call_command
from wagtail.models import Page, Site

from home.models import HomePage

@pytest.mark.django_db
class TestSeedHomepageCommand:
    
    def test_creates_homepage(self) -> None:
        """Test that command creates homepage."""
        out = StringIO()
        call_command('seed_homepage', stdout=out)
        
        assert HomePage.objects.filter(slug='home').exists()
        assert '✅ Homepage created successfully' in out.getvalue()
    
    def test_idempotent_without_force(self) -> None:
        """Test that command skips if homepage exists."""
        call_command('seed_homepage')
        
        out = StringIO()
        call_command('seed_homepage', stdout=out)
        
        assert 'already exists' in out.getvalue()
        assert HomePage.objects.filter(slug='home').count() == 1
    
    def test_force_recreates(self) -> None:
        """Test that --force recreates homepage."""
        call_command('seed_homepage')
        original_id = HomePage.objects.get(slug='home').id
        
        call_command('seed_homepage', force=True)
        new_id = HomePage.objects.get(slug='home').id
        
        assert new_id != original_id
    
    def test_sets_as_site_root(self) -> None:
        """Test that homepage is set as site root."""
        call_command('seed_homepage')
        
        site = Site.objects.get(is_default_site=True)
        assert site.root_page.slug == 'home'
```
