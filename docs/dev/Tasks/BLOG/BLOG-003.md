# BLOG.003: DynamicFormBlock Implementation

**Phase:** 1 - Dynamic Forms Foundation  
**Priority:** P1 (Critical Path)  
**Estimated Hours:** 6h  
**Dependencies:** BLOG.001, BLOG.002

## Pre-Implementation

**Branch from issue:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/BLOG-003-dynamic-form-block
```

## Objective

Create the `DynamicFormBlock` StructBlock that allows content editors to embed `FormDefinition` instances into any page's StreamField. This is the primary mechanism for placing forms throughout the site and is **critical** for blog CTA integration.

## References

- Implementation Plan: `@/home/mark/workspaces/sum-platform/docs/dev/master-docs/IMPLEMENTATION-PLAN-BLOG-DYNAMICFORMS-v1.md:163-187`
- Wagtail SnippetChooserBlock: https://docs.wagtail.org/en/stable/reference/streamfield/blocks.html#snippetchooserblock
- Existing Blocks: `core/sum_core/blocks/`
- Repository Guidelines: `@/home/mark/workspaces/sum-platform/AGENTS.md`

## Technical Specification

### Location
- **File:** `core/sum_core/blocks/forms.py`

### Block Definition

Create `DynamicFormBlock` (StructBlock):

```python
class DynamicFormBlock(blocks.StructBlock):
    form_definition = SnippetChooserBlock(
        'forms.FormDefinition',
        required=True,
        help_text="Select the form to display"
    )
    presentation_style = blocks.ChoiceBlock(
        choices=[
            ('inline', 'Inline (renders in page flow)'),
            ('modal', 'Modal (button opens overlay)'),
            ('sidebar', 'Sidebar (fixed slide-in)'),
        ],
        default='inline',
        help_text="How the form should be presented"
    )
    cta_button_text = blocks.CharBlock(
        required=False,
        max_length=100,
        help_text="Override default CTA button text (for modal/sidebar styles)"
    )
    success_redirect_url = blocks.URLBlock(
        required=False,
        help_text="Optional redirect after submission (defaults to same page with message)"
    )
    
    class Meta:
        icon = 'form'
        label = 'Dynamic Form'
        template = 'sum_core/blocks/dynamic_form_block.html'
```

### Integration with Existing Pages

Update `core/sum_core/blocks/__init__.py`:
- Import `DynamicFormBlock`
- Add to `ALL_BLOCKS` or relevant block collections

Update StreamField definitions:
- **StandardPage** (`core/sum_core/pages/standard.py`): Add to `body` StreamField
- **ServicePage** (if exists): Add to `body` StreamField
- Verify existing pages can use the block without migration issues

### Template Placeholder

Create minimal template placeholder:
- **File:** `themes/theme_a/templates/sum_core/blocks/dynamic_form_block.html`
- Content: Simple placeholder rendering block data (full implementation in BLOG.006)

```html
{# Placeholder - full implementation in BLOG.006 #}
<div class="dynamic-form-block" data-style="{{ self.presentation_style }}">
    <p><strong>Form:</strong> {{ self.form_definition.name }}</p>
    <p><em>Form rendering will be implemented in BLOG.006</em></p>
</div>
```

## Implementation Tasks

- [ ] Create/update `core/sum_core/blocks/forms.py`
- [ ] Implement `DynamicFormBlock` StructBlock with all fields
- [ ] Add block to `core/sum_core/blocks/__init__.py` exports
- [ ] Update `StandardPage.body` StreamField to include DynamicFormBlock
- [ ] Update `ServicePage.body` if it exists
- [ ] Create placeholder template in `themes/theme_a/templates/sum_core/blocks/`
- [ ] Create migration: `python manage.py makemigrations sum_core`
- [ ] Write unit tests in `tests/blocks/test_dynamic_form_block.py`:
  - Block instantiation
  - FormDefinition chooser works
  - Presentation style options
  - Optional fields (CTA text, redirect URL)
  - Block rendering with placeholder template

## Acceptance Criteria

- [ ] `DynamicFormBlock` appears in page StreamField editors
- [ ] Can select FormDefinition from snippet chooser
- [ ] All presentation styles selectable
- [ ] Optional fields work (can be blank)
- [ ] Placeholder template renders without errors
- [ ] Migration runs cleanly
- [ ] Existing pages not broken by new block addition
- [ ] Unit tests pass with ≥80% coverage
- [ ] `make lint` passes

## Testing Commands

```bash
# Run unit tests
pytest tests/blocks/test_dynamic_form_block.py -v

# Check coverage
pytest tests/blocks/test_dynamic_form_block.py --cov=core/sum_core/blocks/forms --cov-report=term-missing

# Interactive test
python core/sum_core/test_project/manage.py runserver
# Create a FormDefinition in admin
# Edit a StandardPage and add DynamicFormBlock
# Verify chooser and options work

# Run linting
make lint
```

## Post-Implementation

**Commit, push, and create PR:**
```bash
git add .
git commit -m "feat(blocks): add DynamicFormBlock for form embedding

- Create DynamicFormBlock with FormDefinition chooser
- Support inline, modal, and sidebar presentation styles
- Add optional CTA text and redirect URL overrides
- Integrate with StandardPage and ServicePage
- Add placeholder template for rendering
- Include unit tests and migration

Refs: BLOG.003"

git push origin feature/BLOG-003-dynamic-form-block

gh pr create \
  --base develop \
  --title "feat(blocks): DynamicFormBlock for form embedding" \
  --body "Implements BLOG.003 - Block for embedding FormDefinitions in pages.

## Changes
- DynamicFormBlock StructBlock with SnippetChooserBlock
- Three presentation styles: inline, modal, sidebar
- Optional CTA and redirect overrides
- Integration with existing page StreamFields
- Placeholder template (full rendering in BLOG.006)
- Unit tests and migration

## Testing
- ✅ Block appears in admin StreamField editor
- ✅ FormDefinition chooser works
- ✅ All options configurable
- ✅ Placeholder renders
- ✅ Lint checks pass

## Related
- Depends on: BLOG.001, BLOG.002
- Blocks on: BLOG.006 (form rendering), BLOG.011 (BlogPostPage integration)"
```

**Monitor CI and resolve review comments:**
```bash
gh pr status
gh pr checks --watch
# Address feedback, ensure all conversations resolved
```

## Notes for AI Agents

- **Critical path** task - required for blog CTA integration
- Placeholder template is intentional - full rendering comes in Phase 2
- Ensure only **active** FormDefinitions appear in chooser (filter in block or admin)
- Consider adding a `get_context()` method if needed for template rendering
- This block will be used heavily in BlogPostPage (BLOG.011)
- Verify backward compatibility with existing form blocks (ContactFormBlock, etc.)
