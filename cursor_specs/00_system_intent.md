# 00 — System Intent & Guardrails (Read First)

## Objective
Build and operate a **Local Buyer Intelligence & Lead Generation platform** that helps local businesses understand **where demand exists** and **how to reach it** in a defined geography (city/ZIP/neighborhood), across many service verticals (fireworks, lawn care, security, IT, etc.).

This system produces **actionable targeting and channel access**, plus (optionally) **opt-in lead capture**—without collecting or scraping private personal data.

## Non‑Negotiable Constraints
### Privacy / Compliance
- **Do not scrape or store private-person PII** (no resident emails/phones/names/addresses, no social profiles).
- Allowed data types:
  - **Aggregates**: ZIP/census-block-group demographics (Census), counts, distributions.
  - **Signals**: event counts/dates, seasonality, permit counts (public), housing turnover indicators (aggregate).
  - **Institutional channels**: HOAs, property managers, venues, schools, churches, local media (store org info + URLs; **no personal contacts**).
  - **Opt-in leads** only (if/when Option 2 is implemented): user provides consent via forms/SMS.

### Crawling / Data Collection
- No scraping behind logins; no CAPTCHA bypass; respect robots.txt and ToS.
- Prefer:
  - Official public APIs (e.g., Census ACS).
  - User-provided CSV imports for property/events/channels.

### Geographic Precision
- Do not store precise residential addresses.
- If any coordinates exist, keep them **aggregated** (ZIP/block group centroids) or jittered. Prefer block group IDs.

## Product Definition of Done
For a given `city/state` and a set of `ZIPs`, the system can generate:
- **Buyer insights** (aggregate demand profile by ZIP / neighborhood)
- **Recommended channels** (institutional/gatekeepers)
- **Timing recommendations** (event + seasonality window)
- Exportable, client-ready outputs (JSON/CSV; PDF optional later)

## Implementation Approach
Work in two stages:
1. **Core intelligence platform** (Option 1) + ingestion + compliance guardrails + auth + multi-tenancy.
2. Add modules for Options 2–5 (opt-in funnels, channel CRM, orchestration, etc.) later.
