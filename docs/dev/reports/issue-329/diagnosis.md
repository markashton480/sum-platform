# Diagnosis Report: Issue #329 - Sage & Stone Footer Duplication

**Date:** 2025-12-30
**Investigator:** Antigravity
**Branch:** `fix/issue-329-diagnosis`
**Target Site:** `https://sage-and-stone.lintel.site`

## Observation

Upon inspecting the HTML content of the target site, a duplication was observed in the footer area. Two distinct sections titled "Studio" appear:

1.  **Link-based Studio Section:**

    ```html
    <div class="footer__section">
      <h4 class="footer__section-title">Studio</h4>
      <ul class="footer__link-list">
        <li>
          <a href="#studio-address" class="footer__link"
            >The Old Joinery, Unit 4</a
          >
        </li>
        ...
      </ul>
    </div>
    ```

2.  **Hardcoded Studio Section (Address/Contact):**
    ```html
    <div class="footer__section">
      <h4 class="footer__section-title">Studio</h4>
      <div class="footer__text footer__text--address">
        <p class="footer__text--spaced">The Old Joinery<br />Unit 4...</p>
        ...
      </div>
    </div>
    ```

## Root Cause Analysis

The issue stems from a conflict between the **CMS-configured Footer Navigation** and the **Theme A Hardcoded Footer Template**.

1.  **CMS Configuration:** The site administrator has manually created a Footer Navigation section named "Studio" and populated it with links (likely pointing to address anchors or similar).
2.  **Theme Template (`themes/theme_a/templates/theme/includes/footer.html`):** The theme explicitly renders a "Contact" section but hardcodes the title to "Studio". This section is automatically populated from the Site Settings (Business Address, Phone, Email).

    ```django
    {# Contact Section #}
    <div class="footer__section">
        <h4 class="footer__section-title">Studio</h4>
        <div class="footer__text footer__text--address">
            ...
        </div>
    </div>
    ```

Because both the CMS setting includes a "Studio" section and the Template hardcodes a "Studio" section, both appear in the final output.

## Recommendations

### Short-term (Content Fix)

The quickest resolution is to **remove the "Studio" section from the Footer Navigation menu in the Wagtail Admin**.

- The theme's design intent is to automatically display the Studio address in the footer based on global site settings.
- Manually adding it creates the observed duplication.

### Long-term (Code Fix)

Modify `themes/theme_a/templates/theme/includes/footer.html` to be more resilient, though this is architectural.

- Options include checking if a "Studio" section is defined in `link_sections` (complex in Django templates).
- Or, stick to the "Theme Contract" that Theme A _owns_ the Studio contact block, and documentation should reflect that this relies on Site Settings, not Menu configuration.

## Artifacts

- `debug_site.html`: Full HTML capture of the issue state.
