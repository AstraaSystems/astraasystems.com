# Astraa Database Migration Plan

## Purpose

This document defines the future managed database model for Astraa public launch hardening.

Current local proof storage uses:

- astraa_data/astraa_usage_db.json
- astraa_data/astraa_payment_db.json
- astraa_data/astraa_sessions.json
- preloads.jsonl
- payments.jsonl

These files are acceptable for local QA and controlled proof, but public production should use managed, transactional storage.

## Migration principle

Do not migrate all local test data into production.

Local runtime data should be classified first:

- KEEP_AS_PROOF
- ARCHIVE_LATER
- DO_NOT_MIGRATE
- MANUAL_REVIEW

The archive/export scripts preserve current runtime data before any cleanup or migration.

## Core production tables

### accounts

Purpose:

- Stable account identity.
- Source of truth for customer/user account.

Suggested fields:

- account_id
- primary_email
- display_name
- business_name
- account_type
- status
- created_at
- updated_at

### tenants

Purpose:

- Multi-tenant organization boundary.

Suggested fields:

- tenant_id
- account_id
- organization_name
- tenant_type
- status
- created_at
- updated_at

### sessions

Purpose:

- Backend-authenticated identity/session tracking.

Suggested fields:

- session_id
- account_id
- tenant_id
- token_hash
- identity_source
- expires_at
- created_at
- revoked_at

Security note:

- Store token hash, not raw token.

### subscriptions

Purpose:

- Source of truth for plan access.

Suggested fields:

- subscription_id
- account_id
- tenant_id
- selected_tool
- selected_plan
- payment_status
- subscription_status
- billing_period_key
- billing_period_start
- billing_period_end
- estimate_limit
- created_at
- updated_at

### payments

Purpose:

- Payment-level transaction summary.

Suggested fields:

- payment_id
- account_id
- tenant_id
- selected_tool
- selected_plan
- purchase_type
- payment_gateway
- environment
- idempotency_key
- ticket_reference
- verified
- receipt_request_ok
- receipt_approved
- verification_source
- verification_reason
- verified_at
- created_at

Constraints:

- idempotency_key should be unique.
- ticket_reference + account_id + purchase_type should be protected from duplicate application.

### payment_events

Purpose:

- Append-only audit trail for payment lifecycle.

Suggested fields:

- event_id
- payment_id
- account_id
- tenant_id
- event_type
- event_status
- event_reason
- safe_gateway_reference
- created_at

Example event types:

- preload_requested
- ticket_created
- receipt_verification_requested
- receipt_approved
- receipt_declined
- idempotent_replay
- usage_activation_applied
- usage_activation_blocked

### preload_events

Purpose:

- Record checkout preload attempts without storing sensitive payment data.

Suggested fields:

- preload_id
- account_id
- tenant_id
- order_no
- selected_tool
- selected_plan
- amount
- environment
- status
- ticket_reference
- gateway_success
- gateway_error
- created_at

### usage_counters

Purpose:

- Tool usage limits and counters.

Suggested fields:

- usage_id
- account_id
- tenant_id
- selected_tool
- selected_plan
- billing_period_key
- estimate_limit
- estimate_used
- extra_estimate_credits_total
- extra_estimate_credits_used
- last_trial_estimate_date
- created_at
- updated_at

Constraints:

- account_id + selected_tool + billing_period_key should be unique.

### estimate_runs

Purpose:

- Store estimate execution history.

Suggested fields:

- estimate_run_id
- account_id
- tenant_id
- selected_tool
- billing_period_key
- base_cost
- complexity_factor
- material_multiplier
- labor_multiplier
- location_multiplier
- estimated_total
- source
- created_at

### audit_events

Purpose:

- Security and operational audit trail.

Suggested fields:

- audit_event_id
- account_id
- tenant_id
- event_type
- route
- identity_source
- decision
- reason
- ip_reference
- user_agent_reference
- created_at

Example events:

- account_authority_blocked
- account_authority_token_allowed
- estimator_allowed
- estimator_blocked
- payment_verification_blocked
- payment_verification_allowed
- rate_limit_blocked
- request_size_blocked
- schema_validation_blocked

## Do not store

Astraa should not store:

- card numbers
- CVV/CVC
- full magnetic stripe/chip data
- PIN/PIN block
- Moneris API token
- raw secrets

## Migration phases

### Phase 1 — Design

- Finalize schema.
- Confirm IDs and relationships.
- Confirm which local records are KEEP_AS_PROOF vs DO_NOT_MIGRATE.

### Phase 2 — Adapter layer

- Add storage abstraction functions.
- Keep JSON backend as default.
- Prepare DB backend behind environment flag.

### Phase 3 — Managed DB staging

- Create database tables.
- Run migration dry-run into staging DB.
- Validate counts and relationships.

### Phase 4 — Dual-read / controlled write

- Keep JSON as fallback.
- Write new records to DB in staging.
- Compare DB vs JSON behavior.

### Phase 5 — Production cutover

- Use DB as source of truth.
- Keep local JSON only for local development.
- Archive final JSON snapshot.

## Current recommendation

Do not perform DB migration yet.

Next engineering task:

- Add storage abstraction layer while JSON remains the active backend.
