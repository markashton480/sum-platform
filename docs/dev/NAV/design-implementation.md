# Navigation Design Implementation

## Overview

This document details the implementation of the SUM Platform navigation system, specifically focussing on the 2-level nested menu support (3 levels total: Top -> Submenu -> Sub-submenu) introduced in NAV-010.

## HTML Structure

The navigation uses a nested `<ul>` structure. The top-level items are iterated, and if they have children, a dropdown structure is rendered.

```html
<nav class="nav-links">
  <!-- Level 1 -->
  <div class="nav-dropdown">
    <button class="nav-dropdown__toggle" aria-expanded="false">
      Top Level Item
    </button>
    <ul class="nav-dropdown__menu">
      <!-- Level 2 -->
      <li class="nav-dropdown__li">
        <div class="nav-nested-dropdown">
          <button class="nav-nested-dropdown__toggle" aria-expanded="false">
            Submenu Item
          </button>
          <!-- Level 3 -->
          <ul class="nav-nested-dropdown__menu">
            <li>
              <a href="..." class="nav-nested-dropdown__item">
                Grandchild Item
              </a>
            </li>
          </ul>
        </div>
      </li>
    </ul>
  </div>
</nav>
```

## CSS Architecture

Styles are located in `core/sum_core/static/sum_core/css/components.header.css`.

### Classes

- `.nav-dropdown`: Container for top-level dropdowns.
- `.nav-dropdown__menu`: The dropdown menu itself.
- `.nav-nested-dropdown`: Container for 2nd-level dropdowns inside a `.nav-dropdown__li`.
- `.nav-nested-dropdown__menu`: The nested menu.

### Responsive Behavior

**Desktop (>= 1024px):**

- Top-level dropdowns appear below the parent.
- Nested dropdowns (`.nav-nested-dropdown__menu`) appear to the **right** (`left: 100%`) of the parent item (Flyout style).
- Visibility is controlled via `opacity` and `visibility` based on the adjacent sibling combinator `[aria-expanded="true"] + .menu`.

**Mobile (< 1024px):**

- Navigation is an off-canvas or overlay drawer.
- Dropdowns behave as **accordions**.
- Visibility/Expansion is controlled via `max-height` transition.
- Nested items are indented (`padding-left`) to show hierarchy.

## JavaScript Behavior

Logic is contained in `core/sum_core/static/sum_core/js/navigation.js`.

- **Event Delegation:** Click listeners are attached to all `.nav-dropdown__toggle` and `.nav-nested-dropdown__toggle` elements.
- **Toggle Logic:**
  - Toggling a button updates its `aria-expanded` attribute.
  - Opening a dropdown closes all _other_ dropdowns that are NOT in the current ancestry chain (Smart Closing).
  - Closing a dropdown recursively closes all its child dropdowns.
- **Keyboard Support:** `Escape` key closes the deep-most open dropdown first, then bubbles up.

## Accessibility

- **ARIA Attributes:**
  - `aria-haspopup="true"` on toggles.
  - `aria-expanded="true/false"` state managed by JS.
  - `aria-label` on `<ul>`s to describe the submenu.
  - `aria-current="page"` on links matching the current URL.
- **Focus Management:** Standard tab order.
