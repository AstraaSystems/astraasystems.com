# Astraa Backend Enforcement Notes

These notes define how estimate limits should be enforced once Astraa moves from frontend/browser-session testing into production backend enforcement.

## Current Frontend Preview State

The current portal uses browser `sessionStorage` to track:

- selected tool
- selected plan
- selected price
- trial registration
- estimate usage
- daily trial estimate date
- saved estimates
- expenses
- local payment state

This is acceptable for:

- internal testing
- live soft-launch validation
- customer journey review
- visual and UX testing
- Moneris payment path testing

It is not production-grade enforcement.

Frontend/session enforcement can be bypassed by:

- clearing browser session storage
- using another browser
- using incognito/private mode
- using another device
- editing browser developer tools
- registering with another email unless backend prevents abuse

## Required Production Enforcement

Estimate limits must eventually be enforced by the backend, not only the browser.

The backend should enforce limits using:

- verified account ID
- verified primary email
- selected tool
- selected plan
- paid status
- payment confirmation status
- estimate count
- estimate period
- daily trial date
- account creation date
- trial start date
- subscription start date
- subscription renewal period
- custom package agreement, if applicable

## Estimate Limits by Plan

### Trial

Trial access should enforce:

- 15 total estimates
- 1 estimate per day
- 15-day trial window
- one primary account identity
- one verified business identity where possible
- launch bonus eligibility only if paid account matches or is verified

Backend rule:

```text
If plan is Trial:
  block if total estimates used >= 15
  block if estimate already used today
  block if trial period expired
```

### Basic

Basic access should enforce:

- 30 estimates per monthly billing period
- no daily cap unless abuse protection is added later
- paid status must be active
- selected tool and plan must match payment/subscription record

Backend rule:

```text
If plan is Basic:
  block if monthly estimates used >= 30
  block if payment/subscription is not active
```

### Professional

Professional access should enforce:

- 120 estimates per monthly billing period
- no daily cap unless abuse protection is added later
- paid status must be active
- selected tool and plan must match payment/subscription record

Backend rule:

```text
If plan is Professional:
  block if monthly estimates used >= 120
  block if payment/subscription is not active
```

### Custom / Franchise / Enterprise

Custom, Franchise, and Enterprise usage should be scoped by package agreement.

Backend rule:

```text
If plan is Custom, Franchise, or Enterprise:
  read estimate limit from customer contract/package settings
  enforce according to configured package limits
  support custom approval, reporting, and usage rules
```

## Recommended Estimate Limits

| Plan | Estimate Limit | Period | Daily Limit | Payment Required |
|---|---:|---|---:|---|
| Trial | 15 | 15-day trial | 1/day | No |
| Basic | 30 | Monthly billing period | None by default | Yes |
| Professional | 120 | Monthly billing period | None by default | Yes |
| Custom | Scoped | Agreement-based | Scoped | Yes |
| Franchise | Scoped | Agreement-based | Scoped | Yes |
| Enterprise | Scoped | Agreement-based | Scoped | Yes |

## Suggested Backend Data Model

A production backend should store customer account records similar to:

```json
{
  "account_id": "uuid",
  "primary_email": "customer@example.com",
  "backup_email": "backup@example.com",
  "business_name": "Example Business",
  "industry": "Construction / contracting",
  "selected_tool": "Astraa Estimator",
  "selected_plan": "Professional",
  "selected_price": "$99 CAD/month",
  "payment_status": "active",
  "subscription_status": "active",
  "trial_start_date": "YYYY-MM-DD",
  "subscription_start_date": "YYYY-MM-DD",
  "billing_period_start": "YYYY-MM-DD",
  "billing_period_end": "YYYY-MM-DD",
  "estimate_limit": 120,
  "estimate_used": 0,
  "last_trial_estimate_date": null,
  "custom_limit_config": null
}
```

## Suggested Estimate Request Flow

Production estimate requests should follow this flow:

```text
1. User selects Run Estimate in portal
2. Frontend sends estimate request to backend
3. Backend verifies account/session
4. Backend loads selected plan and payment status
5. Backend checks estimate usage limit
6. Backend checks daily trial limit if Trial
7. Backend either blocks or calculates estimate
8. Backend stores estimate record
9. Backend increments usage count
10. Backend returns updated usage summary to frontend
```

## Suggested API Endpoints

Recommended future backend endpoints:

```text
POST /api/register
POST /api/login
GET  /api/account
GET  /api/account/usage
POST /api/estimate
POST /api/expense
POST /api/payment/preload
POST /api/payment/webhook
GET  /api/payment/status
```

## Backend Estimate Enforcement Pseudocode

```python
def enforce_estimate_limit(account):
    plan = account.selected_plan

    if plan == "Trial":
        if account.trial_expired:
            return False, "Trial period expired."

        if account.estimate_used >= 15:
            return False, "Trial estimate limit reached."

        if account.last_trial_estimate_date == today():
            return False, "Daily trial estimate limit reached."

        return True, "Allowed"

    if plan == "Basic":
        if account.payment_status != "active":
            return False, "Payment is not active."

        if account.estimate_used >= 30:
            return False, "Basic monthly estimate limit reached."

        return True, "Allowed"

    if plan == "Professional":
        if account.payment_status != "active":
            return False, "Payment is not active."

        if account.estimate_used >= 120:
            return False, "Professional monthly estimate limit reached."

        return True, "Allowed"

    if plan in ["Custom", "Franchise", "Enterprise"]:
        if not account.custom_limit_config:
            return False, "Custom usage limit is not configured."

        if account.estimate_used >= account.custom_limit_config.estimate_limit:
            return False, "Custom estimate limit reached."

        return True, "Allowed"

    return False, "Unknown plan."
```

## Suggested Backend Estimate Endpoint Shape

Future `POST /api/estimate` should eventually work like this:

```python
@app.post("/api/estimate")
def create_estimate():
    user = require_authenticated_user()
    account = load_account(user.account_id)

    allowed, reason = enforce_estimate_limit(account)

    if not allowed:
        return {
            "success": False,
            "error": reason,
            "usage": get_usage_summary(account)
        }, 403

    estimate_result = run_estimate_logic(request.json)

    save_estimate(account.account_id, estimate_result)
    increment_estimate_usage(account.account_id)

    return {
        "success": True,
        "estimate": estimate_result,
        "usage": get_usage_summary(account)
    }
```

## Backend Usage Summary Response

Frontend portal should eventually receive usage from the backend in this shape:

```json
{
  "success": true,
  "usage": {
    "selected_plan": "Professional",
    "selected_tool": "Astraa Estimator",
    "estimate_limit": 120,
    "estimate_used": 18,
    "estimate_remaining": 102,
    "period_label": "Monthly",
    "billing_period_start": "YYYY-MM-DD",
    "billing_period_end": "YYYY-MM-DD",
    "daily_limit": null,
    "last_estimate_date": "YYYY-MM-DD",
    "payment_status": "active"
  }
}
```

## Moneris Payment Enforcement

Frontend payment success is not official payment proof.

Production backend should only mark paid access as active after one of these is verified:

- Moneris approved transaction response
- Moneris admin confirmation
- Moneris webhook/receipt validation if available
- backend payment status record updated after verification

Browser session keys such as:

```text
astraa_payment_complete
astraa_payment_receipt
astraa_paid_tool
astraa_paid_plan
astraa_paid_price
```

are useful for customer-facing display, but should not be treated as official payment truth.

Official payment proof, refunds, reconciliation, and accounting should be confirmed through Moneris merchant/admin records.

## Required Backend Tables Later

Recommended future tables or collections:

```text
accounts
subscriptions
payments
estimate_usage
estimates
expenses
custom_packages
audit_logs
```

## Abuse Protection Notes

Backend should eventually protect trials by checking:

- primary email
- backup email
- business name
- IP address
- device/session fingerprint if legally appropriate
- repeated payment email mismatch
- repeated trial creation attempts
- suspicious repeated estimate usage
- expired trial windows

## Launch Stage Recommendation

For soft launch:

- frontend session limits are acceptable for trusted testing
- live payment should be tested with a small amount
- every successful payment must be verified in Moneris admin
- wider public marketing should wait until backend account/payment enforcement is added

For production:

- backend must enforce all estimate limits
- backend must store account records
- backend must store estimate usage
- backend must verify paid status
- backend must prevent trial abuse
- backend must support custom package limits
