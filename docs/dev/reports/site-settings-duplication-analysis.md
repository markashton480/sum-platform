# Site Settings Duplication Analysis Report

**Date:** 2025-12-12  
**Author:** Cursor Implementation Agent  
**Status:** Analysis Complete  
**Related Tickets:** M1-002, NAV-003

---

## Executive Summary

This report analyses the duplication of fields between the existing `SiteSettings` model (from Milestone 1) and the newly added navigation models (`HeaderNavigation` and `FooterNavigation` from NAV-003). Several fields overlap between these models, which could lead to editor confusion and data inconsistency.

---

## 1. Current Site Settings Inventory

### 1.1 SiteSettings (Branding Module)

| Property           | Value                                                          |
| ------------------ | -------------------------------------------------------------- |
| **Module Path**    | `core/sum_core/branding/models.py`                             |
| **Class Name**     | `SiteSettings`                                                 |
| **Base Class**     | `BaseSiteSetting`                                              |
| **Admin Location** | Settings → Site settings                                       |
| **Purpose**        | Branding and business configuration shared across client sites |

**Fields:**

| Field Name               | Type               | Category        |
| ------------------------ | ------------------ | --------------- |
| `primary_color`          | CharField(7)       | Brand Colours   |
| `secondary_color`        | CharField(7)       | Brand Colours   |
| `accent_color`           | CharField(7)       | Brand Colours   |
| `background_color`       | CharField(7)       | Brand Colours   |
| `text_color`             | CharField(7)       | Brand Colours   |
| `surface_color`          | CharField(7)       | Brand Colours   |
| `surface_elevated_color` | CharField(7)       | Brand Colours   |
| `text_light_color`       | CharField(7)       | Brand Colours   |
| `header_logo`            | ForeignKey (Image) | Logos & Favicon |
| `footer_logo`            | ForeignKey (Image) | Logos & Favicon |
| `favicon`                | ForeignKey (Image) | Logos & Favicon |
| `og_default_image`       | ForeignKey (Image) | Logos & Favicon |
| `heading_font`           | CharField(100)     | Typography      |
| `body_font`              | CharField(100)     | Typography      |
| `company_name`           | CharField(255)     | Business Info   |
| **`tagline`**            | CharField(255)     | Business Info   |
| **`phone_number`**       | CharField(50)      | Business Info   |
| **`email`**              | EmailField         | Business Info   |
| **`address`**            | TextField          | Business Info   |
| **`business_hours`**     | TextField          | Business Info   |
| **`facebook_url`**       | URLField           | Social Links    |
| **`instagram_url`**      | URLField           | Social Links    |
| **`linkedin_url`**       | URLField           | Social Links    |
| **`twitter_url`**        | URLField           | Social Links    |
| **`youtube_url`**        | URLField           | Social Links    |
| **`tiktok_url`**         | URLField           | Social Links    |

---

### 1.2 HeaderNavigation (Navigation Module)

| Property           | Value                                   |
| ------------------ | --------------------------------------- |
| **Module Path**    | `core/sum_core/navigation/models.py`    |
| **Class Name**     | `HeaderNavigation`                      |
| **Base Class**     | `BaseSiteSetting`                       |
| **Admin Location** | Settings → Header Navigation            |
| **Purpose**        | Header menu items and CTA configuration |

**Fields:**

| Field Name                  | Type          | Category          |
| --------------------------- | ------------- | ----------------- |
| `menu_items`                | StreamField   | Main Navigation   |
| `show_phone_in_header`      | BooleanField  | Main Navigation   |
| `header_cta_enabled`        | BooleanField  | Header CTA        |
| `header_cta_text`           | CharField(50) | Header CTA        |
| `header_cta_link`           | StreamField   | Header CTA        |
| `mobile_cta_enabled`        | BooleanField  | Mobile Sticky CTA |
| `mobile_cta_phone_enabled`  | BooleanField  | Mobile Sticky CTA |
| `mobile_cta_button_enabled` | BooleanField  | Mobile Sticky CTA |
| `mobile_cta_button_text`    | CharField(50) | Mobile Sticky CTA |
| `mobile_cta_button_link`    | StreamField   | Mobile Sticky CTA |

---

### 1.3 FooterNavigation (Navigation Module)

| Property           | Value                                               |
| ------------------ | --------------------------------------------------- |
| **Module Path**    | `core/sum_core/navigation/models.py`                |
| **Class Name**     | `FooterNavigation`                                  |
| **Base Class**     | `BaseSiteSetting`                                   |
| **Admin Location** | Settings → Footer Navigation                        |
| **Purpose**        | Footer link sections and social media configuration |

**Fields:**

| Field Name             | Type           | Category       |
| ---------------------- | -------------- | -------------- |
| **`tagline`**          | CharField(255) | Footer Content |
| `link_sections`        | StreamField    | Footer Content |
| `auto_service_areas`   | BooleanField   | Footer Content |
| **`social_facebook`**  | URLField       | Social Links   |
| **`social_instagram`** | URLField       | Social Links   |
| **`social_linkedin`**  | URLField       | Social Links   |
| **`social_youtube`**   | URLField       | Social Links   |
| **`social_x`**         | URLField       | Social Links   |
| `copyright_text`       | CharField(255) | Copyright      |

---

## 2. Duplication Analysis

### 2.1 Direct Overlaps (Same Data, Different Locations)

| Field                  | SiteSettings (Branding) | FooterNavigation   | Impact                                                 |
| ---------------------- | ----------------------- | ------------------ | ------------------------------------------------------ |
| **Tagline**            | `tagline`               | `tagline`          | ⚠️ **HIGH** - Editor confusion: which one is used?     |
| **Social - Facebook**  | `facebook_url`          | `social_facebook`  | ⚠️ **HIGH** - Different field names, same purpose      |
| **Social - Instagram** | `instagram_url`         | `social_instagram` | ⚠️ **HIGH** - Different field names, same purpose      |
| **Social - LinkedIn**  | `linkedin_url`          | `social_linkedin`  | ⚠️ **HIGH** - Different field names, same purpose      |
| **Social - YouTube**   | `youtube_url`           | `social_youtube`   | ⚠️ **HIGH** - Different field names, same purpose      |
| **Social - Twitter/X** | `twitter_url`           | `social_x`         | ⚠️ **HIGH** - Different field names, X is more current |

### 2.2 Related Data (Not Duplicated But Interconnected)

| SiteSettings Field | Used By Navigation                      | Relationship                                |
| ------------------ | --------------------------------------- | ------------------------------------------- |
| `phone_number`     | `HeaderNavigation.show_phone_in_header` | Header displays phone from SiteSettings     |
| `email`            | Footer template                         | Footer may display contact email            |
| `address`          | Footer template                         | Footer may display business address         |
| `company_name`     | `FooterNavigation.copyright_text`       | Copyright uses `{company_name}` placeholder |

### 2.3 Unique Fields (No Overlap)

**SiteSettings only:**

- All colour fields (brand palette)
- Logo fields (header_logo, footer_logo, favicon)
- Typography (heading_font, body_font)
- Business info (address, business_hours, email)
- TikTok URL (not in FooterNavigation)

**FooterNavigation only:**

- `link_sections` (StreamField for footer columns)
- `auto_service_areas` (future feature)
- `copyright_text` (with placeholders)

**HeaderNavigation only:**

- `menu_items` (navigation structure)
- All CTA-related fields

---

## 3. Problematic Scenarios

### Scenario 1: Tagline Confusion

An editor sets the tagline in **Site settings** to "Quality You Can Trust" but also sets a different tagline in **Footer Navigation** to "Serving London Since 1985". Which appears in the footer? How does the editor know?

### Scenario 2: Social Links Out of Sync

Marketing updates the Facebook URL in **Site settings** but forgets to update it in **Footer Navigation**. Header/about pages may show one URL while the footer shows another.

### Scenario 3: Twitter to X Migration

**Site settings** has `twitter_url` while **Footer Navigation** has `social_x`. This naming inconsistency adds confusion even though they serve the same purpose.

---

## 4. Recommendations

### Option A: Navigation Settings Override Brand Settings (RECOMMENDED)

**Approach:** Keep both models but establish a clear hierarchy where navigation-specific settings **override** branding settings when both exist.

**Implementation:**

1. Create a helper function or template tag that returns the "effective" value:

   ```python
   def get_footer_tagline(request):
       footer = FooterNavigation.for_request(request)
       branding = SiteSettings.for_request(request)

       # Footer overrides branding if set
       return footer.tagline or branding.tagline
   ```

2. Document the precedence clearly in help_text:

   - FooterNavigation.tagline: "Footer-specific tagline. If blank, uses tagline from Site Settings."
   - FooterNavigation.social\_\*: "Footer-specific social link. If blank, uses URL from Site Settings."

3. Add a visual indicator in the admin showing when defaults are being used.

**Pros:**

- Maximum flexibility for editors who need different values in different contexts
- Backwards compatible with existing SiteSettings data
- Clear separation of concerns (branding vs. navigation presentation)

**Cons:**

- Slightly more complex logic
- Requires clear documentation for editors

---

### Option B: Remove Duplicates from FooterNavigation

**Approach:** Remove `tagline` and `social_*` fields from FooterNavigation. Footer templates always pull these values from SiteSettings.

**Implementation:**

1. Create a migration to remove these fields from FooterNavigation
2. Update FooterNavigation panels to not show these fields
3. Footer template loads both `SiteSettings` and `FooterNavigation`

**Pros:**

- Single source of truth
- No editor confusion
- Simpler data model

**Cons:**

- Less flexibility (can't have different footer tagline vs. header/site tagline)
- Requires migration with potential data loss
- May not match navigation-spec.md requirements

---

### Option C: Consolidate into a Single Settings Model

**Approach:** Merge all navigation fields into SiteSettings, or vice versa.

**Pros:**

- Single admin screen for all settings
- No duplication possible

**Cons:**

- **Not recommended** - the admin screen would become overwhelming
- Violates separation of concerns
- Makes future maintenance harder
- SiteSettings is already quite large (26 fields)

---

## 5. Recommended Action Plan

Based on the analysis, **Option A (Override Pattern)** is recommended because:

1. It respects the existing architecture and navigation-spec.md design
2. It provides flexibility for edge cases (different footer tagline is a valid use case)
3. It requires no destructive migrations
4. It's the standard pattern for layered configuration (think CSS cascade)

### Implementation Steps (if proceeding with Option A)

1. **Update FooterNavigation help_text** to clarify override behaviour:

   ```python
   tagline = models.CharField(
       help_text="Short tagline for the footer. Leave blank to use the tagline from Site Settings.",
   )
   ```

2. **Create a navigation context service** that merges settings:

   ```python
   # core/sum_core/navigation/services.py
   def get_merged_footer_context(request):
       """Return footer context with fallbacks to SiteSettings."""
   ```

3. **Update template tags** (when implemented) to use merged context

4. **Add TikTok to FooterNavigation** for parity (or document that TikTok only comes from SiteSettings)

5. **Consider renaming** `social_x` to `twitter_x_url` for clarity, or rename `twitter_url` in SiteSettings to `x_url`

---

## 6. Summary Table

| Field Type         | SiteSettings Location | FooterNavigation Location | Recommendation                        |
| ------------------ | --------------------- | ------------------------- | ------------------------------------- |
| Tagline            | `tagline`             | `tagline`                 | Footer overrides if set               |
| Social - Facebook  | `facebook_url`        | `social_facebook`         | Footer overrides if set               |
| Social - Instagram | `instagram_url`       | `social_instagram`        | Footer overrides if set               |
| Social - LinkedIn  | `linkedin_url`        | `social_linkedin`         | Footer overrides if set               |
| Social - YouTube   | `youtube_url`         | `social_youtube`          | Footer overrides if set               |
| Social - Twitter/X | `twitter_url`         | `social_x`                | Footer overrides if set; unify naming |
| Social - TikTok    | `tiktok_url`          | (not present)             | Add to Footer or document fallback    |

---

## 7. Decision Required

Please review this analysis and decide:

1. **Proceed with Option A (Override Pattern)?** - Requires help_text updates and service layer implementation
2. **Proceed with Option B (Remove Duplicates)?** - Requires migration and template updates
3. **Alternative approach?** - Please specify requirements

Once a decision is made, a follow-up ticket should be created to implement the chosen solution.

---

_End of Report_
