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

1. Backend-authenticated account identity.
2. Managed database/storage.
3. Route-level authorization.
4. Rate limiting and abuse protection.
5. Estimate-pack approved-payment proof.
6. Production logging and monitoring.
7. Test data cleanup.

## Next engineering priority

Move from:

frontend-submitted email + local JSON

to:

backend-authenticated account_id + managed database.
