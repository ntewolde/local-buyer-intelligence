"""
End-to-End API Tests
Tests the API structure and basic functionality
Uses existing fixtures from conftest.py
"""
import pytest


class TestAPIRoot:
    """Test root API endpoints"""

    def test_root_returns_api_info(self, client):
        """Root endpoint should return API information"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "Local Buyer Intelligence" in data["message"]

    def test_openapi_docs_available(self, client):
        """OpenAPI docs should be accessible"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_json_available(self, client):
        """OpenAPI JSON schema should be accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "paths" in data
        assert "info" in data


class TestAuthenticationEndpoints:
    """Test authentication endpoint behavior"""

    def test_login_endpoint_exists(self, client):
        """Login endpoint should exist and accept POST"""
        # Test with missing fields to verify endpoint exists
        response = client.post("/api/v1/auth/login", data={})
        # Should return 422 (validation error) not 404 (not found)
        assert response.status_code == 422

    def test_login_with_missing_password(self, client):
        """Login with missing password should return validation error"""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "test@email.com"}
        )
        # Should return 422 (validation error for missing field)
        assert response.status_code == 422

    def test_me_endpoint_requires_auth(self, client):
        """/me endpoint should require authentication"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_register_requires_admin(self, client):
        """Register endpoint should require authentication"""
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "new@test.com", "password": "pass123", "role": "client"}
        )
        assert response.status_code == 401


class TestProtectedEndpoints:
    """Test that protected endpoints require authentication"""

    def test_geography_list_requires_auth(self, client):
        """Geography list should require authentication"""
        response = client.get("/api/v1/geography/")
        assert response.status_code == 401

    def test_intelligence_reports_requires_auth(self, client):
        """Intelligence reports should require authentication"""
        response = client.get("/api/v1/intelligence/reports")
        assert response.status_code == 401

    def test_households_requires_auth(self, client):
        """Households endpoint should require authentication"""
        response = client.get("/api/v1/households/")
        assert response.status_code == 401


class TestAuthenticatedGeographyAccess:
    """Test geography endpoints with authentication"""

    def test_list_geographies_with_token(self, client, client_token):
        """Client user should be able to list geographies"""
        response = client.get(
            "/api/v1/geography/",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_geography_requires_valid_data(self, client, admin_token):
        """Geography creation should validate input"""
        response = client.post(
            "/api/v1/geography/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={}  # Empty/invalid data
        )
        # Should return 400 or 422 (validation error) not 500
        assert response.status_code in [400, 422]


class TestDataFreshnessEndpoint:
    """Test data freshness tracking"""

    def test_freshness_endpoint_requires_auth(self, client):
        """Freshness endpoint should require authentication"""
        response = client.get("/api/v1/freshness/geography/1/freshness")
        assert response.status_code == 401

    def test_freshness_endpoint_for_nonexistent_geo(self, client, client_token):
        """Freshness endpoint should handle non-existent geography"""
        response = client.get(
            "/api/v1/freshness/geography/99999/freshness",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        # Should return 404 (not found) not 500 (error)
        assert response.status_code in [200, 403, 404]


class TestIngestionRunsEndpoint:
    """Test ingestion runs endpoints"""

    def test_ingestion_runs_requires_auth(self, client):
        """Ingestion runs endpoint should require authentication"""
        response = client.get("/api/v1/ingestion-runs/")
        assert response.status_code == 401

    def test_ingestion_runs_with_auth(self, client, client_token):
        """Ingestion runs should be accessible with valid token"""
        response = client.get(
            "/api/v1/ingestion-runs/",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        assert response.status_code == 200
