# AI Execution Prompt: M6-A-003 Theme Guardrails v1

**Task ID**: M6-A-003  
**Objective**: Implement repo-level guardrails that prevent Theme A's compiled Tailwind CSS from drifting or regressing

---

## Agent Role

You are a **defensive system engineer** implementing automated guardrails for a compiled CSS build pipeline. Your goal is to ensure that Theme A's Tailwind CSS remains valid, current, and free from legacy contamination across all future development.

---

## Task Objective (Restated from M6-A-003)

Prevent Theme A's compiled Tailwind CSS (`main.css`) from drifting due to:

- Changes to Tailwind/PostCSS configuration without rebuilding CSS
- Changes to template files that require new utility classes
- Accidental deletion or corruption of compiled CSS
- Reintroduction of legacy core CSS imports

This must be enforced via **automated tests** that fail immediately when drift is detected.

---

## Hard Constraints (NON-NEGOTIABLE)

1. **Build fingerprint MUST be deterministic**

   - Based on exact file contents (not timestamps)
   - Must cover ALL inputs that affect Tailwind output

2. **Guardrail tests MUST fail loudly**

   - Clear error messages explaining what went wrong
   - Explicit instructions on how to fix (rebuild + regenerate)

3. **No manual process dependencies**

   - Fingerprint regeneration must be scriptable
   - All checks must run via `make test`

4. **Zero false negatives**

   - If inputs change without rebuilding, tests MUST fail
   - If CSS is corrupted/missing, tests MUST fail

5. **PromptOps compliance**
   - This prompt file must be created and committed
   - Follow-up report must reference this prompt's commit hash

---

## Exact Files to Create/Modify

### Files to CREATE:

1. **`core/sum_core/themes/theme_a/build_fingerprint.py`**

   - Python module (runnable via `python -m`)
   - Computes SHA256 hash of all fingerprint inputs
   - Writes `.build_fingerprint` file
   - Exits non-zero on missing inputs

2. **`tests/themes/test_theme_a_guardrails.py`**

   - pytest test module
   - Tests fingerprint freshness
   - Tests compiled CSS validity
   - Tests for legacy contamination

3. **`core/sum_core/themes/theme_a/static/theme_a/css/.build_fingerprint`**

   - Plain text file containing SHA256 hash
   - Committed to repo
   - Updated only when inputs change

4. **`docs/prompts/themes/M6-A-003-theme-guardrails.prompt.md`**

   - This file
   - AI execution contract

5. **`docs/dev/M6/M6-A-003_followup.md`**
   - Evidence artifact
   - References prompt commit hash
   - Confirms all acceptance criteria met

### Files to REFERENCE (do not modify):

- `core/sum_core/themes/theme_a/tailwind.config.js`
- `core/sum_core/themes/theme_a/postcss.config.js`
- `core/sum_core/themes/theme_a/static/theme_a/css/input.css`
- `core/sum_core/themes/theme_a/templates/theme/**/*.html` (all template files)
- `core/sum_core/themes/theme_a/static/theme_a/css/main.css`

---

## Fingerprint Inputs (Exact Specification)

The fingerprint MUST be computed from these inputs IN THIS ORDER:

1. `tailwind.config.js` (full content)
2. `postcss.config.js` (full content, empty string if absent)
3. `static/theme_a/css/input.css` (full content)
4. All `.html` files under `templates/theme/`, sorted alphabetically by path (concatenated content)

**Algorithm**:

```python
import hashlib
from pathlib import Path

def compute_fingerprint():
    hasher = hashlib.sha256()

    # 1. tailwind.config.js
    hasher.update(read_file("tailwind.config.js").encode())

    # 2. postcss.config.js (or empty if missing)
    hasher.update(read_file_or_empty("postcss.config.js").encode())

    # 3. input.css
    hasher.update(read_file("static/theme_a/css/input.css").encode())

    # 4. All template files (sorted)
    for template_path in sorted(template_files):
        hasher.update(read_file(template_path).encode())

    return hasher.hexdigest()
```

---

## CSS Validity Checks (Exact Specification)

The test suite MUST validate `main.css`:

1. **Exists**: File must be present
2. **Non-trivial**: Size > 5KB (5000 bytes)
3. **Contains Tailwind signatures**:
   - `.flex{display:flex}` (exact substring)
   - `.hidden{display:none}` (exact substring)
4. **No legacy contamination**:
   - MUST NOT contain `@import url("/static/sum_core/css/main.css")`
   - MUST NOT contain `/static/sum_core/css/main.css`

---

## Test Integration Requirements

1. **Tests run via `make test`**

   - No special flags required
   - Failures halt the suite

2. **Error messages MUST include**:

   ```
   FAILED: Theme A build fingerprint is stale.

   Fix:
   1. cd core/sum_core/themes/theme_a
   2. npm run build
   3. python -m sum_core.themes.theme_a.build_fingerprint
   4. git add static/theme_a/css/main.css static/theme_a/css/.build_fingerprint
   5. git commit
   ```

3. **Fingerprint regeneration command**:
   ```bash
   python -m sum_core.themes.theme_a.build_fingerprint
   ```
   - Overwrites `.build_fingerprint`
   - Exits 0 on success
   - Exits 1 if inputs missing

---

## Required Python File Header

```python
"""
Name: Theme A Guardrails
Path: <actual file path>
Purpose: Prevent compiled Tailwind CSS drift and regressions
Family: Themes / Toolchain
Dependencies: filesystem, hashlib, pytest
"""
```

---

## Acceptance Criteria (Definition of Done)

### Code Validation:

- [ ] Fingerprint script runs successfully via `python -m sum_core.themes.theme_a.build_fingerprint`
- [ ] Guardrail tests pass when fingerprint is fresh
- [ ] Guardrail tests FAIL when inputs change without regeneration
- [ ] Guardrail tests FAIL if CSS is deleted
- [ ] Guardrail tests FAIL if CSS is < 5KB
- [ ] Guardrail tests FAIL if Tailwind signatures missing
- [ ] Guardrail tests FAIL if legacy imports present
- [ ] All tests run via `make test`
- [ ] `make lint` passes

### PromptOps Validation:

- [ ] This prompt file exists at `docs/prompts/themes/M6-A-003-theme-guardrails.prompt.md`
- [ ] This prompt file is committed
- [ ] Follow-up report references prompt path
- [ ] Follow-up report includes commit hash containing this prompt

### Evidence Validation:

- [ ] Follow-up report exists at `docs/dev/M6/M6-A-003_followup.md`
- [ ] Follow-up confirms all acceptance criteria
- [ ] Follow-up documents any deviations or learnings

---

## Scope Boundary (FORBIDDEN)

Do NOT:

- Modify Theme A templates or styling
- Change Tailwind configuration
- Rebuild or regenerate `main.css` (assume it's already current)
- Add client-side theme validation
- Implement runtime fingerprint checks
- Extract fingerprinting to a generic library
- Add fingerprints for other themes

This task is ONLY about:

- Building the fingerprint mechanism
- Testing fingerprint freshness
- Testing CSS validity
- PromptOps compliance

---

## Definition of Done Checklist

- [ ] `build_fingerprint.py` created and functional
- [ ] `test_theme_a_guardrails.py` created with all required checks
- [ ] `.build_fingerprint` generated and committed
- [ ] `make test` passes
- [ ] `make lint` passes
- [ ] Prompt file committed
- [ ] Follow-up report written and committed
- [ ] Follow-up references prompt commit hash
- [ ] All acceptance criteria validated

---

## Expected Workflow

1. Create `build_fingerprint.py`
2. Run fingerprint script to generate `.build_fingerprint`
3. Create `test_theme_a_guardrails.py` with all validation logic
4. Run tests - verify they pass
5. Manually modify an input file (e.g., `tailwind.config.js`)
6. Run tests - verify they FAIL with clear message
7. Revert change
8. Run tests - verify they pass again
9. Commit all code and fingerprint file
10. Create follow-up report with commit hash
11. Commit prompt and follow-up report

---

**This prompt is an execution contract. Deviation from these specifications invalidates the implementation.**
