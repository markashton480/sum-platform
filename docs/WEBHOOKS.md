# Webhooks

This document covers webhook payloads, signing, and field controls for SUM Platform.

## Dynamic Form Webhooks

Dynamic form submissions can send webhook payloads when a Form Definition has:

- Webhooks enabled
- A webhook URL
- Optional signing secret
- Optional field allowlist/denylist

### Payload schema

Dynamic form webhooks use a nested payload that includes form metadata, submission
data, and attribution fields.

```json
{
  "event": "form.submitted",
  "timestamp": "2025-12-30T00:00:00+00:00",
  "form": {
    "id": 123,
    "name": "Contact",
    "slug": "contact"
  },
  "submission": {
    "id": 456,
    "contact": {
      "name": "Jane Doe",
      "email": "jane@example.com",
      "phone": "555-555-5555",
      "message": "Need a quote"
    },
    "data": {
      "service": "Roofing",
      "budget": "5000"
    },
    "created_at": "2025-12-30T00:00:00+00:00"
  },
  "attribution": {
    "source_url": "https://example.com/contact",
    "landing_page": "https://example.com/landing",
    "utm_source": "google",
    "utm_medium": "cpc",
    "utm_campaign": "spring",
    "utm_term": "roofing",
    "utm_content": "ad-1"
  },
  "request_id": "req-123"
}
```

Notes:

- `submission.data` contains only non-standard form fields (extra data).
- `request_id` is included only when available from the originating request.

### Field allowlist/denylist

Form Definitions can restrict which keys appear in `submission.data`:

- Allowlist: only listed keys are included.
- Denylist: listed keys are removed.
- If both are set, the denylist is applied after the allowlist.

These controls affect only `submission.data`. Contact fields (`name`, `email`,
`phone`, `message`) are always included when present on the Lead record.

### Signing

When a webhook signing secret is set, SUM Platform sends an HMAC signature header:

```
X-SUM-Webhook-Signature: sha256=<hex>
```

The signature is calculated using HMAC-SHA256 over the raw request body. The
request body is serialized as compact JSON with sorted keys:

```
json.dumps(payload, separators=(",", ":"), sort_keys=True)
```

Treat signing secrets as sensitive credentials. Store them securely and rotate
regularly.

#### Verification example (Python)

```python
import hashlib
import hmac

secret = "supersecret"
request_body_bytes = b"..."  # Use the exact body bytes received
signature = hmac.new(
    secret.encode(),
    request_body_bytes,
    hashlib.sha256,
).hexdigest()

expected_header = f"sha256={signature}"
```

#### Verification example (Node.js)

```js
import crypto from "crypto";

const secret = "supersecret";
const rawBody = req.body; // Use raw bytes, not JSON-parsed object
const signature = crypto
  .createHmac("sha256", secret)
  .update(rawBody)
  .digest("hex");

const expectedHeader = `sha256=${signature}`;
```

## Lead Webhooks

Lead webhooks use a flat schema defined in
`sum_core.leads.tasks.build_webhook_payload` (e.g. `lead_id`, `name`, `email`,
`form_type`, `form_data`, `utm_*`). Dynamic form webhooks intentionally use the
nested `event/form/submission/attribution` schema to reflect the form metadata
and submission context.
