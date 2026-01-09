import os
import pytest

# Set environment variables BEFORE any imports that use settings (CRITICAL: Phase 1.1)
# Use setdefault to ensure deterministic initialization order
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("CELERY_TASK_ALWAYS_EAGER", "true")
os.environ.setdefault("CELERY_TASK_EAGER_PROPAGATES", "true")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
# Note: Spec says app.db.base but we use app.core.database
from app.core.config import settings
from app.core.security import create_access_token
from passlib.context import CryptContext

# Import all models to ensure all tables are created in Base.metadata
# This must happen before creating the engine
import app.models.client
import app.models.geography
import app.models.household
import app.models.demand_signal
import app.models.intelligence_report
import app.models.ingestion
import app.models.channel

# Now import the models for use in tests
from app.models import (
    User, Client, UserRole,
    Geography, ZIPCode, Neighborhood,
    Household,
    DemandSignal,
    IntelligenceReport,
    IngestionRun,
    Channel
)

from app.main import app

# Use a simple password context for tests (no bcrypt required)
test_pwd_context = CryptContext(schemes=["plaintext"], deprecated="auto")

def get_test_password_hash(password: str) -> str:
    """Simple password hash for tests"""
    return test_pwd_context.hash(password)
from app.core.database import SessionLocal

@pytest.fixture(scope="session", autouse=True)
def test_env():
    # Environment already set above
    pass

@pytest.fixture(scope="session")
def engine():
    # Use in-memory SQLite for tests, or PostgreSQL if DATABASE_URL is set
    test_db_url = os.environ.get("DATABASE_URL", "sqlite+pysqlite:///:memory:")

    # check_same_thread is only valid for SQLite
    if "sqlite" in test_db_url:
        engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(test_db_url)

    Base.metadata.create_all(engine)
    return engine

@pytest.fixture()
def db(engine):
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    # Clear tables before each test to ensure isolation
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture()
def client(db):
    # Override get_db dependency
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides = {}
    from app.core.database import get_db
    app.dependency_overrides[get_db] = override_get_db
    
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
        hashed_password=get_test_password_hash("testpassword"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture()
def client_user(db, test_client_account):
    user = User(
        email="client@test.com",
        hashed_password=get_test_password_hash("testpassword"),
        role=UserRole.CLIENT,
        client_id=test_client_account.id,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture()
def admin_token(admin_user):
    return create_access_token(data={"sub": str(admin_user.id), "email": admin_user.email, "role": admin_user.role.value})

@pytest.fixture()
def client_token(client_user):
    token_data = {
        "sub": str(client_user.id),
        "email": client_user.email,
        "role": client_user.role.value
    }
    if client_user.client_id:
        token_data["client_id"] = str(client_user.client_id)
    return create_access_token(data=token_data)

