"""
Upload Auth Regression Tests (Phase 1.1)
Ensures uploads endpoint requires authentication
"""
import io
import pytest


def test_uploads_requires_auth(client):
    """Test that POST /api/v1/uploads without token returns 401"""
    csv_data = "zip_code,property_type\n30043,SINGLE_FAMILY"
    res = client.post(
        "/api/v1/uploads",
        files={"file": ("test.csv", io.BytesIO(csv_data.encode()), "text/csv")}
    )
    assert res.status_code == 401, f"Expected 401, got {res.status_code}: {res.text}"


def test_uploads_with_token(client, client_token):
    """Test that POST /api/v1/uploads with client token succeeds"""
    csv_data = "zip_code,property_type\n30043,SINGLE_FAMILY"
    res = client.post(
        "/api/v1/uploads",
        files={"file": ("test.csv", io.BytesIO(csv_data.encode()), "text/csv")},
        headers={"Authorization": f"Bearer {client_token}"}
    )
    assert res.status_code in (200, 202), f"Expected 200/202, got {res.status_code}: {res.text}"
    assert "file_ref" in res.json(), "Response should contain file_ref"

