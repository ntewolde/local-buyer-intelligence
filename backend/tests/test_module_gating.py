"""
Module Gating Tests (PHASE 2)
Verifies that future work modules are properly gated by feature flags.
"""
import pytest
from app.core.config import settings
from app.api.v1.api import api_router


def test_future_work_modules_disabled_by_default():
    """Test that future work modules are disabled by default"""
    assert settings.FEATURE_LEAD_FUNNEL_ENABLED is False
    assert settings.FEATURE_PUBLIC_SIGNALS_ENABLED is False
    assert settings.FEATURE_CHANNEL_CRM_ENABLED is False
    assert settings.FEATURE_CAMPAIGNS_ENABLED is False


def test_core_modules_always_enabled(client, client_token):
    """Test that core modules are always accessible"""
    # Core endpoints should work regardless of feature flags
    res = client.get("/api/v1/geography/", headers={"Authorization": f"Bearer {client_token}"})
    # Should not be 404 (might be 200, 401, or 403 depending on auth, but not 404 from gating)
    assert res.status_code != 404, "Core geography endpoint should not be gated"


def test_gated_endpoints_return_404_when_disabled(client, client_token):
    """Test that gated endpoints return 404 when feature flags are disabled"""
    # These endpoints should not exist when feature flags are disabled
    # We check by looking at the router paths
    routes = [route.path for route in api_router.routes]
    
    # When disabled, these paths should not be in the router
    if not settings.FEATURE_CHANNEL_CRM_ENABLED:
        assert "/channel-outreach" not in str(routes)
    
    if not settings.FEATURE_CAMPAIGNS_ENABLED:
        assert "/campaigns" not in str(routes)
    
    if not settings.FEATURE_LEAD_FUNNEL_ENABLED:
        assert "/lead-funnel" not in str(routes)
    
    if not settings.FEATURE_PUBLIC_SIGNALS_ENABLED:
        assert "/public-signals" not in str(routes)


def test_feature_flag_dependency_raises_404():
    """Test that feature flag dependency raises 404 when disabled"""
    from app.core.feature_flags import require_feature_flag
    from fastapi import HTTPException
    
    with pytest.raises(HTTPException) as exc_info:
        require_feature_flag("test_feature", False)
    
    assert exc_info.value.status_code == 404
    assert "not enabled" in exc_info.value.detail.lower()


def test_feature_flag_dependency_allows_when_enabled():
    """Test that feature flag dependency allows when enabled"""
    from app.core.feature_flags import require_feature_flag
    
    # Should not raise when enabled
    try:
        require_feature_flag("test_feature", True)
    except Exception as e:
        pytest.fail(f"Feature flag dependency should not raise when enabled, but raised: {e}")

