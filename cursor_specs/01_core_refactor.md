# 01 — Core Refactor Spec (Repo: local-buyer-intelligence-main)

Repo input: `/mnt/data/local-buyer-intelligence-main.zip` (unpack and apply changes in working tree)

## Goal
Refactor the repo from scaffold to a **working, compliance-locked** Local Buyer Intelligence platform that:
- **Never** scrapes/stores private-person PII
- Produces **non-empty, useful** intelligence reports for a given geography + service category
- Supports repeatable ingestion (Census API + CSV imports) with background refresh
- Is **multi-tenant** with basic auth and tenant isolation
- Adds observability (ingestion runs, freshness, structured logs) and export-ready deliverables

---

# 0) Hard Constraints (Non‑Negotiable)
1. No private-person PII in DB, API, collectors, imports, logs.
   Disallowed keys/fields anywhere: `email`, `phone`, `first_name`, `last_name`, `full_name`, `owner_name`, `address`, `street`, `apt`, `unit`, `ssn`, `dob`, social handles, etc.
2. No scraping behind logins; no CAPTCHA bypass; respect robots.txt/ToS. Scraping here is limited to public aggregate sources (Census) or user-provided CSV.
3. Geographic data must be aggregated (ZIP/census block group). Do not store precise household addresses.

---

# 1) Deliverables
## D1 — Real ingestion
- Implement a working **CensusCollector** using ACS 5-year estimates (US Census API)
- Add **CSV import** endpoints for:
  - Property characteristics (non-PII)
  - Events/signals (non-PII)
  - Channels (institutional/gatekeepers; non-PII)

## D2 — Compliance guardrails
- Add/enforce a PII guard module:
  - Validates collector payloads/import payloads
  - Validates write endpoints
  - Prevents PII keys in nested metadata
- Add unit tests that fail if PII keys appear

## D3 — Background refresh + freshness
- Implement Celery tasks for refresh/import/recompute/report generation
- Store and expose freshness timestamps per geography and source type

## D4 — Multi-tenant + auth (MVP)
- Models: `Client`, `User` (JWT auth)
- Role-based access: `admin`, `analyst`, `client`
- Scope all data by `client_id`

## D5 — Frontend improvements
- Geography selection + ZIP management UI
- Ingestion UI (upload CSV, run imports, view run status)
- Freshness indicator UI
- Report export (JSON/CSV)

---

# 2) Data Model Changes
## 2.1 New models
### Client
- `id (UUID)`, `name`, `created_at`

### User
- `id (UUID)`, `client_id (nullable for global admin)`, `email`, `hashed_password`, `role`, `is_active`, `created_at`

### IngestionRun
- `id`, `client_id`, `geography_id`, `source_type (census/csv_property/csv_events/csv_channels)`, `status (queued/running/success/failed)`, timestamps, `error_message`, `records_upserted`

### Channel (institutional)
- `id`, `client_id`, `geography_id`, `channel_type`, `name`, `city`, `state`, `zip_code?`, `estimated_reach?`, `website?`, `notes?`, `source_url?`, `created_at`
- **No personal contact fields**.

## 2.2 Add `client_id` to existing tables
Add `client_id` to: Geography, DemandSignal, IntelligenceReport, IngestionRun (if not already), Channel.

## 2.3 Household precision
If household rows exist, ensure:
- No addresses
- Prefer block group aggregates; jitter coordinates if stored

---

# 3) Alembic migrations (Must)
- Ensure `alembic/env.py` loads model metadata
- Create migration revisions in `backend/alembic/versions/`
- Acceptance: `alembic upgrade head` creates schema from scratch

---

# 4) Implement Real Collectors
## 4.1 CensusCollector
- Use ACS 5-year endpoints
- Inputs: ZIPs from Geography
- Fetch at least: population, households, median income, owner vs renter counts
- Store as DemandSignal (aggregate) with metadata and `source_url`
- Add retries/backoff for 429/5xx
- Update IngestionRun and freshness timestamps

## 4.2 EventCollector
- MVP: CSV import
- Optional: ICS feed parsing
- Store as DemandSignal with `signal_type=EVENT` and metadata

## 4.3 PropertyCollector
- MVP: CSV import for non-PII property characteristics

---

# 5) CSV Import Pipeline (MVP unlock)
## 5.1 Upload endpoint
- `POST /api/v1/uploads` -> stores file locally (dev) and returns `file_ref`

## 5.2 Import endpoints
- `POST /api/v1/import/property?geography_id=...&file_ref=...`
- `POST /api/v1/import/events?geography_id=...&file_ref=...`
- `POST /api/v1/import/channels?geography_id=...&file_ref=...`
Enqueue Celery jobs; return `ingestion_run_id`.

## 5.3 Strict CSV schemas
### Property (non-PII)
Required: `zip_code`
Optional: `property_type`, `ownership_type`, `lot_size_sqft`, `year_built`, `estimated_income_band`, `block_group`, `lat`, `lon` (jitter/aggregate)

### Events (non-PII)
Required: `event_name`, `start_date`
Optional: `end_date`, `zip_code`, `category`, `estimated_attendance`, `source_url`

### Channels (non-PII)
Required: `channel_type`, `name`
Optional: `zip_code`, `estimated_reach`, `website`, `source_url`, `notes`

Reject if any PII columns appear.

## 5.4 Upsert / dedupe rules
- Events upsert by (client_id, geography_id, event_name, start_date)
- Channels upsert by (client_id, geography_id, channel_type, name)
- Property: store as aggregates or upsert by key fields

---

# 6) PII Guardrails
Create/enhance `backend/app/core/pii_guard.py`:
- `assert_no_pii_keys(obj)` checks nested keys; normalizes case/underscores/spaces
- Enforce in:
  1) CSV import parsing
  2) API write endpoints
  3) Before DB commit in service layer
- Add unit tests

---

# 7) Background Jobs (Celery)
Create `backend/app/tasks.py` and implement:
- `refresh_census(ingestion_run_id)`
- `import_csv_property(ingestion_run_id, file_ref, geography_id, client_id)`
- `import_csv_events(...)`
- `import_csv_channels(...)`
- `recompute_scores(geography_id, client_id)`
- `generate_report(report_id, client_id)`

All tasks must update IngestionRun status and record counts.

---

# 8) Intelligence Engine improvements
Update `backend/app/services/intelligence_engine.py` to output deliverable-grade results:
- top ZIPs + “why”
- buyer profile summary (aggregate)
- recommended channels from Channel table
- timing window suggestion (events + seasonality rule set)
- export-friendly response schema

---

# 9) Auth + Multi-tenancy
- Implement JWT auth endpoints `/auth/login`, `/auth/me`
- Protect all routers except auth with dependencies
- Scope all data by client_id; admin can bypass if allowed

---

# 10) Frontend enhancements
Add pages:
- Geographies (create, edit ZIPs)
- Ingestion (upload/import, show status)
- Channels (CRUD/import)
- Reports (generate, view, export JSON/CSV)
Add freshness indicators.

---

# 11) Acceptance Criteria
- Migrations apply from scratch
- Census refresh creates non-empty signals
- CSV imports create non-empty records and reject PII columns
- Reports return non-empty recommendations
- All endpoints (except /auth) require auth
- Tenant isolation: client cannot access other clients data
