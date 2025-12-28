# Code Review Strategy: Copilot + Claude

This document explains how we use two AI reviewers with complementary roles to ensure both code quality AND scope alignment.

---

## The Two-Prong Approach

| | Copilot | Claude |
|---|---------|--------|
| **Role** | Craftsman | Project Manager |
| **Question** | "Is this code good?" | "Is this the right code?" |
| **Focus** | Implementation quality | Scope & context |
| **Level** | Line / Method | PR / Feature |
| **Context** | File-local | Issue hierarchy aware |

---

## Copilot's Domain (Tactical)

Copilot handles **code quality** at the implementation level:

### What Copilot Reviews
- ✓ Syntax and style consistency
- ✓ Method-level improvements
- ✓ Performance micro-optimizations
- ✓ Common bug patterns
- ✓ Test coverage suggestions
- ✓ DRY / refactoring opportunities
- ✓ Type hints and docstrings
- ✓ Variable and function naming
- ✓ Error handling patterns
- ✓ Code complexity

### Copilot's Typical Comments
- "This method could be simplified using list comprehension"
- "Consider extracting this logic into a helper function"
- "Missing type hint for return value"
- "This variable name could be more descriptive"
- "Consider adding error handling for edge case X"

---

## Claude's Domain (Strategic)

Claude handles **scope alignment** at the project level:

### What Claude Reviews

#### 0. PR Targeting Compliance (NEW)
- Does the PR target the correct branch per workflow rules?
- `task/*` → `feature/*`, not `develop`
- `feature/*` → `release/*`, not `develop`
- Catches workflow violations early

#### 1. Scope Alignment
- Does the PR address the issue's acceptance criteria?
- Are there changes unrelated to the stated goal?
- Is the PR doing MORE than the issue asks for?

#### 2. Boundary Compliance
- Does the issue have "Do NOT" sections?
- Are those boundaries respected?
- Example: Issue says "Do NOT modify templates" — did they?

#### 3. File Scope
- Are changes in expected directories?
- Any unexpected files touched?
- Changes to shared code without justification?

#### 4. AI Blunder Detection
- Imports from packages not in requirements.txt
- Django/Wagtail features that don't exist
- References to non-existent files or classes
- Hallucinated API endpoints
- Test mocks for things that should be real

#### 5. Regression Risk
- Core model changes (migration impact)
- Shared utility modifications
- Base template changes
- Settings file changes
- URL configuration changes

#### 6. Completeness
- Are ALL acceptance criteria addressed?
- Are tests included for new functionality?
- Is anything missing that should be there?

### Claude's Typical Findings

**🚫 Blocker:**
- "PR targets `develop` but should target `feature/forms` per workflow"
- "Issue says 'Do NOT implement validation (Task #115)' but PR adds FormValidator"
- "Import `from wagtail.contrib.forms import FormField` — this module doesn't exist"

**⚠️ Important:**
- "AC#3 (unit tests) only partially addressed — missing edge case tests"
- "Touches `core/utils.py` (used by 12 modules) — medium regression risk"

**📝 Note:**
- "PR modifies `base.html` — verify this is intentional for blog component"

---

## Why This Split?

### Copilot's Strengths
- Fast, lightweight
- Good at pattern matching within files
- Trained on millions of code reviews
- Consistent style suggestions

### Copilot's Limitations
- No access to issue tracker
- Can't see project structure context
- Doesn't know the "intent" behind changes
- Can't compare PR against requirements

### Claude's Strengths
- Can traverse issue hierarchy (Task → WO → VD)
- Understands project context
- Can detect scope creep
- Catches AI-generated hallucinations
- Can assess regression risk

### Claude's Limitations
- Slower, more resource-intensive
- Overkill for simple style issues
- Shouldn't duplicate Copilot's work

**Together:** Copilot ensures the code is well-written. Claude ensures it's the right code.

---

## Review Flow

```
PR Opened
    │
    ├──→ Copilot Review (automatic)
    │    └── Code quality feedback
    │
    └──→ Claude Strategic Review (automatic)
         ├── Load linked issue
         ├── Load parent WO (if exists)
         ├── Check scope alignment
         ├── Check boundary compliance
         ├── Detect AI blunders
         └── Assess regression risk
    │
    ▼
Agent/Author addresses feedback
    │
    ├── Copilot items: Fix code quality issues
    └── Claude items: Fix scope issues OR justify/defer
    │
    ▼
Reviews pass → Ready for human review
```

---

## For Agents: Handling Review Feedback

When you receive review feedback as an agent:

### From Copilot
- **Implement** if it's a clear improvement
- **Defer** if it's out of scope (create sub-issue)
- **Decline** if it conflicts with requirements (explain why)

### From Claude
- **Implement** if you missed something in scope
- **Remove** code if you went out of scope
- **Justify** if Claude flagged something that's actually correct
- **Escalate** if there's a genuine scope question (ask human)

### Priority
Claude's scope concerns take priority over Copilot's style suggestions. If Claude says "this file shouldn't be touched," removing the change trumps making it prettier.

---

## Example Reviews

### Copilot Review (Tactical)
```markdown
## Suggestions

**core/models/form.py:45**
Consider using a property decorator instead of a method:
```python
@property
def field_count(self):
    return self.fields.count()
```

**core/models/form.py:67**
This could raise an IndexError if fields is empty. Consider:
```python
return self.fields.first() if self.fields.exists() else None
```

**tests/test_forms.py:23**
Missing test for edge case when form has no fields.
```

### Claude Review (Strategic)
```markdown
## 🎯 Strategic Review

**Issue:** #111 — FormDefinition snippet model
**Work Order:** #100 — Dynamic Form System
**Targeting:** `task/forms/issue-111-formdefinition` → `feature/forms` ✅

### Acceptance Criteria Coverage
- [x] AC#1: FormDefinition model — ✅ `core/models/form.py:12`
- [x] AC#2: Wagtail snippet registration — ✅ `core/wagtail_hooks.py:8`
- [x] AC#3: Admin UI functional — ✅ Verified
- [x] AC#4: Unit tests — ✅ `tests/test_forms.py`

### Scope Delta
**In Scope:** FormDefinition model, snippet registration, tests
**Out of Scope:** `FormFieldBlock` in `core/blocks/forms.py` — belongs to Task #112
**Unclear:** None

### Findings

**🚫 Blocker**
- `core/blocks/forms.py`: FormFieldBlock violates boundary "Do NOT create form field blocks (Task #112)"
- Line 12: `from wagtail.contrib.forms.models import FormSubmission` — incorrect import path (should be `AbstractFormSubmission`)

---

**Verdict:** CHANGES REQUESTED

Remove FormFieldBlock (out of scope) and fix Wagtail import.
```

---

## Workflow Triggers

| PR Type | Copilot | Claude Strategic | Claude Audit |
|---------|---------|------------------|--------------|
| Task → Feature | ✓ | ✓ | — |
| Feature → Release | ✓ | ✓ | — |
| Release → Develop | — | — | ✓ (full audit) |
| Develop → Main | — | — | ✓ (full audit) |
| Hotfix → Main | — | — | ✓ (scope check) |

---

## Operational Notes

### Single Comment, Updated on Each Push

Claude edits its previous comment rather than creating new ones:
```bash
gh pr comment --edit-last --create-if-none
```

This keeps the PR clean — one Claude review that updates as you push fixes.

### Concurrency Control

Rapid pushes cancel in-progress Claude reviews to avoid wasted runs:
```yaml
concurrency:
  group: claude-review-${{ github.event.pull_request.number }}
  cancel-in-progress: true
```

### Issue Detection Fallbacks

Claude finds the linked issue via:
1. GitHub's `closingIssuesReferences` (most reliable)
2. Branch name parsing (`task/*/issue-NNN-*`)
3. PR body regex (`Closes #NNN`)

If all fail, Claude proceeds with diff-only review and flags missing issue link.

---

## Key Principle

> **Copilot asks:** "Is this good code?"
> **Claude asks:** "Is this the right code?"

Both must pass for a PR to be ready for human review.
