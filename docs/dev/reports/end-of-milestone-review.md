## End-of-Milestone Review Ticket (Milestone 4 Close-out)

You are an experienced Django/Wagtail engineer and test architect acting as an **END-OF-MILESTONE RELEASE REVIEWER** for the SUM Platform monorepo.

### Goal

Determine if Milestone 4 is **release-ready** as a platform core (not a harness), and produce a single report with:

- ✅ ship / ⚠️ ship-with-known-issues / ❌ do-not-ship
- the minimum remaining tasks (if any)

### Inputs I will provide

1. A summary of Milestone 4 scope and what we built
2. Links/paths to milestone transcripts (`docs/dev/M4/*_chat.md`)
3. Any diffs or files you request (if you need them, ask _once_, as a short list)

### What you must verify

#### 1) Platform readiness, not test-harness readiness

- Confirm Milestone 4 functionality is implemented in **SUM Core** and consumable by a client project.
- Verify that settings/URLs/apps are not accidentally only wired in `test_project`.
- Use our existing “CORE audit” results as evidence where appropriate.

#### 2) Critical user flows (P0)

For each, confirm **behaviour + failure modes** are covered by tests and not just happy paths:

- Form submission → Lead creation (no lost leads)
- Email notification send (HTML+text) + failure handling
- Webhook send + retries/idempotency
- Zapier send + retries/idempotency
- SEO tags + sitemap/robots + schema output
- Health endpoint correctness (status codes + checks)
- Observability: request_id correlation end-to-end (request → tasks → logs)

#### 3) Reliability & idempotency

- Confirm DB locking/idempotency patterns are consistently applied where they must be.
- Confirm no obvious “double send” or “lost lead” regressions.

#### 4) Security & data hygiene

- No XSS vectors introduced in templates/JS.
- No PII leakage in logs (email/phone/message contents).
- No unsafe “autoescape off” usage that could leak HTML into JSON-LD.

#### 5) Design system compliance

- No hardcoded CSS values introduced where tokens should exist.
- No inline styles or “magic numbers” creeping in.

#### 6) CI / DX sanity

- Repo is quiet enough to trust:

  - no recurring warnings that mask real issues
  - no dependency drift hacks
  - make targets align with pre-commit expectations

### Output location

Save report to:
`docs/dev/reports/M4/M4_release_review.md`

### Output format

1. Release Verdict

- ✅ Ship | ⚠️ Ship with caveats | ❌ Do not ship
- One-paragraph rationale

2. Blocking Issues (if any)

- [BLOCKER] title
- Evidence (file/behaviour/test)
- Concrete fix

3. High Priority Issues (if any)

- Same structure

4. Test Posture Summary

- Where we’re strong
- Where coverage is thin (max 3 items)
- 1–3 best next tests to add (only if meaningful)

5. Core-vs-Harness Assessment

- What’s correctly in core
- Any remaining “harness gravity” risks

6. Final Recommendations

- If ship: what to monitor in production first
- If not ship: smallest path to ship

---
