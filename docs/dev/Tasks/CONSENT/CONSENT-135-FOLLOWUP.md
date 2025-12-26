# GH-135: Consent cookies + banner behavior + manage flow (JS) — Follow-up

**Date:** 2025-12-25  
**Status:** ✅ Complete  
**PR:** #146  
**Branch:** `feat/m0-135-cookie-consent-js`  
**Base Branch:** `dev/consent-legal-homepage`

---

## Executive Summary

Successfully implemented the cookie consent JavaScript functionality as specified in issue #135 (GH-0603). The implementation includes:

- Cookie management (set/get/delete) with proper attributes
- Banner visibility control based on consent state
- Accept/Reject/Manage flows
- Version checking to re-prompt when consent text changes
- Custom events for analytics integration
- Accessibility features (aria-live, screen reader announcements)

---

## Deliverables

### Files Created

1. **`core/sum_core/static/sum_core/js/cookie_consent.js`** (241 lines)
   - Complete cookie consent management system
   - Exposes public API: `window.SumCookieConsent`

### Files Modified

1. **`core/sum_core/templates/theme/base.html`**

   - Added `<meta name="sum:cookie-consent-version">` to expose version
   - Included `cookie_consent.js` script tag

2. **`core/sum_core/templates/sum_core/includes/cookie_banner.html`**
   - Added `style="display: none;"` and `aria-hidden="true"` to initial state
   - JavaScript controls visibility dynamically

---

## Implementation Details

### Cookie Specification

```javascript
// Cookie names
const COOKIE_CONSENT = 'sum_cookie_consent';
const COOKIE_CONSENT_VERSION = 'sum_cookie_consent_v';

// Cookie values
const CONSENT_ACCEPTED = 'accepted';
const CONSENT_REJECTED = 'rejected';

// Cookie attributes
- Max-Age: 15552000 (180 days)
- Path: /
- SameSite: Lax
- Secure: true (only on HTTPS)
```

### Banner Behavior

1. **On Page Load:**

   - Check if consent cookies exist
   - Check if version matches current version
   - If missing or version mismatch → show banner
   - If valid → hide banner

2. **On Accept:**

   - Set `sum_cookie_consent=accepted`
   - Set `sum_cookie_consent_v={current_version}`
   - Hide banner
   - Dispatch `cookieConsentChanged` event
   - Update status for screen readers

3. **On Reject:**

   - Set `sum_cookie_consent=rejected`
   - Set `sum_cookie_consent_v={current_version}`
   - Hide banner
   - Dispatch `cookieConsentChanged` event
   - Update status for screen readers

4. **On Manage:**
   - Delete both consent cookies
   - Show banner
   - Scroll banner into view
   - Update status for screen readers

### Event Interface

```javascript
// Custom event dispatched on consent change
document.addEventListener("cookieConsentChanged", (event) => {
  console.log(event.detail.consent); // 'accepted' or 'rejected'
  console.log(event.detail.version); // e.g., '1'
});
```

### Public API

```javascript
// Debugging/testing interface
window.SumCookieConsent = {
  getConsent: () => getCookie(COOKIE_CONSENT),
  getConsentVersion: () => getCookie(COOKIE_CONSENT_VERSION),
  isValid: isConsentValid,
  showBanner: showBanner,
  hideBanner: hideBanner,
};
```

---

## Acceptance Criteria — Verification

| Criterion                                                      | Status | Notes                          |
| -------------------------------------------------------------- | ------ | ------------------------------ |
| Cookie names: `sum_cookie_consent` = `accepted\|rejected`      | ✅     | Implemented in JS              |
| Cookie names: `sum_cookie_consent_v` = version                 | ✅     | Implemented in JS              |
| Expiry: 180 days; Path=/; SameSite=Lax; Secure on https        | ✅     | See cookie spec above          |
| Unknown state if missing OR version mismatch => banner visible | ✅     | `isConsentValid()` checks both |
| Clicking Accept sets cookies and hides banner                  | ✅     | `handleAccept()`               |
| Clicking Reject sets cookies and hides banner                  | ✅     | `handleReject()`               |
| Clicking "Manage cookies" re-shows banner                      | ✅     | `handleManage()`               |
| JS-disabled: banner includes noscript copy                     | ✅     | Implemented in #134            |

---

## Testing Results

### Linting

```bash
$ make lint
✅ ruff: All checks passed
✅ mypy: Success: no issues found in 263 source files
✅ black: 263 files would be left unchanged
✅ isort: Skipped 47 files
```

### Tests

```bash
$ make test
✅ 844 passed, 48 warnings in 296.16s (0:04:56)
✅ Coverage: 80%
```

---

## Dependencies

### Upstream (Required)

- ✅ #133 (GH-0601): SiteSettings fields — **Merged**
- ✅ #134 (GH-0602): Banner DOM hooks + markup — **Merged**

### Downstream (Blocked on this)

- ⏳ #136 (GH-0604): Analytics loader (needs consent state)
- ⏳ #137 (GH-0605): Tests for consent flows

---

## DOM Contract

The JavaScript requires the following DOM structure (provided by #134):

```html
<!-- Banner -->
<aside class="cookie-banner" aria-label="Cookie preferences">
  <button data-cookie-consent="accept">Accept</button>
  <button data-cookie-consent="reject">Reject</button>
  <p class="cookie-banner__status" aria-live="polite"></p>
</aside>

<!-- Manage link (in footer or elsewhere) -->
<a data-cookie-consent="manage">Manage cookies</a>

<!-- Meta tag (in <head>) -->
<meta
  name="sum:cookie-consent-version"
  content="{{ site_settings.cookie_consent_version }}"
/>
```

---

## Integration Points

### For Analytics Loader (#136)

1. **Listen to custom event:**

   ```javascript
   document.addEventListener("cookieConsentChanged", (event) => {
     if (event.detail.consent === "accepted") {
       // Load GTM/GA scripts
     }
   });
   ```

2. **Check consent on page load:**
   ```javascript
   const consent = window.SumCookieConsent.getConsent();
   if (consent === "accepted" && window.SumCookieConsent.isValid()) {
     // Load analytics
   }
   ```

### For Tests (#137)

- Use `window.SumCookieConsent` API to manipulate/verify state
- Verify cookie attributes with JS cookie parser
- Test version mismatch scenarios
- Test manage flow (delete + re-show)

---

## Known Limitations / Future Work

1. **No granular categories:**

   - Current implementation is binary (accept/reject all)
   - Future: could extend to `{analytics: true, marketing: false, ...}`

2. **No server-side audit logging:**

   - Consent is stored client-side only
   - Future: could POST to server endpoint for compliance audit trail

3. **No strict CSP compatibility:**
   - Uses inline `style="display: none;"`
   - Future: move to CSS class-based hiding with nonce

---

## Risk Mitigation

**Risk Level:** Med  
**Mitigations Applied:**

1. ✅ Cookie expiry limited to 180 days (not indefinite)
2. ✅ Secure flag only set on HTTPS (prevents insecure transmission)
3. ✅ SameSite=Lax prevents CSRF attacks
4. ✅ Version checking forces re-prompt when policy changes
5. ✅ Custom event allows decoupling from analytics loader
6. ✅ Public API namespaced under `SumCookieConsent` to avoid conflicts

---

## Deployment Notes

1. **Version bumping:**

   - To force re-consent: increment `cookie_consent_version` in SiteSettings
   - All users will see banner again on next visit

2. **Banner disabled:**

   - If `cookie_banner_enabled=False`, banner never renders
   - Analytics loader should treat as "always accepted" (implemented in #136)

3. **Multisite:**
   - Each site has its own `cookie_consent_version`
   - Cookies are host-only (no Domain attribute)

---

## Commit Summary

```
feature:consent-cookie consent JS + banner behavior + manage flow

- Implemented cookie_consent.js with accept/reject/manage flows
- Cookie names: sum_cookie_consent, sum_cookie_consent_v
- Expiry: 180 days, Path=/, SameSite=Lax, Secure on https
- Banner shows only when consent is unknown or version mismatches
- Manage flow clears consent and re-shows banner
- Custom event 'cookieConsentChanged' for analytics integration
- Added meta tag to expose consent version to JS
- Banner initially hidden with aria-hidden, shown by JS when needed

Closes #135
```

**Commit Hash:** `d81ea3e`

---

## Next Steps

1. ⏳ Wait for PR #146 review
2. ⏳ Merge to `dev/consent-legal-homepage` after approval
3. ⏳ Proceed with #136 (Analytics loader)
4. ⏳ Add E2E/integration tests in #137

---

## References

- **Issue:** [#135](https://github.com/markashton480/sum-platform/issues/135)
- **PR:** [#146](https://github.com/markashton480/sum-platform/pull/146)
- **Work Order:** `docs/dev/planning/0.6.0/legal-cookie-homepage.md`
- **Parent:** #132 (WO: Consent + Legal Pages + Starter Homepage)
