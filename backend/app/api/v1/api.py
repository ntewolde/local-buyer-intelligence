"""
API Router - Main API endpoint aggregation
Module gating (PHASE 2): Future work modules are conditionally included based on feature flags.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    geography, households, intelligence, demand_signals, auth,
    uploads, imports, channels, ingestion, freshness,
    channel_outreach, campaigns, lead_funnel, public_signals
)
from app.core.config import settings

api_router = APIRouter()

# Core modules (always enabled)
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(imports.router, prefix="/import", tags=["imports"])
api_router.include_router(channels.router, prefix="/channels", tags=["channels"])
api_router.include_router(ingestion.router, prefix="/ingestion-runs", tags=["ingestion"])
api_router.include_router(freshness.router, prefix="/freshness", tags=["freshness"])
api_router.include_router(geography.router, prefix="/geography", tags=["geography"])
api_router.include_router(households.router, prefix="/households", tags=["households"])
api_router.include_router(intelligence.router, prefix="/intelligence", tags=["intelligence"])
api_router.include_router(demand_signals.router, prefix="/demand-signals", tags=["demand-signals"])

# Future work modules (gated by feature flags - PHASE 2)
if settings.FEATURE_CHANNEL_CRM_ENABLED:
    api_router.include_router(channel_outreach.router, prefix="/channel-outreach", tags=["channel-outreach"])

if settings.FEATURE_CAMPAIGNS_ENABLED:
    api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])

if settings.FEATURE_LEAD_FUNNEL_ENABLED:
    api_router.include_router(lead_funnel.router, prefix="/lead-funnel", tags=["lead-funnel"])

if settings.FEATURE_PUBLIC_SIGNALS_ENABLED:
    api_router.include_router(public_signals.router, prefix="/public-signals", tags=["public-signals"])

