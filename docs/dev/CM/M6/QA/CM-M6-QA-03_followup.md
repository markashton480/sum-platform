# CM-M6-QA-03 — Mypy Debt Investigation Report

## Summary

The investigation into the 32 mypy errors reported across 18 files has been completed. The errors predominantly fall into Category B (Boundary typing/Any leakage), with a few Category A (Mechanical) fixes. No Category C (Architectural ambiguity) errors were identified that require deferral or significant refactoring.

## Error Categorisation Table

| File                                                       | Error                                               | Cat | Proposed Resolution                                             |
| :--------------------------------------------------------- | :-------------------------------------------------- | :-- | :-------------------------------------------------------------- |
| `core/sum_core/ops/health.py:130`                          | `Collection[str]` has no attribute `values`         | B   | Direct access to `checks` dict instead of `response["checks"]`. |
| `tests/themes/test_theme_a_guardrails.py:35, 107`          | Returning `Any` from declared `Path`                | B   | Explicit `Path(...)` cast.                                      |
| `cli/sum_cli/cli.py:45, 50, 52`                            | Returning `Any` from declared `int`                 | B   | Explicit `int(...)` cast on subcommand returns.                 |
| `cli/sum_cli/boilerplate/project_name/home/models.py:77`   | Returning `Any` from declared `bool`                | B   | Explicit `bool(...)` cast on Wagtail `can_create_at`.           |
| `core/sum_core/test_project/home/models.py:74`             | Returning `Any` from declared `bool`                | B   | Explicit `bool(...)` cast on Wagtail `can_create_at`.           |
| `core/sum_core/templatetags/form_tags.py:35, 91`           | Returning `Any` from declared `str`                 | B   | Explicit `str(...)` cast on `format_html`/`mark_safe`.          |
| `core/sum_core/pages/mixins.py:73, 76, 112`                | Returning `Any` from declared `str`                 | B   | Explicit `str(...)` cast on Django fields/methods.              |
| `core/sum_core/pages/mixins.py:108, 187`                   | Unused "type: ignore" comment                       | A   | Remove unused comments.                                         |
| `core/sum_core/leads/wagtail_admin.py:40`                  | Returning `Any` from declared `str`                 | B   | Explicit `str(...)` cast on `format_html`.                      |
| `core/sum_core/leads/wagtail_admin.py:172`                 | Returning `Any` from declared `list[Any]`           | B   | Explicit `list(...)` cast on `urlpatterns`.                     |
| `core/sum_core/leads/wagtail_admin.py:237, 247, 252`       | Returning `Any` from declared `bool`                | B   | Explicit `bool(...)` cast on `user.has_perm`.                   |
| `core/sum_core/leads/services.py:222`                      | Returning `Any` from declared `bool`                | B   | Explicit `bool(...)` cast on `user.has_perm`.                   |
| `core/sum_core/forms/models.py:81`                         | Returning `Any` from declared `FormConfiguration`   | B   | Cast result of `get_or_create` to `FormConfiguration`.          |
| `core/sum_core/branding/panels.py:28`                      | Returning `Any` from declared `dict[str, Any]`      | B   | Cast `super().clone_kwargs()` to `dict[str, Any]`.              |
| `core/sum_core/branding/forms.py:47`                       | Need type annotation for "exclude"                  | A   | Add `exclude: list[str] = []`.                                  |
| `core/sum_core/forms/services.py:258`                      | Returning `Any` from declared `str`                 | A   | Add `HttpRequest` type hint for `request` argument.             |
| `cli/sum_cli/boilerplate/project_name/settings/base.py:43` | Returning `Any` from declared `str \| None`         | B   | Explicit cast of JSON dict access.                              |
| `core/sum_core/leads/admin.py:112, 116`                    | Returning `Any` from declared `str`                 | B   | Explicit `str(...)` cast on Django/Wagtail helpers.             |
| `cli/sum_cli/commands/init.py:45`                          | Returning `Any` from declared `Path \| Traversable` | B   | Explicit cast to `BoilerplateSource`.                           |
| `tests/conftest.py:29`                                     | Returning `Any` from declared `Path`                | B   | Explicit `Path(...)` cast on pytest fixture.                    |
| `tests/templates/test_gallery_rendering.py:133, 150`       | `Tag \| None` has no attribute `text`               | B   | Assert tag is not `None` before `.text` access.                 |

## Conclusion

All identified debts are manageable within this CM. Fixes will focus on making types explicit where Django/Wagtail or third-party libraries leak `Any`.
