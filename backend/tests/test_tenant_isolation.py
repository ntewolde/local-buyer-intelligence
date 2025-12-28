"""
Tenant Isolation Proof Tests (Phase 1.1)
Ensures Client A cannot access Client B's resources
"""
import pytest
from app.models import Client, User, UserRole, Geography
from app.core.security import create_access_token
import uuid


@pytest.fixture()
def client_a(db):
    """Create Client A"""
    client = Client(name="Client A")
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@pytest.fixture()
def client_b(db):
    """Create Client B"""
    client = Client(name="Client B")
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@pytest.fixture()
def user_a(db, client_a):
    """Create User A for Client A"""
    user = User(
        email="usera@test.com",
        hashed_password="hashed",
        role=UserRole.CLIENT,
        client_id=client_a.id,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def user_b(db, client_b):
    """Create User B for Client B"""
    user = User(
        email="userb@test.com",
        hashed_password="hashed",
        role=UserRole.CLIENT,
        client_id=client_b.id,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def token_a(user_a):
    """Token for User A"""
    token_data = {
        "sub": str(user_a.id),
        "email": user_a.email,
        "role": user_a.role.value
    }
    if user_a.client_id:
        token_data["client_id"] = str(user_a.client_id)
    return create_access_token(data=token_data)


@pytest.fixture()
def token_b(user_b):
    """Token for User B"""
    token_data = {
        "sub": str(user_b.id),
        "email": user_b.email,
        "role": user_b.role.value
    }
    if user_b.client_id:
        token_data["client_id"] = str(user_b.client_id)
    return create_access_token(data=token_data)


@pytest.fixture()
def geography_a(db, client_a):
    """Create Geography for Client A"""
    geography = Geography(
        name="Client A Geography",
        client_id=client_a.id,
        type="CITY",
        state_code="GA"
    )
    db.add(geography)
    db.commit()
    db.refresh(geography)
    return geography


def test_client_b_cannot_access_client_a_geography(client, token_b, geography_a):
    """Test that User B (Client B) cannot access Geography owned by Client A"""
    # User B attempts to fetch Client A's geography
    res = client.get(
        f"/api/v1/geography/{geography_a.id}",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    # Should return 403 (Forbidden) or 404 (Not Found) - both are acceptable
    assert res.status_code in (403, 404), f"Expected 403/404, got {res.status_code}: {res.text}"


def test_client_a_can_access_own_geography(client, token_a, geography_a):
    """Test that User A (Client A) can access their own geography"""
    res = client.get(
        f"/api/v1/geography/{geography_a.id}",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    assert res.json()["id"] == geography_a.id
    assert res.json()["client_id"] == str(geography_a.client_id)

