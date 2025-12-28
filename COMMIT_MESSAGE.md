# Commit Message for Refactoring

If you need a more detailed commit message, use:

```
Major refactoring: Add multi-tenancy, PII guardrails, auth, and real Census collector

Key changes:
- Added multi-tenancy: Client, User models with JWT auth and role-based access
- Implemented PII Guard module with comprehensive validation and tests
- Real Census API collector using ACS 5-year estimates
- Alembic migrations for all new models and multi-tenancy fields
- Authentication endpoints (login, register, me)
- Data freshness tracking per geography and source type
- Example CSV templates for property, events, and channels imports
- Updated all models with client_id scoping

See REFACTORING_STATUS.md for detailed implementation status.
```

