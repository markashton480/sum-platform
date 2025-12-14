# Chat Conversation

Note: _This is purely the output of the chat conversation and does not contain any raw data, codebase snippets, etc. used to generate the output._

### User Input

Please review details in task @[docs/dev/M4/M4-002.md] and carefully implement.

*Viewed [M4-002.md](file:///home/mark/workspaces/sum-platform/docs/dev/M4/M4-002.md) *

*Searched filesystem*

*Viewed [contact_form.html](file:///home/mark/workspaces/sum-platform/core/sum_core/templates/sum_core/blocks/contact_form.html) *

*Viewed [quote_request_form.html](file:///home/mark/workspaces/sum-platform/core/sum_core/templates/sum_core/blocks/quote_request_form.html) *

*User accepted the command `ls -F core/sum_core/static/sum_core/`*

*Checked command status*

*Viewed [base.html](file:///home/mark/workspaces/sum-platform/core/sum_core/templates/sum_core/base.html) *

*User accepted the command `ls -F core/sum_core/static/sum_core/js/main.js`*

*Checked command status*

*Edited relevant file*

*Semantic searched codebase*

*Edited relevant file*

*Edited relevant file*

*User accepted the command `find tests -name "test_*.py" | grep template`*

*Checked command status*

*Viewed [test_base_template.py](file:///home/mark/workspaces/sum-platform/tests/templates/test_base_template.py) *

*Viewed [test_form_blocks_rendering.py](file:///home/mark/workspaces/sum-platform/tests/templates/test_form_blocks_rendering.py) *

*Edited relevant file*

*Edited relevant file*

*User accepted the command `source .venv/bin/activate && pytest tests/templates/test_form_blocks_rendering.py tests/templates/test_base_template.py`*

*Checked command status*

*Checked command status*

*Checked command status*

*Checked command status*

*User accepted the command `source .venv/bin/activate && make lint`*

*Checked command status*

### Planner Response

I have implemented the event tracking JavaScript module and integrated it into the application.

1.  **Created [core/sum_core/static/sum_core/js/event_tracking.js](cci:7://file:///home/mark/workspaces/sum-platform/core/sum_core/static/sum_core/js/event_tracking.js:0:0-0:0)**:
    *   This script initializes `window.dataLayer`.
    *   It listens for `click` events on the document to track:
        *   **CTAs**: Explicitly via `data-track="cta"`, or implicitly for `.btn`/`.button` elements (with exclusions for admin, header/footer, etc.).
        *   **Phone Links**: `a[href^="tel:"]`.
        *   **Email Links**: `a[href^="mailto:"]`.
    *   It listens for `submit` events to track **Form Submissions** logic ONLY for forms with `data-form-type`.
    *   It strictly adheres to the "Never track list" (ignoring utility areas like navs, modals, cookie banners) unless explicitly overridden by `data-track="cta"`.

2.  **Updated [core/sum_core/templates/sum_core/base.html](cci:7://file:///home/mark/workspaces/sum-platform/core/sum_core/templates/sum_core/base.html:0:0-0:0)**:
    *   Added the [event_tracking.js](cci:7://file:///home/mark/workspaces/sum-platform/core/sum_core/static/sum_core/js/event_tracking.js:0:0-0:0) script to the footer with `defer`, ensuring it loads on every page.

3.  **Updated [core/sum_core/templates/sum_core/blocks/quote_request_form.html](cci:7://file:///home/mark/workspaces/sum-platform/core/sum_core/templates/sum_core/blocks/quote_request_form.html:0:0-0:0)**:
    *   Changed `data-form-type` from [quote](cci:1://file:///home/mark/workspaces/sum-platform/tests/templates/test_form_blocks_rendering.py:41:0-61:33) to [quote_request](cci:1://file:///home/mark/workspaces/sum-platform/tests/templates/test_form_blocks_rendering.py:41:0-61:33) to match the controlled vocabulary specified in the requirements.
    *   Verified [contact_form.html](cci:7://file:///home/mark/workspaces/sum-platform/core/sum_core/templates/sum_core/blocks/contact_form.html:0:0-0:0) already uses `data-form-type="contact"`.

4.  **Verified with Tests**:
    *   Updated [tests/templates/test_form_blocks_rendering.py](cci:7://file:///home/mark/workspaces/sum-platform/tests/templates/test_form_blocks_rendering.py:0:0-0:0) to assert the correct `data-form-type` for quote forms.
    *   Added a new test case to [tests/templates/test_base_template.py](cci:7://file:///home/mark/workspaces/sum-platform/tests/templates/test_base_template.py:0:0-0:0) to verify the [event_tracking.js](cci:7://file:///home/mark/workspaces/sum-platform/core/sum_core/static/sum_core/js/event_tracking.js:0:0-0:0) script tag is correctly rendered in the base template.
    *   Ran the tests (`pytest tests/templates/test_form_blocks_rendering.py tests/templates/test_base_template.py`) and confirmed they pass.

The system is now ready to track key user conversions (Form Fills, CTA clicks, Contact clicks) and push them to the dataLayer for GTM/GA4 consumption.