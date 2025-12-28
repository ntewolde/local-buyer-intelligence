# MVP Contract — Local Buyer Intelligence Platform

**Version**: 1.0  
**Date**: 2024-01-02  
**Status**: Locked for MVP Release

---

## Purpose

This document defines the **MVP (Minimum Viable Product) contract** for the Local Buyer Intelligence Platform. It establishes what is **included** in the MVP, what is **excluded** (future work), and the **non-negotiable constraints** that govern the platform.

---

## MVP Scope (What IS Included)

### Core Intelligence Platform (Module 1)

The MVP includes the following capabilities:

1. **Geographic Data Management**
   - Create and manage geographies (cities, counties, states)
   - Manage ZIP codes and neighborhoods within geographies
   - Track data freshness per geography and source type

2. **Data Ingestion**
   - **Census Data**: Automated refresh via US Census API (ACS 5-year estimates)
   - **CSV Imports**: Upload and process CSV files for:
     - Property characteristics (non-PII)
     - Events/signals (public event calendars)
     - Channels (institutional/gatekeeper data)
   - Background processing via Celery tasks
   - Ingestion run tracking and status

3. **Intelligence Reports**
   - Generate buyer intelligence reports for a geography + service category
   - ZIP-level demand scoring with rationale
   - Buyer profile summaries (aggregated, non-PII)
   - Channel recommendations
   - Timing recommendations
   - Export reports as JSON or CSV

4. **Multi-Tenancy & Authentication**
   - Client-based data isolation
   - JWT-based authentication
   - Role-based access control (admin, analyst, client)
   - Tenant-scoped queries

5. **PII Compliance & Guardrails**
   - PII Guard module validates all imports and API writes
   - CSV header validation
   - Nested metadata validation
   - No personal identifiers stored or processed

6. **Data Freshness Tracking**
   - Timestamps for census, property, events, and channels data
   - Freshness indicators in UI

---

## Excluded from MVP (Future Work)

The following modules are **NOT part of the MVP** and are gated by feature flags:

1. **Lead Funnel & Opt-In Capture Builder** (Option 2)
   - Landing pages per city + service
   - Consent capture (email/SMS)
   - CRM pipeline
   - **Status**: Gated by `FEATURE_LEAD_FUNNEL_ENABLED` (default: disabled)

2. **Public Signals Ingestion** (Option 3)
   - ICS calendar parsing
   - Additional public data feeds
   - **Status**: Gated by `FEATURE_PUBLIC_SIGNALS_ENABLED` (default: disabled)

3. **Institutional Channel CRM** (Option 4)
   - Channel outreach tracking
   - Contact status management
   - **Status**: Gated by `FEATURE_CHANNEL_CRM_ENABLED` (default: disabled)

4. **Campaign Orchestrator** (Option 5)
   - Campaign planning
   - Asset generation
   - Budget allocation
   - **Status**: Gated by `FEATURE_CAMPAIGNS_ENABLED` (default: disabled)

**Note**: These modules are implemented but disabled by default. They require explicit feature flag enablement and are subject to stabilization and compliance review before activation.

---

## Non-Negotiable Constraints

### Privacy & Compliance

1. **No Private-Person PII**
   - Do NOT scrape or store personal emails, phones, names, addresses, or social profiles
   - Only aggregated/geographic data is allowed
   - PII Guard enforces this at multiple layers (imports, API, service layer)
   
   **Explicit Forbidden Keys** (case-insensitive, normalized):
   - **Contact Information**: `email`, `e-mail`, `e_mail`, `email_address`, `phone`, `phone_number`, `telephone`, `mobile`, `cell`, `cell_phone`
   - **Personal Names**: `firstname`, `first_name`, `fname`, `lastname`, `last_name`, `lname`, `surname`, `full_name`, `owner`, `owner_name`, `property_owner`, `homeowner_name`
   - **Addresses**: `address`, `street`, `street_address`, `street_address_line_1`, `apt`, `apartment`, `unit`, `unit_number`, `suite`
   - **Identity Documents**: `ssn`, `social_security_number`, `social_security`, `dob`, `date_of_birth`, `birthday`, `birth_date`, `driver_license`, `drivers_license`, `dl_number`, `passport`, `passport_number`
   - **Social Media**: `facebook`, `facebook_id`, `facebook_url`, `instagram`, `instagram_id`, `instagram_url`, `linkedin`, `linkedin_id`, `linkedin_url`, `twitter`, `twitter_id`, `twitter_url`, `twitter_handle`, `tiktok`, `tiktok_id`, `tiktok_url`
   
   **Note**: The keys `name` and `fullname` (without underscore) are **allowed** as they are required for organizations and institutions. Only personal identifiers (as listed above) are forbidden.

2. **Data Sources**
   - Official public APIs (e.g., Census ACS)
   - User-provided CSV imports
   - Public event calendars (ICS feeds when enabled)
   - **No scraping behind logins, no CAPTCHA bypass, respect robots.txt**

3. **Geographic Precision**
   - No precise residential addresses
   - Data aggregated at ZIP/census block group level
   - Coordinates jittered or aggregated if stored

### Technical Constraints

1. **Multi-Tenancy**
   - All data scoped by `client_id`
   - Complete isolation between clients
   - Admin users can access all clients

2. **Authentication**
   - All API endpoints (except `/auth/*`) require authentication
   - JWT tokens with role-based access
   - Client-scoped queries enforced

3. **Data Processing**
   - Background jobs via Celery
   - Async processing for all imports
   - Ingestion run tracking for observability

---

## MVP Deliverables

### Functional Deliverables

1. **Working Intelligence Reports**
   - Generate reports for any geography + service category
   - Export as JSON or CSV
   - Include demand scores, buyer profiles, channel recommendations

2. **Data Ingestion Pipeline**
   - Census data refresh (automated)
   - CSV import for property, events, channels
   - Background processing with status tracking

3. **Multi-Tenant Platform**
   - Client isolation
   - User management
   - Role-based access

### Non-Functional Deliverables

1. **PII Compliance**
   - PII Guard tests passing
   - No PII in database, API, or logs
   - Compliance validation at import time

2. **Test Coverage**
   - API authorization tests
   - Tenant isolation tests
   - PII guard tests
   - CSV import tests
   - Module gating tests

3. **Documentation**
   - API documentation (OpenAPI/Swagger)
   - Setup guide
   - CSV import schemas
   - This MVP contract

---

## Feature Flag Policy

Future work modules are controlled via feature flags in `app.core.config`:

- `FEATURE_LEAD_FUNNEL_ENABLED` (default: `False`)
- `FEATURE_PUBLIC_SIGNALS_ENABLED` (default: `False`)
- `FEATURE_CHANNEL_CRM_ENABLED` (default: `False`)
- `FEATURE_CAMPAIGNS_ENABLED` (default: `False`)

**Policy**: These flags must remain `False` for MVP release. Activation requires:
1. Stabilization review
2. Compliance review
3. Explicit enablement via environment variable

---

## Acceptance Criteria

The MVP is considered complete when:

1. ✅ All core features (listed above) are functional
2. ✅ All tests pass (29+ tests)
3. ✅ PII Guard correctly allows organizational names, rejects personal PII
4. ✅ Uploads endpoint requires authentication
5. ✅ Tenant isolation verified
6. ✅ Future work modules gated and disabled by default
7. ✅ Documentation complete (this contract, API docs, setup guide)

---

## Change Control

This MVP contract is **locked** for the MVP release. Changes to scope require:
1. Stakeholder approval
2. Update to this document
3. Re-evaluation of test coverage
4. Compliance review

---

## References

- System Intent: `cursor_specs/00_system_intent.md`
- Core Refactor Spec: `cursor_specs/01_core_refactor.md`
- Testing & Hardening: `cursor_specs/02_testing_and_hardening.md`
- Stabilization Spec: `cursor_specs/03_stabilization_and_mvp_lockdown.md`
- Future Work: `cursor_specs/99_future_work.md`

