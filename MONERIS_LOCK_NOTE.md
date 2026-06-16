# Moneris Payment Flow Lock

Moneris payment flow is considered working and protected as of 2026-06-16.

Do not edit these files without creating a fresh Moneris backup first:

- payment.html
- payment-success.html
- pricing.html
- login.html
- register.html
- frontend/payment.html
- frontend/payment-success.html
- frontend/pricing.html
- frontend/login.html
- frontend/register.html

Working snapshot:
SAFE_SNAPSHOTS/moneris/moneris_working_snapshot_20260616_144609.tar.gz

Rules:
- Do not change Moneris checkout ticket logic.
- Do not change payment success receipt/sessionStorage logic.
- Do not change selected tool/plan/price handoff unless intentionally testing payment flow.
- Do not replace ngrok/backend payment URL until backend deployment is confirmed.
- Confirm official payments in Moneris admin.
