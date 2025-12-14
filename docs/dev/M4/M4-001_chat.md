# Chat Conversation

Note: _This is purely the output of the chat conversation and does not contain any raw data, codebase snippets, etc. used to generate the output._

### User Input

Please review the task details in @[docs/dev/M4/M4-001.md] and carefully implement.

*Viewed [M4-001.md](file:///home/mark/workspaces/sum-platform/docs/dev/M4/M4-001.md) *

*Listed directory [sum_core](file:///home/mark/workspaces/sum-platform/core/sum_core) *

*Listed directory [branding](file:///home/mark/workspaces/sum-platform/core/sum_core/branding) *

*Viewed [models.py](file:///home/mark/workspaces/sum-platform/core/sum_core/branding/models.py) *

*Viewed [models.py](file:///home/mark/workspaces/sum-platform/core/sum_core/models.py) *

*Grep searched codebase*

*Edited relevant file*

*Viewed [Makefile](file:///home/mark/workspaces/sum-platform/Makefile) *

*User accepted the command `source .venv/bin/activate && make makemigrations`*

*Listed directory [sum_core](file:///home/mark/workspaces/sum-platform/core/sum_core/templates/sum_core) *

*Listed directory [includes](file:///home/mark/workspaces/sum-platform/core/sum_core/templates/sum_core/includes) *

*User accepted the command `mkdir -p core/sum_core/templates/sum_core/includes/analytics`*

*Edited relevant file*

*Edited relevant file*

*Edited relevant file*

*Listed directory [analytics](file:///home/mark/workspaces/sum-platform/core/sum_core/analytics) *

*Searched filesystem*

*Viewed [settings.py](file:///home/mark/workspaces/sum-platform/core/sum_core/test_project/test_project/settings.py) *

*Viewed [apps.py](file:///home/mark/workspaces/sum-platform/core/sum_core/apps.py) *

*Listed directory [analytics](file:///home/mark/workspaces/sum-platform/core/sum_core/analytics) *

*Edited relevant file*

*User accepted the command `mkdir -p core/sum_core/analytics/templatetags && touch core/sum_core/analytics/templatetags/__init__.py`*

*Edited relevant file*

*Edited relevant file*

*Viewed [base.html](file:///home/mark/workspaces/sum-platform/core/sum_core/templates/sum_core/base.html) *

*Edited relevant file*

*User accepted the command `source .venv/bin/activate && make migrate`*

*Listed directory [tests](file:///home/mark/workspaces/sum-platform/tests) *

*User accepted the command `mkdir -p tests/analytics`*

*Viewed [conftest.py](file:///home/mark/workspaces/sum-platform/tests/conftest.py) *

*Edited relevant file*

*Edited relevant file*

*User accepted the command `source .venv/bin/activate && pytest tests/analytics`*

*Checked command status*

*Edited relevant file*

*Edited relevant file*

*User accepted the command `source .venv/bin/activate && pytest tests/analytics`*

*Checked command status*

*Checked command status*

*User accepted the command `source .venv/bin/activate && make lint`*

*User accepted the command `source .venv/bin/activate && make format`*

*User accepted the command `source .venv/bin/activate && ruff check . --fix`*

*User accepted the command `source .venv/bin/activate && make lint`*

*User accepted the command `source .venv/bin/activate && make test`*

*Checked command status*

*Checked command status*

*Checked command status*

*Checked command status*

### Planner Response

Implement the **analytics template tags** (M4-001) that inject GA4 or GTM scripts (head + body) based on per-site [SiteSettings](cci:2://file:///home/mark/workspaces/sum-platform/core/sum_core/branding/models.py:19:0-234:49).

### Changes Implemented

1.  **Site Settings Updates**:
    -   Modified [core/sum_core/branding/models.py](cci:7://file:///home/mark/workspaces/sum-platform/core/sum_core/branding/models.py:0:0-0:0) to add `gtm_container_id` and `ga_measurement_id` fields to [SiteSettings](cci:2://file:///home/mark/workspaces/sum-platform/core/sum_core/branding/models.py:19:0-234:49).
    -   Added an "Analytics" panel to the Wagtail admin interface for [SiteSettings](cci:2://file:///home/mark/workspaces/sum-platform/core/sum_core/branding/models.py:19:0-234:49).
    -   Created and applied migration `sum_core.0003_sitesettings_ga_measurement_id_and_more`.

2.  **App & Configuration**:
    -   Created `sum_core.analytics` app ([apps.py](cci:7://file:///home/mark/workspaces/sum-platform/core/sum_core/apps.py:0:0-0:0)) to host the template tags.
    -   Added `sum_core.analytics` to `INSTALLED_APPS` in [core/sum_core/test_project/test_project/settings.py](cci:7://file:///home/mark/workspaces/sum-platform/core/sum_core/test_project/test_project/settings.py:0:0-0:0) to ensure template tags are discoverable.

3.  **Template Tags ([core/sum_core/analytics/templatetags/analytics_tags.py](cci:7://file:///home/mark/workspaces/sum-platform/core/sum_core/analytics/templatetags/analytics_tags.py:0:0-0:0))**:
    -   Implemented `{% analytics_head %}`: Injects GTM head script (priority) OR GA4 head script, or neither.
    -   Implemented `{% analytics_body %}`: Injects GTM body noscript iframe (only if GTM is active).
    -   Follows the priority logic: GTM > GA4 > None.
    -   Resolves settings via `SiteSettings.for_request(request)`.

4.  **Templates**:
    -   Created reusable template includes:
        -   [core/sum_core/templates/sum_core/includes/analytics/gtm_head.html](cci:7://file:///home/mark/workspaces/sum-platform/core/sum_core/templates/sum_core/includes/analytics/gtm_head.html:0:0-0:0)
        -   [core/sum_core/templates/sum_core/includes/analytics/gtm_body.html](cci:7://file:///home/mark/workspaces/sum-platform/core/sum_core/templates/sum_core/includes/analytics/gtm_body.html:0:0-0:0)
        -   [core/sum_core/templates/sum_core/includes/analytics/ga4_head.html](cci:7://file:///home/mark/workspaces/sum-platform/core/sum_core/templates/sum_core/includes/analytics/ga4_head.html:0:0-0:0)
    -   Updated [core/sum_core/templates/sum_core/base.html](cci:7://file:///home/mark/workspaces/sum-platform/core/sum_core/templates/sum_core/base.html:0:0-0:0) to load `analytics_tags` and insert the tags in `<head>` (after viewport) and `<body>`.

5.  **Testing**:
    -   Created **Unit Tests** in [tests/analytics/test_analytics_tags.py](cci:7://file:///home/mark/workspaces/sum-platform/tests/analytics/test_analytics_tags.py:0:0-0:0): Verified tag logic, priority handling, and correct rendering context.
    -   Created **Integration Tests** in [tests/analytics/test_analytics_integration.py](cci:7://file:///home/mark/workspaces/sum-platform/tests/analytics/test_analytics_integration.py:0:0-0:0): Verified full page rendering, script presence in HTML response, and correct script IDs.
    -   Verified all tests pass with `make test`.

### Verification Code
You can verify the new tests specifically:
```bash
source .venv/bin/activate
pytest tests/analytics
```

Or run the full suite:
```bash
make test
```