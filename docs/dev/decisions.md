## Decision: Defer Docker-based local dev (US-F01 AC5–AC7)

- Date: 2025-12-08
- Context: Solo dev, Linux host, non-Docker production.
- Decision: Proceed with bare-metal Python venv + `manage.py runserver` for local dev.
- Impact:
  - US-F01 AC5–AC7 considered "planned" but not implemented yet.
  - Milestone 0 considered "functionally complete" for now; Docker added as separate ticket.
- Revisit:
  - When another dev joins the project, or
  - When CI pipeline is implemented.
