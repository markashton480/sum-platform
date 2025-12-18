## Decision: Defer Docker-based local dev (US-F01 AC5–AC7)

**ADR ID**: ADR-001

- Date: 2025-12-08
- Context: Solo dev, Linux host, non-Docker production.
- Decision: Proceed with bare-metal Python venv + `manage.py runserver` for local dev.
- Impact:
  - US-F01 AC5–AC7 considered "planned" but not implemented yet.
  - Milestone 0 considered "functionally complete" for now; Docker added as separate ticket.
- Revisit:
  - When another dev joins the project, or
  - When CI pipeline is implemented.
- UPDATE: Implemented anyway a couple of days later. 17/12/2025

---

# ADR — v0.6 Theme Rendering Contract Reset

**ADR ID**: ADR-002
**Date**: 2025-12-17
**Status**: Accepted
**Context**: SUM Platform v0.6 (Post-MVP)

## Decision

Starting in **v0.6**, SUM introduces a **new theme rendering contract** in which **themes are the primary owners of layout and templates**, and page models no longer hard-bind to `sum_core` template paths.

This decision intentionally **breaks the v0.5 rendering shape**, while remaining acceptable because:

- v0.5 is pre-v1 and has no external consumers
- a major frontend paradigm shift (CSS Tokens → Tailwind) has already occurred
- platform clarity and forward momentum outweigh retrofit complexity

## Previous State (v0.5)

- Page models define templates under `sum_core/...`
- Themes override core templates via path shadowing
- Rendering validation requires harness workarounds
- Theme ownership is implicit and ergonomically hostile

## New State (v0.6+)

- **Themes own layout and page templates**
- Page models reference **theme-scoped template slots**, not core paths
- `sum_core` templates are:

  - fallback only
  - minimal
  - not the primary rendering surface

- Theme A defines the **reference shape** for future themes

## Consequences

### Positive

- Eliminates template shadowing hacks
- Simplifies theme development and testing
- Makes themes first-class citizens
- Aligns platform architecture with real-world usage

### Trade-offs

- v0.5 templates become legacy
- Rendering contract is not backward-compatible
- Requires a controlled migration inside v0.6

## Notes

This decision is limited to **pre-v1**.
Once v1 is released, rendering contracts will be frozen and backward compatibility will be enforced.

---
