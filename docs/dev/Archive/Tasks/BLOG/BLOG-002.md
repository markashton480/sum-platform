# BLOG.002: Form Field Type Blocks

**Phase:** 1 - Dynamic Forms Foundation  
**Priority:** P1 (Critical Path)  
**Estimated Hours:** 11h  
**Dependencies:** BLOG.001

## Pre-Implementation

**Branch from issue:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/BLOG-002-field-type-blocks
```

## Objective

Create Wagtail StreamField blocks that define the field types available in `FormDefinition`. These blocks provide the schema for runtime Django form generation and enable content editors to build forms visually.

## References

- Implementation Plan: `@/home/mark/workspaces/sum-platform/docs/dev/master-docs/IMPLEMENTATION-PLAN-BLOG-DYNAMICFORMS-v1.md:125-161`
- Wagtail Blocks Documentation: https://docs.wagtail.org/en/stable/topics/streamfield.html
- Existing Blocks: `core/sum_core/blocks/`
- Repository Guidelines: `@/home/mark/workspaces/sum-platform/AGENTS.md`

## Technical Specification

### Location
- **New File:** `core/sum_core/forms/fields.py`

### Base Block Structure

Create `FormFieldBlock` (StructBlock) with common properties:
```python
class FormFieldBlock(blocks.StructBlock):
    field_name = blocks.SlugBlock(required=True, help_text="Unique field identifier (e.g., 'email', 'phone')")
    label = blocks.CharBlock(required=True, help_text="Field label shown to users")
    help_text = blocks.CharBlock(required=False, help_text="Optional help text below field")
    required = blocks.BooleanBlock(required=False, default=True, help_text="Mark field as required")
    css_class = blocks.CharBlock(required=False, help_text="Optional CSS classes for styling")
```

### Input Field Blocks

Implement these field types extending `FormFieldBlock`:

1. **TextInputBlock**
   - `max_length` (IntegerBlock, default=255)
   - `placeholder` (CharBlock, optional)

2. **EmailInputBlock**
   - Inherits from TextInputBlock
   - Built-in email validation pattern

3. **PhoneInputBlock**
   - `format_mask` (CharBlock, optional, e.g., "(###) ###-####")
   - `placeholder` (CharBlock, optional)

4. **TextareaBlock**
   - `rows` (IntegerBlock, default=4)
   - `max_length` (IntegerBlock, optional)
   - `placeholder` (CharBlock, optional)

5. **SelectBlock** (custom implementation)
   - `choices` (StreamBlock of ChoiceOptionBlock)
   - `allow_multiple` (BooleanBlock, default=False)

6. **CheckboxBlock**
   - Single checkbox with custom label
   - `checked_value` (CharBlock, default="yes")

7. **CheckboxGroupBlock**
   - `choices` (StreamBlock of ChoiceOptionBlock)
   - Allows multiple selections

8. **RadioButtonsBlock**
   - `choices` (StreamBlock of ChoiceOptionBlock)
   - Single selection only

9. **FileUploadBlock**
   - `allowed_extensions` (CharBlock, e.g., ".pdf,.doc,.docx")
   - `max_file_size_mb` (IntegerBlock, default=10)

### Layout Blocks (Non-Input)

10. **SectionHeadingBlock**
    - `heading` (CharBlock)
    - `level` (ChoiceBlock: h2, h3, h4)

11. **HelpTextBlock**
    - `text` (RichTextBlock)
    - Visual instructions/descriptions

### Supporting Blocks

Create `ChoiceOptionBlock` (StructBlock):
- `value` (CharBlock) - submitted value
- `label` (CharBlock) - display text

### Block Collection Export

```python
FORM_FIELD_BLOCKS = [
    ('text_input', TextInputBlock()),
    ('email_input', EmailInputBlock()),
    ('phone_input', PhoneInputBlock()),
    ('textarea', TextareaBlock()),
    ('select', SelectBlock()),
    ('checkbox', CheckboxBlock()),
    ('checkbox_group', CheckboxGroupBlock()),
    ('radio_buttons', RadioButtonsBlock()),
    ('file_upload', FileUploadBlock()),
    ('section_heading', SectionHeadingBlock()),
    ('help_text', HelpTextBlock()),
]
```

## Implementation Tasks

- [ ] Create `core/sum_core/forms/fields.py`
- [ ] Import required Wagtail blocks modules
- [ ] Implement `FormFieldBlock` base class
- [ ] Implement `ChoiceOptionBlock`
- [ ] Implement all 9 input field blocks with specific options
- [ ] Implement 2 layout blocks
- [ ] Define `FORM_FIELD_BLOCKS` list export
- [ ] Update `FormDefinition.fields` in BLOG.001 to use `FORM_FIELD_BLOCKS`
- [ ] Create migration: `python manage.py makemigrations sum_core`
- [ ] Write comprehensive unit tests in `tests/forms/test_field_blocks.py`:
  - Each block type instantiation
  - Block validation rules
  - Required field enforcement
  - Choice blocks with options
  - Max length constraints
  - File upload restrictions

## Acceptance Criteria

- [ ] All 11 block types defined and importable
- [ ] `FORM_FIELD_BLOCKS` correctly exports all blocks
- [ ] FormDefinition admin now shows field blocks in StreamField
- [ ] Each block validates its specific constraints
- [ ] Migration runs cleanly
- [ ] Unit tests pass with ≥80% coverage for each block type
- [ ] `make lint` passes
- [ ] Can create a FormDefinition with mixed field types in admin

## Testing Commands

```bash
# Run unit tests
pytest tests/forms/test_field_blocks.py -v

# Check coverage
pytest tests/forms/test_field_blocks.py --cov=core/sum_core/forms/fields --cov-report=term-missing

# Interactive test in admin
python core/sum_core/test_project/manage.py runserver
# Navigate to /admin/snippets/forms/formdefinition/create/

# Run linting
make lint
```

## Post-Implementation

**Commit, push, and create PR:**
```bash
git add .
git commit -m "feat(forms): add form field type blocks

- Implement 9 input field block types
- Add section heading and help text layout blocks
- Create base FormFieldBlock with common properties
- Support choice-based fields (select, radio, checkbox group)
- Add file upload with extension/size validation
- Update FormDefinition to use FORM_FIELD_BLOCKS
- Add comprehensive unit tests

Refs: BLOG.002"

git push origin feature/BLOG-002-field-type-blocks

gh pr create \
  --base develop \
  --title "feat(forms): Form field type blocks" \
  --body "Implements BLOG.002 - Field type blocks for dynamic form builder.

## Changes
- 11 StreamField blocks for form field definitions
- Base FormFieldBlock with common properties
- Choice option blocks for select/radio/checkbox
- File upload constraints
- Unit tests for all block types

## Testing
- ✅ All block types instantiate correctly
- ✅ Validation rules work
- ✅ FormDefinition admin shows StreamField editor
- ✅ Lint checks pass

## Related
- Depends on: BLOG.001
- Blocks on: BLOG.003 (DynamicFormBlock)"
```

**Monitor CI and resolve review comments:**
```bash
gh pr status
gh pr checks --watch
# Address feedback, push fixes, resolve conversations
```

## Notes for AI Agents

- **Critical path** task - required for BLOG.003
- Follow existing block patterns in `core/sum_core/blocks/`
- Ensure block icons and labels are user-friendly for content editors
- File upload will integrate with existing media handling
- Choice blocks must support dynamic addition/removal of options
- Keep block definitions simple - complex validation happens in BLOG.004
