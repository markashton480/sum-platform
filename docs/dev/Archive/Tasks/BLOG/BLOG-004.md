# BLOG.004: Runtime Django Form Generation

**Phase:** 2 - Forms Rendering + Submission  
**Priority:** P1 (Critical Path)  
**Estimated Hours:** 11h  
**Dependencies:** BLOG.002

## Pre-Implementation

**Branch from issue:**
```bash
git checkout develop
git pull origin develop
git checkout -b feature/BLOG-004-form-generation
```

## Objective

Create the `DynamicFormGenerator` that converts `FormDefinition` StreamField blocks into runtime Django Form classes. This is the engine that powers dynamic form rendering and validation.

## References

- Implementation Plan: `@/home/mark/workspaces/sum-platform/docs/dev/master-docs/IMPLEMENTATION-PLAN-BLOG-DYNAMICFORMS-v1.md:195-224`
- Django Forms Documentation: https://docs.djangoproject.com/en/stable/topics/forms/
- Django Dynamic Form Creation: https://docs.djangoproject.com/en/stable/ref/forms/fields/
- Existing Forms: `core/sum_core/forms/`
- Repository Guidelines: `@/home/mark/workspaces/sum-platform/AGENTS.md`

## Technical Specification

### Location
- **New File:** `core/sum_core/forms/dynamic.py`

### DynamicFormGenerator Class

```python
class DynamicFormGenerator:
    """
    Generates Django Form classes from FormDefinition at runtime.
    
    Usage:
        generator = DynamicFormGenerator(form_definition)
        FormClass = generator.generate_form_class()
        form = FormClass(data=request.POST)
    """
    
    def __init__(self, form_definition):
        self.form_definition = form_definition
    
    def generate_form_class(self):
        """Returns a Django Form class with fields from FormDefinition."""
        pass
    
    def _map_block_to_field(self, block_type, block_value):
        """Maps a FormFieldBlock to a Django form field."""
        pass
```

### Field Type Mapping

Map FormFieldBlock types to Django fields:

| Block Type | Django Field | Widget | Notes |
|------------|--------------|--------|-------|
| TextInputBlock | CharField | TextInput | Use max_length from block |
| EmailInputBlock | EmailField | EmailInput | Built-in email validation |
| PhoneInputBlock | CharField | TextInput | Optional: add format mask via attrs |
| TextareaBlock | CharField | Textarea | Set rows via widget attrs |
| SelectBlock | ChoiceField or MultipleChoiceField | Select or SelectMultiple | Based on allow_multiple |
| CheckboxBlock | BooleanField | CheckboxInput | Single checkbox |
| CheckboxGroupBlock | MultipleChoiceField | CheckboxSelectMultiple | From choices |
| RadioButtonsBlock | ChoiceField | RadioSelect | From choices |
| FileUploadBlock | FileField | FileInput | Validate extensions and size |
| SectionHeadingBlock | N/A | N/A | Skip - layout only |
| HelpTextBlock | N/A | N/A | Skip - layout only |

### Validation Rules

Preserve from block configuration:
- Required/optional status
- Max length constraints
- Email format validation
- File size limits (validate in clean method)
- File extension whitelist (validate in clean method)
- Custom CSS classes (add to widget attrs)

### Form Class Generation

Generate form with:
- Dynamic field names from `field_name` block property
- Proper field ordering (preserve StreamField order)
- Help text from blocks
- Custom widget attributes (CSS classes, placeholders)
- Form-level validation for file uploads

## Implementation Tasks

- [ ] Create `core/sum_core/forms/dynamic.py`
- [ ] Implement `DynamicFormGenerator` class
- [ ] Implement `generate_form_class()` method:
  - Iterate through form_definition.fields StreamField
  - Build fields dict mapping field_name to Django field instance
  - Use `type()` to create Form class dynamically
  - Preserve field order
- [ ] Implement `_map_block_to_field()` for each block type
- [ ] Handle choice-based fields (extract options from StreamBlock)
- [ ] Add form-level `clean()` method for file validation
- [ ] Handle layout blocks (skip, don't create fields)
- [ ] Add caching mechanism (optional, for performance)
- [ ] Write comprehensive unit tests in `tests/forms/test_form_generation.py`:
  - Generate form from simple definition
  - Test each field type mapping
  - Verify required/optional enforcement
  - Test choice fields with options
  - Validate file upload constraints
  - Test form-level validation
  - Verify field ordering preserved

## Acceptance Criteria

- [ ] Can generate Django Form class from any FormDefinition
- [ ] All field types map correctly
- [ ] Required fields validated
- [ ] Choice fields render with correct options
- [ ] File uploads validate size and extension
- [ ] Help text and labels preserved
- [ ] CSS classes applied to widgets
- [ ] Field order matches StreamField order
- [ ] Unit tests pass with ≥80% coverage
- [ ] `make lint` passes
- [ ] Generated forms work with Django's validation system

## Testing Commands

```bash
# Run unit tests
pytest tests/forms/test_form_generation.py -v

# Check coverage
pytest tests/forms/test_form_generation.py --cov=core/sum_core/forms/dynamic --cov-report=term-missing

# Manual testing in shell
python core/sum_core/test_project/manage.py shell
>>> from sum_core.forms.models import FormDefinition
>>> from sum_core.forms.dynamic import DynamicFormGenerator
>>> fd = FormDefinition.objects.first()
>>> generator = DynamicFormGenerator(fd)
>>> FormClass = generator.generate_form_class()
>>> form = FormClass()
>>> print(form.as_p())

# Run linting
make lint
```

## Post-Implementation

**Commit, push, and create PR:**
```bash
git add .
git commit -m "feat(forms): add runtime Django form generation

- Implement DynamicFormGenerator class
- Map all 9 input field blocks to Django fields
- Preserve validation rules and constraints
- Handle choice-based fields dynamically
- Add file upload validation
- Maintain field ordering from StreamField
- Include comprehensive unit tests

Refs: BLOG.004"

git push origin feature/BLOG-004-form-generation

gh pr create \
  --base develop \
  --title "feat(forms): Runtime Django form generation" \
  --body "Implements BLOG.004 - Generate Django forms from FormDefinition.

## Changes
- DynamicFormGenerator class for runtime form creation
- Field type mapping for all 11 block types
- Validation rule preservation
- Choice field handling with dynamic options
- File upload constraints enforcement
- Field ordering preservation
- Comprehensive unit tests

## Testing
- ✅ All field types generate correctly
- ✅ Validation rules work
- ✅ Choice fields render with options
- ✅ File uploads validate
- ✅ Field order preserved
- ✅ Lint checks pass

## Related
- Depends on: BLOG.002
- Blocks on: BLOG.006 (form rendering), BLOG.007 (submission handler)"
```

**Monitor CI and resolve review comments:**
```bash
gh pr status
gh pr checks --watch
# Address all feedback and conversations
```

## Notes for AI Agents

- **Critical path** task - required for form rendering and submission
- Use `type()` to create Form class dynamically, not metaclasses
- Consider caching generated form classes (keyed by FormDefinition.id)
- Layout blocks (heading, help text) should be skipped in field generation
- File validation should happen in form's `clean()` method, not field-level
- Preserve exact field order from StreamField for UX consistency
- Generated forms must integrate seamlessly with Django's validation framework
