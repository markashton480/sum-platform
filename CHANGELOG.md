# Changelog

## [v0.5.3] - 2025-12-25
### Changed
- Sync staging now defaults to `/tmp/sum-core-sync` to avoid accidental gitlinks; release docs updated.

## [v0.5.2] - 2025-12-24
### Fixed
- Packaging: limit setuptools discovery to `sum_core` (exclude boilerplate) so pip installs from git tags succeed.

## [v0.5.1] - 2025-12-24
### Fixed
- Packaging: set PEP 508-compliant project name (`sum-core`) so pip installs from git tags work again.

## [v0.5.0] - 2025-12-24

### Added
- Theme A structural blocks: PageHeader, Timeline, TeamMember, ServiceDetail, Spacer/Divider, buttons + social proof, and editorial templates.
- Theme A content refresh: portfolio filters plus rewritten gallery and quote request form.
- Legal content: legal TOC/section blocks and seeded legal pages for the showroom.
- Process steps redesigned with updated templates and theme contract coverage.

### Fixed
- Leads reliability: stabilized retry attempt tracking, avoided retries on template render errors, and moved side effects out of transactions.
- Theme A polish: process steps layout, quote form feedback, timeline typing, and image styling fixes.

### Changed
- Release tooling and sync flow refreshed to support the new public mirror.
- Hygiene updates: excluded boilerplate directories from mypy, lint/format cleanups, and regenerated Theme A CSS artifacts.

### Documentation
- Updated release/Git strategy, two-repo setup guidance, public README, and planning notes for themes and blog work.
