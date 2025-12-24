CLI theme support (Spec v1 §9): ensure sum init supports --theme <slug> and listing available themes, and resolves themes in this order: SUM*THEME_PATH → repo-root ./themes/theme*<slug>/ → (bundled CLI themes later). On init, copy the selected theme into clients/<client>/theme/active/ and ensure template loader priority is theme/active → templates/overrides → sum_core fallbacks.

THEME-ARCHITECTURE-SPECv1

Status: implemented via cli/sum_cli/themes_registry.py + command wiring; bundled CLI themes remain intentionally not implemented yet.
