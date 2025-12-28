"""
API Router - Main API endpoint aggregation
"""
from fastapi import APIRouter
from app.api.v1.endpoints import geography, households, intelligence, demand_signals

api_router = APIRouter()

api_router.include_router(geography.router, prefix="/geography", tags=["geography"])
api_router.include_router(households.router, prefix="/households", tags=["households"])
api_router.include_router(intelligence.router, prefix="/intelligence", tags=["intelligence"])
api_router.include_router(demand_signals.router, prefix="/demand-signals", tags=["demand-signals"])

