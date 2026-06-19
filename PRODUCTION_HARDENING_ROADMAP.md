# Astraa Public Launch Hardening Roadmap

## Current proven milestone

Astraa Estimator has passed controlled live-payment proof:

- Moneris production preload returns real tickets.
- Moneris Checkout starts from payment.html.
- Approved Moneris transaction verifies through backend receipt request.
- Backend requires receipt_approved=true before activation.
- Declined transaction with invalid approval/auth code is blocked.
- Backend activates the correct account after approved payment.
- Estimator enforced route allows active paid account.
- Usage increments after successful estimate.

## Current status

Estimator status:

- Controlled production-readiness proof: PASSED.
- Public unrestricted launch: NOT YET.

## Public launch blockers

### 1. Backend-authenticated account identity

Current controlled-test behavior accepts account_email from browser/session/curl.

Public-production target:

- User logs in.
- Backend identifies account_id / tenant_id.
- Payment and Estimator actions attach to backend identity.
- Browser cannot activate or run another user's account by submitting an email.

### 2. Managed database/storage

Current local proof uses JSON files:

- astraa_data/astraa_usage_db.json
- astraa_data/astraa_payment_db.json
- preloads.jsonl
- payments.jsonl

Public-production target:

- Managed DB/storage.
- Transactional payment activation.
- Unique payment idempotency constraints.
- Backups and audit trail.

### 3. Route-level authorization

Protect:

- /preload
- /api/payment/verify-moneris-receipt
- /api/astraa/estimator/enforced-run

Public-production target:

- Authenticated user/session required where appropriate.
- Tenant/account ownership enforced.
- Public preload allowed only for valid checkout session.

### 4. Rate limiting and abuse protection

Protect against:

- repeated preload calls
- repeated receipt verification calls
- repeated estimator calls
- malformed payloads
- replay attempts

### 5. Estimate-pack approved-payment proof

Still required:

- Approved estimate-pack payment.
- Add exactly 10 credits.
- Same ticket replay does not duplicate credits.

### 6. Production logging and monitoring

Required event logs:

- preload requested
- ticket created
- receipt verified
- receipt declined
- account activated
- estimator allowed
- estimator blocked
- idempotent replay
- limit reached

Do not log:

- card numbers
- CVV/CVC
- full API tokens
- secrets

### 7. Test data cleanup

Before public launch:

- Mark internal QA accounts.
- Remove or archive test records.
- Confirm no test-only state is required for real users.

## Launch classification

Safe now:

- Internal QA.
- Controlled pilot.
- Trusted live demos.
- Supervised payment proof.

Not yet safe:

- Unrestricted public self-serve launch.
- Unknown users at scale.
- Multi-tenant customer base without authenticated backend identity and managed storage.

## Next engineering priority

Move from:

frontend-submitted email + local JSON

to:

backend-authenticated account_id + managed database.
