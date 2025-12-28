"""
Feature Flags - Module Gating (PHASE 2)
Controls which future work modules are enabled at runtime.
"""
from fastapi import HTTPException, status
from app.core.config import settings


def require_feature_flag(flag_name: str, enabled: bool):
    """
    Dependency to require a feature flag to be enabled.
    Raises 404 if the feature is disabled.
    """
    if not enabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature '{flag_name}' is not enabled"
        )


# Feature flag checks for future work modules
def require_lead_funnel():
    """Require lead funnel (Option 2) to be enabled"""
    return require_feature_flag("lead_funnel", settings.FEATURE_LEAD_FUNNEL_ENABLED)


def require_public_signals():
    """Require public signals (Option 3) to be enabled"""
    return require_feature_flag("public_signals", settings.FEATURE_PUBLIC_SIGNALS_ENABLED)


def require_channel_crm():
    """Require channel CRM (Option 4) to be enabled"""
    return require_feature_flag("channel_crm", settings.FEATURE_CHANNEL_CRM_ENABLED)


def require_campaigns():
    """Require campaigns (Option 5) to be enabled"""
    return require_feature_flag("campaigns", settings.FEATURE_CAMPAIGNS_ENABLED)

