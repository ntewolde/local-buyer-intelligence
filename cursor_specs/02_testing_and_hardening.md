# 02 — Testing & Hardening Add-On (PyTest + Security)

## Objective
Add **full-system testing** and final hardening so we can trust the whole app:
- API auth + tenant isolation tests
- CSV import tests (happy path + PII rejection)
- Celery tasks tests (eager mode)
- Census collector tests (mock external calls)
- Migration sanity test

Also improve:
- Global auth enforcement on routers
- PII guard enforced at multiple layers

---

# A) Required hardening
## A1. Global auth enforcement
All routers except `/auth/*` must require:
- `Depends(get_current_user)` at router include or per-endpoint

## A2. Tenant scoping
All queries must be scoped by `client_id` from current user (unless admin).

## A3. PII guard defense-in-depth
Ensure PII guard runs in:
1) CSV parsing
2) API write endpoints (POST/PUT/PATCH)
3) service layer before DB commit

---

# B) Add the following files exactly

Create directory:
`backend/tests/`

## B1) `backend/tests/conftest.py`
```python
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from app.models.client import Client

@pytest.fixture(scope="session", autouse=True)
def test_env():
    os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
    os.environ["SECRET_KEY"] = "test-secret"
    os.environ["CELERY_TASK_ALWAYS_EAGER"] = "true"
    os.environ["CELERY_TASK_EAGER_PROPAGATES"] = "true"

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture()
def db(engine):
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture()
def client(db):
    return TestClient(app)

@pytest.fixture()
def test_client_account(db):
    client = Client(name="Test Client")
    db.add(client)
    db.commit()
    db.refresh(client)
    return client

@pytest.fixture()
def admin_user(db):
    user = User(
        email="admin@test.com",
        hashed_password="hashed",
        role="admin",
        is_active=True
    )
    db.add(user)
    db.commit()
    return user

@pytest.fixture()
def client_user(db, test_client_account):
    user = User(
        email="client@test.com",
        hashed_password="hashed",
        role="client",
        client_id=test_client_account.id,
        is_active=True
    )
    db.add(user)
    db.commit()
    return user

@pytest.fixture()
def admin_token(admin_user):
    return create_access_token(subject=admin_user.email)

@pytest.fixture()
def client_token(client_user):
    return create_access_token(subject=client_user.email)
```

## B2) `backend/tests/test_authz.py`
```python
def test_requires_auth(client):
    res = client.get("/api/v1/geography")
    assert res.status_code == 401

def test_client_access_with_token(client, client_token):
    res = client.get(
        "/api/v1/geography",
        headers={"Authorization": f"Bearer {client_token}"}
    )
    assert res.status_code in (200, 404)
```

## B3) `backend/tests/test_imports_api.py`
```python
import io

def test_property_csv_import_rejects_pii(client, client_token):
    csv_data = "zip_code,email\n30043,test@test.com"
    res = client.post(
        "/api/v1/import/property",
        files={"file": ("bad.csv", io.BytesIO(csv_data.encode()), "text/csv")},
        headers={"Authorization": f"Bearer {client_token}"}
    )
    assert res.status_code == 400

def test_property_csv_import_accepts_valid(client, client_token):
    csv_data = "zip_code,property_type\n30043,SINGLE_FAMILY"
    res = client.post(
        "/api/v1/import/property",
        files={"file": ("good.csv", io.BytesIO(csv_data.encode()), "text/csv")},
        headers={"Authorization": f"Bearer {client_token}"}
    )
    assert res.status_code in (200, 202)
```

## B4) `backend/tests/test_tasks.py`
```python
from app.tasks import recompute_scores

def test_recompute_scores_task_runs():
    result = recompute_scores.delay("fake-geography-id", "fake-client-id")
    assert result.successful()
```

## B5) `backend/tests/test_census_collector.py`
```python
import responses
from app.collectors.census_collector import CensusCollector

@responses.activate
def test_census_collector_ingests_data():
    responses.add(
        responses.GET,
        "https://api.census.gov/data",
        json=[["NAME","B01003_001E"],["30043",1000]],
        status=200
    )
    collector = CensusCollector()
    data = collector.collect(["30043"])
    assert data is not None
```

## B6) `backend/tests/test_migrations.py`
```python
from alembic import command
from alembic.config import Config

def test_alembic_upgrade():
    cfg = Config("backend/alembic.ini")
    command.upgrade(cfg, "head")
```

---

# C) Add/Update Dev Dependencies
Add `backend/requirements-dev.txt` (or update pyproject/requirements) with:
- pytest
- pytest-cov
- responses
- httpx (optional)
- pytest-asyncio (if needed)

Ensure `pip install -r backend/requirements-dev.txt` works.

---

# D) Test Runner
Ensure this command works from repo root:
```bash
pytest -q --cov=app --cov-report=term-missing
```

---

# E) Acceptance Criteria
- All tests pass locally
- Endpoints require auth (401 without token)
- CSV PII is rejected
- Alembic upgrade head works in tests

---

# F) FINAL STEP: Commit & Push to GitHub
After implementing everything and tests pass:
1. `git status` is clean except new changes
2. Commit message:
`feat: full-system pytest coverage, auth enforcement, and PII hardening`
3. Push to GitHub (`git push`)
