"""
API Router - Main API endpoint aggregation
"""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    geography, households, intelligence, demand_signals, auth,
    uploads, imports, channels, ingestion, freshness
)

api_router = APIRouter()

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

